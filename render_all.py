import libtcodpy as libtcod
import settings
import color


def render_all():
    settings.camera_x, settings.camera_y, settings.fov_recompute = move_camera(settings.player.x, settings.player.y, settings.camera_x, settings.camera_y, 
                                                                               settings.MAP_WIDTH, settings.MAP_HEIGHT, 
                                                                               settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    print settings.camera_x, settings.camera_y, settings.fov_recompute
    if settings.fov_recompute:
        settings.fov_recompute = False
        libtcod.map_compute_fov(settings.fov_map, settings.player.x,
                                settings.player.y, settings.TORCH_RADIUS,
                                settings.FOV_LIGHT_WALLS, settings.FOV_ALGO)
        for y in range(settings.CAMERA_HEIGHT):
            for x in range(settings.CAMERA_WIDTH):
                (map_x, map_y) = (settings.camera_x + x, settings.camera_y + y)
                visible = libtcod.map_is_in_fov(settings.fov_map, map_x, map_y)
                wall = settings.map[map_x][map_y].block_sight
                if not visible:
                    if settings.map[map_x][map_y].explored:
                        if wall:
                            libtcod.console_put_char_ex(settings.con,
                                                        x, y, '#',
                                                        color.white,
                                                        color.dark_wall)
                        else:
                            libtcod.console_put_char_ex(settings.con,
                                                        x, y, '.',
                                                        color.white,
                                                        color.dark_ground)
                else:
                    if wall:
                        libtcod.console_put_char_ex(settings.con, x, y, '#',
                                                    color.white,
                                                    color.light_wall)
                    else:
                        libtcod.console_put_char_ex(settings.con, x, y, '.',
                                                    color.white,
                                                    color.light_ground)
                    settings.map[map_x][map_y].explored = True

    for object in settings.objects:
        if object != settings.player:
            object.draw()
    settings.player.draw()

    libtcod.console_blit(settings.con, 0, 0, settings.SCREEN_WIDTH,
                         settings.SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_set_default_background(settings.panel, color.black)
    libtcod.console_clear(settings.panel)

    y = 1
    for (line, msgcolor) in settings.game_msgs:
        libtcod.console_set_default_foreground(settings.panel, msgcolor)
        libtcod.console_print_ex(settings.panel, settings.MSG_X,
                                 y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, line)
        y += 1

    render_bar(1, 1, settings.BAR_WIDTH, 'HP', settings.player.fighter.hp,
               settings.player.fighter.max_hp, color.light_red,
               color.darker_red)
    libtcod.console_print_ex(settings.panel, 1, 3, libtcod.BKGND_NONE,
                             libtcod.LEFT, 'Dungeon level ' +
                             str(settings.dungeon_level))

    libtcod.console_set_default_foreground(settings.con, color.white)
    libtcod.console_print_ex(0, 1, settings.SCREEN_HEIGHT - 2,
                             libtcod.BKGND_NONE, libtcod.LEFT, 'HP: ' +
                             str(settings.player.fighter.hp) +
                             '/' + str(settings.player.fighter.max_hp))

    libtcod.console_set_default_foreground(settings.panel, color.light_gray)
    libtcod.console_print_ex(settings.panel, 1, 0, libtcod.BKGND_NONE,
                             libtcod.LEFT, get_name_under_mouse())

    libtcod.console_blit(settings.panel, 0, 0, settings.SCREEN_WIDTH,
                         settings.PANEL_HEIGHT, 0, 0, settings.PANEL_Y)


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
    libtcod.console_print_ex(settings.panel, x + total_width / 2, y,
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
    x = target_x - CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - CAMERA_HEIGHT / 2
 
    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH : x = MAP_WIDTH - CAMERA_WIDTH
    if y > MAP_HEIGHT - CAMERA_HEIGHT : y = MAP_HEIGHT - CAMERA_HEIGHT
 
    if x != camera_x or y != camera_y: fov_recompute = True
 
    #(camera_x, camera_y) = (x, y)
    return (camera_x, camera_y, fov_recompute)
 
def to_camera_coordinates(x, y, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - camera_x, y - camera_y)
 
    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
            return (None, None)  #if it's outside the view, return nothing
 
    return (x, y)