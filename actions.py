"""
Implementation of actions.
Includes those which might be used by the AI (movement and combat)
and those which are currently only offered to the player.
Magical effects and targeting (spells.py) could also live here.
Conditionals and interfaces for the player sit up top in roguelike.py.
"""
import libtcodpy as libtcod
import copy

import log
import algebra
import config
import map
from components import *



def move(o, direction):
    """
    Moves object by (dx, dy).
    Returns true if move succeeded.
    """
    goal = o.pos + direction
    if not o.current_map.is_blocked_at(goal):
        o.pos = goal
        return True
    return False


def move_towards(o, target_pos):
    """
    Moves object one step towards target location.
    Returns true if move succeeded.
    """
    dir = algebra.Direction(target_pos.x - o.x, target_pos.y - o.y)
    dir.normalize()
    return move(o, dir)

def move_away(o, target_pos):
    """
    moves object away from target
    """
    dir = algebra.Direction(target_pos.x + o.x, target_pos.y + o.y)
    dir.normalize()
    return move(o, dir)

def move_astar(o, target_pos):
    """
    Moves object towards target with A*
    """
    #create a FOV map with dimensions of the map
    fov=libtcod.map_new(config.MAP_WIDTH, config.MAP_HEIGHT)
    #scan the current map and set all walls as unwalkable
    for y in range(config.MAP_HEIGHT):
        for x in range(config.MAP_WIDTH):
            libtcod.map_set_properties(fov, x, y, 
                                       not map.terrain_types[o.current_map.terrain[o.pos.x][o.pos.y]].blocks_sight,
                                       not map.terrain_types[o.current_map.terrain[o.pos.x][o.pos.y]].blocks)

    #Scan all the objects to see if there are objects that must be navigated around
    #Check also that the object isn't self or the target (so that the start and the end points are free)
    #The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
    for object in o.current_map.objects:
        if object.blocks and object != o and object != target_pos:
            #Set the tile as a wall so it must be navigated around
            libtcod.map_set_properties(fov, object.x, object.y, True, False)

    #Allocate a A* path
    #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
    my_path = libtcod.path_new_using_map(fov, 1.41)

    #compute path between self and target position
    libtcod.path_compute(my_path, o.pos.x, o.pos.y, target_pos.x, target_pos.y)

    #Check if the path exists, and in this case, also the path is shorter than 25 tiles
    if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
        #Find the next coordinates in the computed full path
        x, y = libtcod.path_walk(my_path, True)
        if x or y:
            #Set self's coordinates to the next path tile
            o.x = x
            o.y = y
    else:
        #Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
        #it will still try to move towards the player (closer to the corridor opening)
        move_towards(o, target_pos)

def attack(fighter, target, report=True):
    """
    A simple formula for attack damage.
    """
    hit = (fighter.reflex + fighter.weapon_skill) - (target.fighter.reflex + target.fighter.weapon_skill)
    damage = fighter.strength - target.fighter.defense

    if hit > 0: #attack will hit
        if damage > 0:
            if report:
                log.message(
                    fighter.owner.name.capitalize() + ' attacks ' + target.name +
                    ' for ' + str(damage) + ' hit points.')
            inflict_damage(fighter.owner, target.fighter, damage)
        elif report:
            log.message(
                fighter.owner.name.capitalize() + ' attacks ' + target.name +
                ' but it has no effect!')
    elif hit == 0: #attack has 50% chance of hitting
        if libtcod.random_get_int(0, 0, 1) == 1:
            if damage > 0:
                if report:
                    log.message(
                        fighter.owner.name.capitalize() + ' attacks ' + target.name +
                        ' for ' + str(damage) + ' hit points.')
                inflict_damage(fighter.owner, target.fighter, damage)
            elif report:
                log.message(
                    fighter.owner.name.capitalize() + ' attacks ' + target.name +
                    ' but it has no effect')
        else:
            log.message(
                fighter.owner.name.capitalize() + ' missed!')
    elif hit < 0: #attack has 25% chance of hitting
        if libtcod.random_get_int(0, 1, 4) == 4:
            if damage > 0:
                if report:
                    log.message(
                        fighter.owner.name.capitalize() + ' attacks ' + target.name +
                        ' for ' + str(damage) + ' hit points.')
                inflict_damage(fighter.owner, target.fighter, damage)
            elif report:
                log.message(
                    fighter.owner.name.capitalize() + ' attacks ' + target.name +
                    ' but it had no effect')
        else:
            log.message(
                fighter.owner.name.capitalize() + ' missed!')

def ranged_attack(fighter, tardet, report=True):
    pass


def inflict_damage(actor, fighter, damage):
    """
    Apply damage.
    """
    if damage > 0:
        fighter.hp -= damage

        if fighter.hp <= 0:
            function = fighter.death_function
            if function is not None:
                function(fighter.owner)

            actor.fighter.xp += fighter.xp


def heal(fighter, amount):
    """
    Heal by the given amount, without going over the maximum.
    """
    fighter.hp += amount
    if fighter.hp > fighter.max_hp:
        fighter.hp = fighter.max_hp


def pick_up(actor, o, report=True):
    """
    Add an Object to the actor's inventory and remove from the map.
    """
    for p in actor.inventory:
        if o.item.can_combine(p):
            p.item.count += o.item.count
            actor.current_map.objects.remove(o)
            if report:
                log.message(actor.name.capitalize() + ' picked up a ' + o.name + '!', libtcod.green)
            return True

    if len(actor.inventory) >= 22:
        if report:
            log.message(actor.name.capitalize() + ' inventory is full, cannot pick up ' +
                        o.name + '.', libtcod.red)
        return False
    else:
        actor.inventory.append(o)
        actor.current_map.objects.remove(o)
        if report:
            log.message(actor.name.capitalize() + ' picked up a ' + o.name + '!', libtcod.green)

        # Special case: automatically equip if the corresponding equipment slot is unused.
        equipment = o.equipment
        if equipment and _get_equipped_in_slot(actor, equipment.slot) is None:
            equip(actor, equipment)
        return True


def drop(actor, o, report=True):
    """
    Remove an Object from the actor's inventory and add it to the map
    at the player's coordinates.
    If it's equipment, dequip before dropping.
    """
    must_split = False
    if o.item.count > 1:
        o.item.count -= 1
        must_split = True
    else:
        if o.equipment:
            dequip(actor, o.equipment, True)
        actor.inventory.remove(o)

    combined = False
    for p in actor.current_map.objects:
        if p.pos == actor.pos and o.item.can_combine(p):
            p.item.count += 1
            combined = True
            break

    if not combined:
        new_o = o
        if must_split:
            new_o = copy.deepcopy(o)
        new_o.item.count = 1
        new_o.pos = actor.pos
        actor.current_map.objects.append(new_o)

    if report:
        log.message(actor.name.capitalize() + ' dropped a ' + o.name + '.', libtcod.yellow)


def use(actor, o, report=True):
    """
    If the object has the Equipment component, toggle equip/dequip.
    Otherwise invoke its use_function and (if not cancelled) destroy it.
    """
    if o.equipment:
        _toggle_equip(actor, o.equipment, report)
        return

    if o.item.use_function is None:
        if report:
            log.message('The ' + o.name + ' cannot be used.')
    else:
        if o.item.use_function(actor) != 'cancelled':
            if o.item.count > 1:
                o.item.count -= 1
            else:
                actor.inventory.remove(o)


def _toggle_equip(actor, eqp, report=True):
    if eqp.is_equipped:
        dequip(actor, eqp, report)
    else:
        equip(actor, eqp, report)


def equip(actor, eqp, report=True):
    """
    Equip the object (and log unless report=False).
    Ensure only one object per slot.
    """
    old_equipment = _get_equipped_in_slot(actor, eqp.slot)
    if old_equipment is not None:
        dequip(actor, old_equipment, report)

    eqp.is_equipped = True
    if report:
        log.message('Equipped ' + eqp.owner.name + ' on ' + eqp.slot + '.', libtcod.light_green)


def dequip(actor, eqp, report=True):
    """
    Dequip the object (and log).
    """
    if not eqp.is_equipped:
        return
    eqp.is_equipped = False
    if report:
        log.message('Dequipped ' + eqp.owner.name + ' from ' + eqp.slot + '.', libtcod.light_yellow)


def _get_equipped_in_slot(actor, slot):
    """
    Returns Equipment in a slot, or None.
    """
    if hasattr(actor, 'inventory'):
        for obj in actor.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
    return None


class _MockMap(object):
    def is_blocked_at(self, pos):
        return False


def _test_move():
    o = Object(algebra.Location(0, 0), 'o', 'test object', libtcod.white)
    o.current_map = _MockMap()
    assert o.pos == algebra.Location(0, 0)
    move(o, algebra.south)
    assert o.pos == algebra.Location(0, 1)
    move(o, algebra.southeast)
    assert o.pos == algebra.Location(1, 2)


def _test_move_towards():
    o = Object(algebra.Location(0, 0), 'o', 'test object', libtcod.white)
    o.current_map = _MockMap()
    assert o.pos == algebra.Location(0, 0)
    move_towards(o, algebra.Location(10, 10))
    assert o.pos == algebra.Location(1, 1)
    move_towards(o, algebra.Location(10, 10))
    assert o.pos == algebra.Location(2, 2)
    move_towards(o, algebra.Location(-10, 2))
    assert o.pos == algebra.Location(1, 2)
    move_towards(o, o.pos)
    assert o.pos == algebra.Location(1, 2)


def _test_attack():
    af = Fighter(100, 0, 10, 0)
    df = Fighter(100, 0, 0, 0)
    a = Object(algebra.Location(0, 0), 'a', 'test attacker', libtcod.white, fighter=af)
    d = Object(algebra.Location(1, 1), 'd', 'test defender', libtcod.white, fighter=df)

    assert af.hp == 100
    assert df.hp == 100
    # if defense == 0, full damage is done
    attack(af, d, False)
    assert df.hp == 90
    df.base_defense = 5
    attack(af, d, False)
    assert df.hp == 85
    # if defense > attack, no damage is done
    df.base_defense = 15
    attack(af, d, False)
    assert df.hp == 85


def _test_actions():
    _test_move()
    _test_move_towards()
    _test_attack()


if __name__ == '__main__':
    _test_actions()
    print('Action tests complete.')