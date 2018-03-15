import handle_keys
import settings
import color
from Equipment import Equipment
from map_gen import make_map
from Fighter import Fighter
import message
from GameObject import GameObject
#from Equipment import MeleeWeapon
#import actions
#import character_creation




def new_game():
    message.message_init()
    fighter_component = Fighter(hp=100, defense=100, strength=100, reflex=100, regen_rate=1, regen_amount=1, movesSinceLastHit=0,
                                xp=0, wound_counter=0, death_function=player_death)
    settings.player = GameObject(0, 0, '@', 'player', color.white, blocks=True,
                                 fighter=fighter_component)

    settings.player.level = 1
    settings.dungeon_level = 1
    make_map()
    give_name()
    handle_keys.initialize_fov()
    settings.game_state = 'playing'
    settings.inventory = []
    #settings.game_msgs = []


    message.message('Welcome stranger to the the eternal,' 
                    'twisted and slimy realm of noodles. ', color.red)
    equipment_component = Equipment(slot='right hand', strength_bonus=2)
    obj = GameObject(0, 0, '-', 'dagger', color.sky,
                     equipment=equipment_component)
    settings.inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True

def give_name():
    player_name = raw_input('enter name: ')
    settings.player.name = player_name

def player_death(player):
    message.message('you died.')
    settings.game_state = 'dead'
    settings.player.char = '%'
    settings.player.color = color.dark_red