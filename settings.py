from builtins import range
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
MSG_LIMIT = 150

#parameters for dungeon generator
ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 4
MAX_ROOMS = 60

#parameters for room addition
SQUARE_ROOM_MAX_SIZE = 12
SQUARE_ROOM_MIN_SIZE = 6
CROSS_ROOM_MAX_SIZE = 12
CROSS_ROOM_MIN_SIZE = 6
CAVERN_CHANCE = 0.40 # probability that the first room will be a cavern
CAVERN_MAX_SIZE = 35 # max height an width
WALL_PROBABILITY = 0.45
NEIGHBORS = 4
SQUARE_ROOM_CHANCE = 0.2
CROSS_ROOM_CHANCE = 0.15
BUILD_ROOM_ATTEMPTS = 500
PLACE_ROOM_ATTEMPTS = 20
MAX_TUNNEL_LENGTH = 12
INCLUDE_SHORTCUTS = True
SHORTCUT_ATTEMPTS = 500
SHORTCUT_LENGTH = 5
MIN_PATHFINDING_DISTANCE = 50

#constants for bsp
DEPTH = 5
MIN_SIZE = 10
FULL_ROOMS = False

#for hp regeneration
HP_REGEN_TIME = 100

#spell values
HEAL_AMOUNT = 40
GREATHEAL_AMOUNT = 80
LIGHTNING_DAMAGE = 30
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
SLEEP_RANGE = 8
#CONFUSE_NUM_TURNS = 10
PARALYZE_RANGE = 8
#PARALYZE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25
FROSTBOLT_DAMAGE = 20
FROSTBOLT_RANGE = 5
ACIDBALL_DAMAGE = 35
ACIDBALL_RADIUS = 5
MAGICMISSILE_RANGE = 10
EXPLOSION_DAMAGE = 5

#experience and level-ups
LEVEL_UP_BASE = 200000
LEVEL_UP_FACTOR = 1500

TURN_COUNT = 0

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 15

LIMIT_FPS = 20  #20 frames-per-second maximum

#main console window for drawing the map and object
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
#buffer overlaid over the main console window for effects, labels and other such stuff
overlay = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
#UI text data
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

dungeon_level = 1
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
fov_recompute = True
game_state = 'start_up'
#inventory = []
key = libtcod.Key()
map = [[Tile(True) for y in range(MAP_HEIGHT)]
for x in range(MAP_WIDTH)]
flood_map = [[-1 for y in range(MAP_HEIGHT)]
for x in range(MAP_WIDTH)]
mouse = libtcod.Mouse()
(camera_x, camera_y) = (0, 0)
objects =[]
player = GameObject(0, 0, '@', 'player', color.white)
stairs = GameObject(0, 0, '<', 'stairs', color.white)
delicious_cup_of_noodles = GameObject(0, 0, '&', 'delicious cup of noodles', color.yellow)

RNG = rng()

def init():
    libtcod.console_set_custom_font('terminal12x12_gs_ro.png',
                                    libtcod.FONT_TYPE_GREYSCALE |
                                    libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                              'Noodle game', False)
    #libtcod.console_credits()
    libtcod.sys_set_fps(LIMIT_FPS)