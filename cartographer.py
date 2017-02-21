import libtcodpy as libtcod

import config
import algebra
import map
from components import *
import ai
import spells
import miscellany

ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 4
MAX_ROOMS = 60


def _random_position_in_room(room):
    return algebra.Location(libtcod.random_get_int(0, room.x1+1, room.x2-1),
                            libtcod.random_get_int(0, room.y1+1, room.y2-1))


def _create_room(new_map, room):
    """
    Make the tiles in a rectangle passable
    """
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            new_map.terrain[x][y] = 1


def _create_h_tunnel(new_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        new_map.terrain[x][y] = 1


def _create_v_tunnel(new_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        new_map.terrain[x][y] = 1


def _random_choice_index(chances):
    """
    choose one option from list of chances, returning its index
    """
    dice = libtcod.random_get_int(0, 1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if dice <= running_sum:
            return choice
        choice += 1


def _random_choice(chances_dict):
    """
    choose one option from dictionary of chances, returning its key
    """
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[_random_choice_index(chances)]


def _from_dungeon_level(new_map, table):
    # Returns a value that depends on level.
    # The table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if new_map.dungeon_level >= level:
            return value
    return 0


loot_values = {
    'heal' : miscellany.healing_potion,
    'lightning' : miscellany.lightning_scroll,
    'fireball' : miscellany.fireball_scroll,
    'confuse' : miscellany.confusion_scroll,
    'paralyze' : miscellany.paralyzation_scroll,
    'sword' : miscellany.sword,
    'shield' : miscellany.shield
}

def _place_objects(new_map, room, player):
    max_monsters = _from_dungeon_level(new_map, [[2, 1], [3, 4], [5, 6]])

    monster_chances = {}
    # rats always shows up, even if all other monsters have 0 chance.
    monster_chances['orc'] = _from_dungeon_level(new_map, [[60, 2], [70, 3], [80, 4]])
    monster_chances['troll'] = _from_dungeon_level(new_map, [[15, 5], [30, 7], [60, 9]])
    monster_chances['hideous one'] = _from_dungeon_level(new_map, [[20, 4], [40, 6], [70, 8]])
    monster_chances['ettin'] = _from_dungeon_level(new_map, [[15, 6], [30, 8], [60, 10]])
    monster_chances['melted one'] = _from_dungeon_level(new_map, [[15, 5], [30, 7], [60, 10]])
    monster_chances['goblin'] = 20
    monster_chances['giant rat'] = 60
    monster_chances['flayed one'] = _from_dungeon_level(new_map, [[15, 8], [30, 10], [60, 11]])
    monster_chances['goblin archer'] = 20
    
    max_items = _from_dungeon_level(new_map, [[1, 1], [2, 4]])

    item_chances = {}
    # Healing potion always shows up, even if all other items have 0 chance.
    item_chances['heal'] = 35
    item_chances['lightning'] = _from_dungeon_level(new_map, [[25, 4]])
    item_chances['fireball'] = _from_dungeon_level(new_map, [[25, 6]])
    item_chances['confuse'] = _from_dungeon_level(new_map, [[10, 2]])
    item_chances['paralyze'] = 50
    item_chances['sword'] = _from_dungeon_level(new_map, [[5, 4]])
    item_chances['shield'] = _from_dungeon_level(new_map, [[15, 8]])

    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    for i in range(num_monsters):
        pos = _random_position_in_room(room)

        if not new_map.is_blocked_at(pos):
            choice = _random_choice(monster_chances)
            if choice == 'orc':
                fighter_component = Fighter(hp=15, defense=1, strength=5, reflex=3, weapon_skill=0, shield_skill=0, speed_value=6, xp=40, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'o', 'orc', libtcod.desaturated_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'troll':
                fighter_component = Fighter(hp=20, defense=2, strength=8, reflex=3, weapon_skill=0, shield_skill=0, speed_value=6, xp=105, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'T', 'troll', libtcod.darker_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'hideous one':
                fighter_component = Fighter(hp=15, defense=1, strength=6, reflex=4, weapon_skill=0, shield_skill=0, speed_value=6, xp=55, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'h', 'hideous one', libtcod.darker_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'ettin':
                fighter_component = Fighter(hp=30, defense=3, strength=9, reflex=5, weapon_skill=0, shield_skill=0, speed_value=6, xp=155, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'E', 'Ettin', libtcod.pink,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'melted one':
                fighter_component = Fighter(hp=40, defense=4, strength=8, reflex=0, weapon_skill=0, shield_skill=0, speed_value=6, xp=150, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'X', 'Melted one', lighter_red,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'goblin':
                fighter_component = Fighter(hp=10, defense=1, strength=3, reflex=2, weapon_skill=1, shield_skill=0, speed_value=6, xp=20, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'g', 'goblin', libtcod.light_blue,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'giant rat':
                fighter_component = Fighter(hp=5, defense=0, strength=1, reflex=1, weapon_skill=0, shield_skill=0, speed_value=6, xp=25, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'r', 'rat', libtcod.light_grey,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'flayed one':
                fighter_component = Fighter(hp=40, defense=6, strength=10, reflex=5, weapon_skill=0, shield_skill=0, speed_value=6, xp=160, death_function=ai.monster_death)
                ai_component = AI(ai.basic_monster, ai.basic_monster_metadata(player))
                monster = Object(pos, 'f', 'flayed one', libtcod.light_purple,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'goblin archer':
                fighter_component = Fighter(hp=10, defense=1, strength=3, reflex=2, weapon_skill=0, shield_skill=0, speed_value=0, xp=20, death_function=ai.monster_death)
                ai_component = AI(ai.coward_monster, ai.coward_monster_metadata(player))
                monster = Object(pos, 'g', 'goblin archer', libtcod.green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)


            new_map.objects.append(monster)
            monster.current_map = new_map

    num_items = libtcod.random_get_int(0, 0, max_items)
    for i in range(num_items):
        pos = _random_position_in_room(room)

        if not new_map.is_blocked_at(pos):
            choice = _random_choice(item_chances)
            item = loot_values[choice](pos=pos)

            new_map.objects.insert(0, item)
            item.always_visible = True  # Items are visible even out-of-FOV, if in an explored area


def _build_map(new_map):
    new_map.rng = libtcod.random_new_from_seed(new_map.random_seed)
    num_rooms = 0
    for r in range(MAX_ROOMS):
        w = libtcod.random_get_int(new_map.rng, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(new_map.rng, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = libtcod.random_get_int(new_map.rng, 0, new_map.width - w - 1)
        y = libtcod.random_get_int(new_map.rng, 0, new_map.height - h - 1)

        new_room = map.Room(x, y, w, h)

        failed = False
        for other_room in new_map.rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # There are no intersections, so this room is valid.
            _create_room(new_map, new_room)
            new_ctr = new_room.center()

            if num_rooms > 0:
                prev_ctr = new_map.rooms[num_rooms-1].center()

                if libtcod.random_get_int(new_map.rng, 0, 1) == 1:
                    _create_h_tunnel(new_map, prev_ctr.x, new_ctr.x, prev_ctr.y)
                    _create_v_tunnel(new_map, prev_ctr.y, new_ctr.y, new_ctr.x)
                else:
                    _create_v_tunnel(new_map, prev_ctr.y, new_ctr.y, prev_ctr.x)
                    _create_h_tunnel(new_map, prev_ctr.x, new_ctr.x, new_ctr.y)

            new_map.rooms.append(new_room)
            num_rooms += 1

    # Create stairs at the center of the last room.
    stairs = Object(new_ctr, '<', 'stairs down', libtcod.white, always_visible=True)
    stairs.destination = None
    stairs.dest_position = None
    new_map.objects.insert(0, stairs)
    new_map.portals.insert(0, stairs)

    # Test - tunnel off the right edge
    # _create_h_tunnel(new_map, new_ctr.x, new_map.width-1, new_ctr.y)


def make_map(player, dungeon_level):
    """
    Creates a new simple map at the given dungeon level.
    Sets player.current_map to the new map, and adds the player as the first
    object.
    """
    new_map = map.Map(config.MAP_HEIGHT, config.MAP_WIDTH, dungeon_level)
    new_map.objects.append(player)
    player.current_map = new_map
    player.camera_position = algebra.Location(0, 0)
    new_map.random_seed = libtcod.random_save(0)
    _build_map(new_map)
    for new_room in new_map.rooms:
        _place_objects(new_map, new_room, player)
    player.pos = new_map.rooms[0].center()

    new_map.initialize_fov()
    return new_map


def _test_map_repeatability():
    """
    Require that two calls to _build_map() with the same seed produce the
    same corridors and rooms.
    """
    map1 = map.Map(config.MAP_HEIGHT, config.MAP_WIDTH, 3)
    map1.random_seed = libtcod.random_save(0)
    _build_map(map1)

    map2 = map.Map(config.MAP_HEIGHT, config.MAP_WIDTH, 3)
    map2.random_seed = map1.random_seed
    _build_map(map2)

    assert map1.terrain == map2.terrain
    for i in range(len(map1.rooms)):
        assert map1.rooms[i] == map2.rooms[i]

if __name__ == '__main__':
    _test_map_repeatability()
    print('Cartographer tests complete.')