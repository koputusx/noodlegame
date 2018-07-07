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
    
    #@property
    #def x(self):
        #return self.pos.x
    
    #@property
    #def y(self):
        #return self.pos.y


    def ensure_ownership(self, component):
        if (component):
            component.set_owner(self)


    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
    
    #def distance(self, pos):
        #return the distance to some coordinates
        #return math.sqrt((pos.x - self.x) ** 2 + (pos.y - self.y) ** 2)
    
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