import libtcodpy as libtcod
import settings


def closest_monster(max_range):
    #find the closest enemy, up to the maximum range and in players FOV
    closest_enemy = None
    closest_dist = max_range + 1 #start with (slightly more than) maximum distance

    for object in settings.objects:
        if object.fighter and not object == settings.player and libtcod.map_is_in_fov(settings.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = settings.player.distance_to(object)
            if dist < closest_dist: #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None: #player cancelled
            return None

        #return the first clicked monster, otherwise continue looking
        for obj in settings.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != settings.player:
                return obj

def target_tile(max_range=None):
    from render_all import render_all
    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, settings.key,
                                    settings.mouse)
        render_all()

        (x, y) = (settings.mouse.cx, settings.mouse.cy)
        (x, y) = (settings.camera_x + x, settings.camera_y + y)

        if settings.mouse.rbutton_pressed or \
           settings.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

        if (settings.mouse.lbutton_pressed and
            libtcod.map_is_in_fov(settings.fov_map, x, y) and
            (max_range is None or
             settings.player.distance(x, y) <= max_range)):
            return (x, y)