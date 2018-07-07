import libtcodpy as libtcod
import settings
import message
from component import *
import random

def move(obj, dx, dy):
    #moves object by (dx, dy)
    #returns true if move succeeded
    if not is_blocked(obj.x + dx, obj.y + dy):
        obj.x += dx
        obj.y += dy

def move_towards(obj, target_x, target_y):
    #dx = target_x - self.x
    #dy = target_y - self.y
    #distance = math.sqrt(dx ** 2 + dy ** 2)

    #dx = int(round(dx / distance))
    #dy = int(round(dy / distance))
    #self.move(dx, dy)
    #vector from this object to the target, and distance
    dx = target_x - obj.x
    dy = target_y - obj.y
 
    mx = 0
    my = 0

    #get the direction of the vector
    #print(target_x, self.x, mx, target_y, self.y, my)
    if dx > 0:
        mx = 1
    elif dx < 0:
        mx = -1
    if dy > 0:
        my = 1
    elif dy < 0:
        my = -1
 
    #try diagonal first
    if not is_blocked(obj.x + mx, obj.y + my):
        obj.x += mx
        obj.y += my
    else:
        if abs(dx) > abs(dy):
            if not is_blocked(obj.x + mx, obj.y):
                obj.x += mx
            elif not is_blocked(obj.x, obj.y+my):
                obj.y += my
        else:
            if not is_blocked(obj.x, obj.y+my):
                obj.y += my
            elif not is_blocked(obj.x + mx, obj.y):
                obj.x += mx

def move_away(obj, target_x, target_y):
    #vector from this object to the target, and distance

    dx = target_x - obj.x
    dy = target_y - obj.y
    dx = -dx
    dy = -dy

    mx = 0
    my = 0

    #get the direction of the vector
    #print(target_x, self.x, mx, target_y, self.y, my)
    if dx > 0:
        mx = 1
    elif dx < 0:
        mx = -1
    if dy > 0:
        my = 1
    elif dy < 0:
        my = -1
 
    #try diagonal first
    if not is_blocked(obj.x + mx, obj.y + my):
        obj.x += mx
        obj.y += my
    else:
        if abs(dx) > abs(dy):
            if not is_blocked(obj.x + mx, obj.y):
                obj.x += mx
            elif not is_blocked(obj.x, obj.y+my):
                obj.y += my
        else:
            if not is_blocked(obj.x, obj.y+my):
                obj.y += my
            elif not is_blocked(obj.x + mx, obj.y):
                obj.x += mx


def move_astar(obj, target):
    #Create a FOV map that has the dimensions of the map
    fov = libtcod.map_new(settings.MAP_WIDTH, settings.MAP_HEIGHT)
 
    #Scan the current map each turn and set all the walls as unwalkable
    for y1 in range(settings.MAP_HEIGHT):
        for x1 in range(settings.MAP_WIDTH):
            libtcod.map_set_properties(fov, x1, y1, not settings.map[x1][y1].block_sight, not settings.map[x1][y1].blocked)
 
    #Scan all the objects to see if there are objects that must be navigated around
    #Check also that the object isn't self or the target (so that the start and the end points are free)
    #The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
    for eachobj in settings.objects:
        if eachobj.blocks and eachobj != obj and eachobj != target:
            #Set the tile as a wall so it must be navigated around
            libtcod.map_set_properties(fov, eachobj.x, eachobj.y, True, False)

    #Allocate a A* path
    #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
    my_path = libtcod.path_new_using_map(fov, 1.41)

    #Compute the path between self's coordinates and the target's coordinates
    libtcod.path_compute(my_path, obj.x, obj.y, target.x, target.y)
 
    #Check if the path exists, and in this case, also the path is shorter than 25 tiles
    #The path size matters if you want the monster to use alternative longer paths 
    #(for example through other rooms) if for example the player is in a corridor
    #It makes sense to keep path size relatively low to keep the monsters from running 
    #around the map if there's an alternative path really far away        
    if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
        #Find the next coordinates in the computed full path
        x, y = libtcod.path_walk(my_path, True)
        if x or y:
            #Set self's coordinates to the next path tile
            obj.x = x
            obj.y = y
    else:
        #Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
        #it will still try to move towards the player (closer to the corridor opening)
        move_towards(obj, target.x, target.y)

    #delete the path to free memory
    libtcod.path_delete(my_path)

def move_towards_n(obj, target):
    for x in range(obj.speed_value):
        if obj.distance_to(target) > 1.5: #1.5 because of diagonals
            move_astar(obj, target)

def heal(obj, amount):
    obj.hp += amount
    if obj.hp > obj.max_hp:
        obj.hp = obj.max_hp

def attack(fighter, target):
    #a formula for attack damage
    #attacker to-hit roll:
    to_hit_roll = random.randint(1, 6) + fighter.reflex
    #defender evasion roll:
    evasion_roll = random.randint(1, 6) + target.fighter.reflex
    #damage roll:
    damage_roll = random.randint(1, 6) + fighter.strength
    #defense roll:
    defense_roll = random.randint(1, 6) + target.fighter.defense
    #damage:
    damage = damage_roll - defense_roll

    if to_hit_roll > evasion_roll: #attack will hit
        if damage_roll > defense_roll:
            #make the target take some damage
            message.message(fighter.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            inflict_damage(fighter.owner, target.fighter, damage)
        else:
            message.message(fighter.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    elif to_hit_roll == evasion_roll: #attack has 50% chance of hitting
        if libtcod.random_get_int(0, 0, 1) == 1:
            if damage_roll >  defense_roll:
                #make the target take some damage
                message.message(fighter.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                inflict_damage(fighter.owner, target.fighter, damage)
            else:
                message.message(fighter.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
        else:
            message.message(fighter.owner.name.capitalize() + ' missed!')
 
    else: #attack misses
        message.message(fighter.owner.name.capitalize() + ' missed!')

def inflict_damage(actor, fighter, damage):
    if damage > 0:
        fighter.hp -= damage
        if fighter.hp <= 0:
            function = fighter.death_function
            if function is not None:
                function(fighter.owner)
            if fighter.owner != settings.player:
                settings.player.fighter.xp += fighter.xp

def is_blocked(x, y):
    if settings.map[x][y].blocked:
        return True
    
    for object in settings.objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    
    return False
        




def get_equipped_in_slot(slot):
    for obj in settings.inventory:
        if (obj.equipment and obj.equipment.slot == slot and
                obj.equipment.is_equipped):
            return obj.equipment


