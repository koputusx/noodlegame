from __future__ import division
from builtins import str
from builtins import range
from past.utils import old_div
import tcod as libtcod
import time

import settings
import color
import message
import Rect

# frame_index = 0
# twenty_frame_estimate = 1000
# last_frame_time = None

# con = None #main console window for drawing map and objects

# overlay = None #buffer overlaid over the main console window  for effects, labels, and other metadata

# panel = None # UI text data

# console_center = Rect.Location(settings.MAP_WIDTH / 2,
                               # settings.MAP_HEIGHT / 2)

# def block_for_key():
    # #Approximately replacing libtcod.console_wait_for_keypress(),
    # #returns a libtcod.Key object.
    # key = libtcod.Key()
    # mouse = libtcod.Mouse()
    # while True:
        # libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
        # if (key.vk == libtcod.KEY_NONE):
            # continue

        # if (key.vk == libtcod.KEY_ALT or
                # key.vk == libtcod.KEY_SHIFT or
                # key.vk == libtcod.KEY_CONTROL):
            # continue

        # break
    # return key

# class ScreenCoords(tuple):
    # @staticmethod
    # def fromWorldCoords(camera_coords, world_coords):
        # #Returns (None, None) if the specified world coordinates would be off-screen.
        # x = world_coords.x - camera_coords.x
        # y = world_coords.y - camera_coords.y
        # if (x < 0 or y < 0 or x >= settings.MAP_WIDTH or y >= settings.MAP_HEIGHT):
            # return ScreenCoords((None, None))
        # return ScreenCoords((x, y))

    # @staticmethod
    # def toWorldCoords(camera_coords, screen_coords):
        # x = screen_coords[0] + camera_coords.x
        # y = screen_coords[1] + camera_coords.y
        # return Rect.Location(x, y)

# def renderer_init():
    # #Initialize libtcod and set up basic consoles to draw into
    # global con, panel, overlay, last_frame_time
    # libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    # libtcod.console_init_root(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 'noodle game', False)
    # libtcod.sys_set_fps(LIMIT_FPS)
    # _con = libtcod.console_new(settings.MAP_WIDTH, settings.MAP_HEIGHT)
    # _overlay = libtcod.console_new(settings.MAP_WIDTH, settings.MAP_HEIGHT)
    # _panel = libtcod.console_new(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)
    # _last_frame_time = time.time() * 1000
	
###------------------------------------------------------------------------------------------------------------###

def render_all():
    settings.camera_x, settings.camera_y, settings.fov_recompute = move_camera(settings.player.x, settings.player.y, 
                                                                               settings.camera_x, settings.camera_y, 
                                                                               settings.MAP_WIDTH, settings.MAP_HEIGHT, 
                                                                               settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    #print settings.camera_x, settings.camera_y, settings.fov_recompute
    if settings.fov_recompute:
        #recompute FOV if needed
        settings.fov_recompute = False
        libtcod.map_compute_fov(settings.fov_map, settings.player.x,
                                settings.player.y, settings.TORCH_RADIUS,
                                settings.FOV_LIGHT_WALLS, settings.FOV_ALGO)
        libtcod.console_clear(settings.con)

        #go through all tiles, and set their background color according to the FOV
        for y in range(settings.CAMERA_HEIGHT):
            for x in range(settings.CAMERA_WIDTH):
                (map_x, map_y) = (settings.camera_x + x, settings.camera_y + y)
                visible = libtcod.map_is_in_fov(settings.fov_map, map_x, map_y)
                wall = settings.map[map_x][map_y].block_sight
                if not visible:
                    #if it's not visible right now, player can only see after it's explored
                    if settings.map[map_x][map_y].explored:
                        if wall:
                            libtcod.console_put_char_ex(settings.con,
                                                        x, y, '#',
                                                        color.dark_gray,
                                                        color.dark_wall)
                        else:
                            libtcod.console_put_char_ex(settings.con,
                                                        x, y, '.',
                                                        color.dark_gray,
                                                        color.dark_ground)
                else:
                    if wall:
                        libtcod.console_put_char_ex(settings.con, x, y, '#',
                                                    color.light_gray,
                                                    color.light_wall)
                    else:
                        libtcod.console_put_char_ex(settings.con, x, y, '.',
                                                    color.light_gray,
                                                    color.light_ground)
                    settings.map[map_x][map_y].explored = True

    #draw all objects in the  list, except player. We want it to
    #always appear over all other objects, so it is drawn later.
    for object in settings.objects:
        if object != settings.player:
            #print(type(object.char))
            object.draw()
    settings.player.draw()

    libtcod.console_blit(settings.con, 0, 0, settings.SCREEN_WIDTH,
                         settings.SCREEN_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(settings.panel, color.black)
    libtcod.console_clear(settings.panel)

    #print the game messages, one line at a time
    y = 1
    #print(message.game_msgs)
    for single_message in message.game_msgs:
        libtcod.console_set_default_foreground(settings.panel, single_message.color)
        line = single_message.message
        if single_message.count > 1:
            line += ' (x' + str(single_message.count) + ')'
        libtcod.console_print_ex(settings.panel, settings.MSG_X,
                                 y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, single_message.message)
        y += 1

    #show player stats
    render_bar(1, 1, settings.BAR_WIDTH, 'HP', settings.player.fighter.hp,
               settings.player.fighter.max_hp, color.light_red,
               color.darker_red)
    libtcod.console_print_ex(settings.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(settings.dungeon_level) +
                             '\nAttack ' + str(settings.player.fighter.strength) + '\nDefense ' + str(settings.player.fighter.defense) +
                             '\nTurn ' + str(settings.TURN_COUNT))
                             #'\nmovesSinceLastHit ' + str(settings.player.fighter.movesSinceLastHit))

    libtcod.console_set_default_foreground(settings.con, color.white)
    libtcod.console_print_ex(0, 1, settings.SCREEN_HEIGHT - 2,
                             libtcod.BKGND_NONE, libtcod.LEFT, 'HP: ' +
                             str(settings.player.fighter.hp) +
                             '/' + str(settings.player.fighter.max_hp))

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(settings.panel, color.light_gray)
    libtcod.console_print_ex(settings.panel, 1, 0, libtcod.BKGND_NONE,
                             libtcod.LEFT, get_name_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(settings.panel, 0, 0, settings.SCREEN_WIDTH,
                         settings.PANEL_HEIGHT, 0, 0, settings.PANEL_Y)
    
    #draw overlay
    libtcod.console_set_key_color(settings.overlay, color.black)
    libtcod.console_blit(settings.overlay, 0, 0, settings.SCREEN_WIDTH,
                         settings.SCREEN_HEIGHT, 0, 0, 0, 0.4, 1.0)


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(settings.panel, back_color)
    libtcod.console_rect(settings.panel, x, y, total_width, 1,
                         False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(settings.panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(settings.panel, x, y, bar_width, 1,
                             False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(settings.panel, color.white)
    libtcod.console_print_ex(settings.panel, x + old_div(total_width, 2), y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def get_name_under_mouse():
    (x, y) = (settings.mouse.cx, settings.mouse.cy)
    (x, y) = (settings.camera_x + x, settings.camera_y + y)
    names = [obj.name for obj in settings.objects if obj.x == x and
             obj.y == y and libtcod.map_is_in_fov(settings.fov_map,
                                                  obj.x, obj.y)]
    names = ', '.join(names)
    return names.capitalize()

def move_camera(target_x, target_y, camera_x, camera_y, MAP_WIDTH, MAP_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT):
 
    #new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - old_div(CAMERA_WIDTH, 2)  #coordinates so that the target is at the center of the screen
    y = target_y - old_div(CAMERA_HEIGHT, 2)
    #x = target_x - (CAMERA_WIDTH // 2)  #nah, change into these didn't help
    #y = target_y - (CAMERA_HEIGHT // 2) #
 
    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH : x = MAP_WIDTH - CAMERA_WIDTH
    if y > MAP_HEIGHT - CAMERA_HEIGHT : y = MAP_HEIGHT - CAMERA_HEIGHT
 
    if x != camera_x or y != camera_y: settings.fov_recompute = True
 
    #(camera_x, camera_y) = (x, y)
    return (x, y, settings.fov_recompute)
 
def to_camera_coordinates(x, y, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - camera_x, y - camera_y)
 
    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
            return (None, None)  #if it's outside the view, return nothing
 
    return (x, y)