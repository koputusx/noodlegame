import libtcodpy as libtcod
import settings
import color
import math
import render_all
from Item import Item


class GameObject:
    def __init__(self, x, y, char, name, color, speed_value=0,
                 blocks=False, always_visible=False, interactable=None,
                 fighter=None, ai=None, item=None, equipment=None, 
                 chartype=None, monstype=None, variables=None, 
                 melee_weapon=None, missile_weapon=None, placement_range=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.speed_value = speed_value
        self.blocks = blocks
        self.always_visible = always_visible

        self.interactable = interactable
        self.ensure_ownership(interactable)

        self.fighter = fighter
        self.ensure_ownership(fighter)

        self.ai = ai
        self.ensure_ownership(ai)
        
        self.item = item
        self.ensure_ownership(item)
        
        self.equipment = equipment
        self.ensure_ownership(equipment)
        
        self.chartype = chartype
        self.monstype = monstype
        self.variables = variables

        self.melee_weapon = melee_weapon
        self.ensure_ownership(melee_weapon)

        self.missile_weapon = missile_weapon
        self.ensure_ownership(missile_weapon)
        
        self.placement_range = placement_range
    
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def move_towards(self, target_x, target_y):
        #dx = target_x - self.x
        #dy = target_y - self.y
        #distance = math.sqrt(dx ** 2 + dy ** 2)
        
        #dx = int(round(dx / distance))
        #dy = int(round(dy / distance))
        #self.move(dx, dy)
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
 
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
        if not is_blocked(self.x + mx, self.y + my):
            self.x += mx
            self.y += my
        else:
            if abs(dx) > abs(dy):
                if not is_blocked(self.x + mx, self.y):
                    self.x += mx
                elif not is_blocked(self.x, self.y+my):
                    self.y += my
            else:
                if not is_blocked(self.x, self.y+my):
                    self.y += my
                elif not is_blocked(self.x + mx, self.y):
                    self.x += mx

    def move_away(self, target_x, target_y):
        #vector from this object to the target, and distance

        dx = target_x - self.x
        dy = target_y - self.y
        dx = -dx
        dy = -dy

        mx = 0
        my = 0

        #get the direction of the vector
        print(target_x, self.x, mx, target_y, self.y, my)
        if dx > 0:
            mx = 1
        elif dx < 0:
            mx = -1
        if dy > 0:
            my = 1
        elif dy < 0:
            my = -1
 
        #try diagonal first
        if not is_blocked(self.x + mx, self.y + my):
            self.x += mx
            self.y += my
        else:
            if abs(dx) > abs(dy):
                if not is_blocked(self.x + mx, self.y):
                    self.x += mx
                elif not is_blocked(self.x, self.y+my):
                    self.y += my
            else:
                if not is_blocked(self.x, self.y+my):
                    self.y += my
                elif not is_blocked(self.x + mx, self.y):
                    self.x += mx


    def move_astar(self, target):
        #Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(settings.MAP_WIDTH, settings.MAP_HEIGHT)
 
        #Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(settings.MAP_HEIGHT):
            for x1 in range(settings.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not settings.map[x1][y1].block_sight, not settings.map[x1][y1].blocked)
 
        #Scan all the objects to see if there are objects that must be navigated around
        #Check also that the object isn't self or the target (so that the start and the end points are free)
        #The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
        for obj in settings.objects:
            if obj.blocks and obj != self and obj != target:
                #Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
 
        #Allocate a A* path
        #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)
 
        #Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)
 
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
                self.x = x
                self.y = y
        else:
            #Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            #it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y)
        
        #delete the path to free memory
        libtcod.path_delete(my_path)

    def move_towards_n(self, target):
        for x in range(self.speed_value):
            if self.distance_to(target) > 1.5: #1.5 because of diagonals
                self.move_astar(target)

    def ensure_ownership(self, component):
        if (component):
            component.set_owner(self)


    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
    
    def send_to_back(self):
        settings.objects.remove(self)
        settings.objects.insert(0, self)
    
    def draw(self):
        (x, y) = render_all.to_camera_coordinates(self.x, self.y, 
                                                  settings.camera_x, settings.camera_y, 
                                                  settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
        if (libtcod.map_is_in_fov(settings.fov_map, self.x, self.y) or
                (self.always_visible and
                    settings.map[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(settings.con, self.color)
            libtcod.console_put_char(settings.con, x, y, self.char,
                                     libtcod.BKGND_NONE)
    
    def clear(self):
        (x, y) = render_all.to_camera_coordinates(self.x, self.y, 
                                                  settings.camera_x, settings.camera_y, 
                                                  settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
        if libtcod.map_is_in_fov(settings.fov_map, self.x, self.y):
            libtcod.console_put_char_ex(settings.con, x, y,
                                        '.', color.light_gray,
                                        color.light_ground)

def is_blocked(x, y):
    if settings.map[x][y].blocked:
        return True
    
    for object in settings.objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    
    return False

