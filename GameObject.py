import libtcodpy as libtcod
import settings
import color
import math
import render_all
from Item import Item

class GameObject:
    def __init__(self, x, y, char, name, color, blocks=False,
                 always_visible=False, fighter=None, ai=None,
                 item=None, equipment=None, placement_range=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        
        self.item = item
        if self.item:
            self.item.owner = self
        
        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            
            self.item = Item()
            self.item.owner = self
        
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
        (x, y) = render_all.to_camera_coordinates(self.x, self.y, settings.camera_x, settings.camera_y, settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
        if (libtcod.map_is_in_fov(settings.fov_map, self.x, self.y) or
                (self.always_visible and
                    settings.map[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(settings.con, self.color)
            libtcod.console_put_char(settings.con, x, y, self.char,
                                     libtcod.BKGND_NONE)
    
    def clear(self):
        (x, y) = render_all.to_camera_coordinates(self.x, self.y, settings.camera_x, settings.camera_y, settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
        if libtcod.map_is_in_fov(settings.fov_map, self.x, self.y):
            libtcod.console_put_char_ex(settings.con, x, y,
                                        '.', color.white,
                                        color.light_ground)

def is_blocked(x, y):
    if settings.map[x][y].blocked:
        return True
    
    for object in settings.objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    
    return False