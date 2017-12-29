import libtcodpy as libtcod
import color
from GameObject import GameObject
from Tile import Tile
from rng import rng

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map portion shown on-screen
CAMERA_WIDTH = 80
CAMERA_HEIGHT = 40

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 80
 
#sizes and coordinates relevant for the GUI
BAR_WIDTH = 30
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
#MSG_LIMIT = 150
 
#parameters for dungeon generator
ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 4
MAX_ROOMS = 60

#constants for bsp
DEPTH = 5
MIN_SIZE = 10
FULL_ROOMS = False

#for hp regeneration
#HP_REGEN_TIME = 100
 
#spell values
HEAL_AMOUNT = 40
GREATHEAL_AMOUNT = 80
LIGHTNING_DAMAGE = 30
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
#CONFUSE_NUM_TURNS = 10
PARALYZE_RANGE = 8
#PARALYZE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25
MAGICMISSILE_DAMAGE = 40
MAGICMISSILE_RANGE = 10
 
#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
 
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 15
 
LIMIT_FPS = 20  #20 frames-per-second maximum

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

dungeon_level = 1
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
fov_recompute = True
game_msgs = []
game_state = 'start_up'
inventory = []
key = libtcod.Key()
map = [[Tile(True) for y in range(MAP_HEIGHT)]
       for x in range(MAP_WIDTH)]
flood_map = [[-1 for y in range(MAP_HEIGHT)]
             for x in range(MAP_WIDTH)]
mouse = libtcod.Mouse
objects =[]
player = GameObject(0, 0, '@', 'player', color.white)
stairs = GameObject(0, 0, '<', 'stairs', color.white)

RNG = rng()

def init():
    libtcod.console_set_custom_font('terminal12x12_gs_ro.png',
                                    libtcod.FONT_TYPE_GREYSCALE |
                                    libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                              'basicroguelike', False)
    libtcod.console_credits()
    libtcod.sys_set_fps(LIMIT_FPS)