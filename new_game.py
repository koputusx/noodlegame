import libtcodpy as libtcod
import handle_keys
import settings
import color
from Equipment import Equipment
from map_gen import make_map
from Fighter import Fighter
import message
from GameObject import GameObject
#from Equipment import MeleeWeapon
import actions
#import character_creation




def new_game():
    message.message_init()
    fighter_component = Fighter(hp=999, defense=999, strength=999, reflex=999, regen_rate=1, regen_amount=1, #movesSinceLastHit=0,
                                xp=0, wound_counter=0, death_function=player_death)
    settings.player = GameObject(0, 0, '@', 'player', color.white, blocks=True,
                                 fighter=fighter_component)

    settings.player.inventory = []
    settings.player.level = 1
    settings.dungeon_level = 1
    #settings.game_state = 'naming'
    #give_name()
    make_map()
    handle_keys.initialize_fov()
    settings.game_state = 'playing'
    #settings.inventory = []
    #settings.game_msgs = []


    message.message('Welcome stranger to the the eternal,' 
                    'twisted and slimy realm of noodles. ', color.red)
    equipment_component = Equipment(slot='right hand', strength_bonus=2)
    obj = GameObject(0, 0, '-', 'dagger', color.sky,
                     equipment=equipment_component)
    settings.player.inventory.append(obj)
    actions.equip(settings.player, obj.equipment)
    obj.always_visible = True

# def give_name():
    # #settings.game_state = 'naming'
    # #player_name_string = ''
    # #settings.player.name = player_name_string
    # #while settings.game_state = 'naming':

    # #player_name = raw_input('enter name: ')
    # img = libtcod.image_load('menu_background.png')
    # #while settings.game_state == 'start_up':
    # libtcod.image_blit_2x(img, 0, 0, 0)

    # libtcod. console_set_default_foreground(0, color.light_yellow)
    # libtcod.console_print_ex(0, settings.SCREEN_WIDTH / 2,
                             # settings.SCREEN_HEIGHT / 2 - 4,
                             # libtcod.BKGND_NONE, libtcod.CENTER,
                             # 'Character creation')
    # handle_keys.handle_keys()
    # settings.player.name = handle_keys.player_name
    # settings.game_state = 'playing'

def player_death(player):
    message.message('you died.')
    settings.game_state = 'dead'
    settings.player.char = '%'
    settings.player.color = color.dark_red