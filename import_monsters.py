from __future__ import print_function
import color
import glob
from Deaths import Death_type
from Fighter import Fighter
from GameObject import GameObject
from AI import AI_type


def import_monsters():
    monsters = {}
    monster = []
    packs = {}
    processing = False
    direct_read = False
    part = ''
    for filename in glob.glob('Monsters/*.txt'):
        textfile = open(filename, 'r')
        if textfile.read(8) == 'MONSTERS':
            for c in textfile.read():
                if c == '{' and not processing:
                    monster = []
                    processing = True
                if processing:
                    if c == '\\' and not direct_read:
                        direct_read = True
                    elif direct_read:
                        part = part + c
                        direct_read = False
                    elif c == '[':
                        part = ''
                    elif c == ']':
                        monster.append(part)
                    elif c == '}':
                        finishedmonster = make_monster(monster)
                        packsize = check_if_pack(monster)
                        if packsize:
                            packs[finishedmonster.name] = packsize
                        monsters[finishedmonster.name] = finishedmonster
                        processing = False
                    else:
                        part = part + c
    return monsters, packs


def make_monster(parts):
    name = 'default'
    char = '@'
    colour = 'white'
    _speed = 0
    blocking = False
    fighter_component = None
    ai_component = None
    placement_range_component = None
    for p in parts:
        if p.startswith('name'):
            name = p.split('=', 1)[1]
        elif p.startswith('char'):
            char = p[-1:]
        elif p.startswith('color'):
            colour = p.split('=', 1)[1]
        elif p.startswith('speed'):
            _speed = p.split('=', 1)[1]
        elif p == 'blocks':
            blocking = True
        elif p.startswith('fighter'):
            piece = ''
            pieces = []
            for c in p:
                if c == '<':
                    piece = ''
                elif c == '>':
                    pieces.append(piece)
                else:
                    piece = piece + c

            fighter_component = make_fighter(pieces)
        elif p.startswith('ai'):
            ai_component = p.split('=', 1)[1]
        elif p.startswith('placement'):
            piece = ''
            pieces = []
            for c in p:
                if c == '<':
                    piece = ''
                elif c == '>':
                    pieces.append(piece)
                else:
                    piece = piece + c

            placement_range_component = make_placement_range(pieces)

    return GameObject(0, 0, char, name, getattr(color, colour), speed_value=int(_speed),
                  blocks=blocking, fighter=fighter_component,
                  ai=AI_type[ai_component](),
                  placement_range=placement_range_component)


def make_fighter(pieces):
    _hp = 0
    _defense = 0
    _strength = 0
    _reflex = 0
    _regen_rate = 0
    _regen_amount = 0
    #_movesSinceLastHit = 0
    _move_probability = 0
    _attack_number = 0
    _xp = 0
    _wound_counter = 0
    death_component = 'basic_death'
    for p in pieces:
        if p.startswith('hp'):
            _hp = p.split('=', 1)[1]
        elif p.startswith('def'):
            _defense = p.split('=', 1)[1]
        elif p.startswith('str'):
            _strength = p.split('=', 1)[1]
        elif p.startswith('ref'):
            _reflex = p.split('=', 1)[1]
        elif p.startswith('regr'):
            _regen_rate = p.split('=', 1)[1]
        elif p.startswith('rega'):
            _regen_amount = p.split('=', 1)[1]
        #elif p.startswith('mslh'):
            #_movesSinceLastHit = p.split('=', 1)[1]
        elif p.startswith('mprb'):
            _move_probability = p.split('=', 1)[1]
        elif p.startswith('an'):
            _attack_number = p.split('=', 1)[1]
        elif p.startswith('xp'):
            _xp = p.split('=', 1)[1]
        elif p.startswith('wcount'):
            _wound_counter = p.split('=', 1)[1]
        elif p.startswith('death'):
            death_component = p.split('=', 1)[1]

    return Fighter(hp=int(_hp), defense=int(_defense),
                   strength=int(_strength), reflex=int(_reflex), regen_rate=int(_regen_rate),
                   regen_amount=int(_regen_amount), #movesSinceLastHit=int(_movesSinceLastHit),
                   xp=int(_xp), wound_counter=int(_wound_counter), move_probability=int(_move_probability),
                   attack_number=int(_attack_number), death_function=Death_type[death_component])


def make_placement_range(pieces):
    placement_range_component = []
    for p in pieces:
        s = p.split(':')
        placement_range_component.append([int(s[1]), int(s[0])])

    return placement_range_component


def check_if_pack(parts):
    for p in parts:
        if p.startswith('pack'):
            s = p.split('=')[1].split(':')
            i = [int(s[0]), int(s[1])]
            return i

    return False


(monsters, packs) = import_monsters()


if __name__ == '__main__':
    monsterlist = import_monsters()
    for key in monsterlist:
        print(key)