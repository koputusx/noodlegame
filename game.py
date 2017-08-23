#!/usr/bin/python
#
# libtcod python tutorial
#
 
import libtcodpy as libtcod
import random
import math
import textwrap
import shelve
import sys

 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map portion shown on-screen
CAMERA_WIDTH = 80
CAMERA_HEIGHT = 43

#size of the map
MAP_WIDTH = 93
MAP_HEIGHT = 93
 
#sizes and coordinates relevant for the GUI
BAR_WIDTH = 30
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
 
#parameters for dungeon generator
ROOM_MAX_SIZE = 20
ROOM_MIN_SIZE = 4
MAX_ROOMS = 60
 
#spell values
HEAL_AMOUNT = 40
GREATHEAL_AMOUNT = 80
LIGHTNING_DAMAGE = 30
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
PARALYZE_RANGE = 8
PARALYZE_NUM_TURNS = 10
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
 
 

 
class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        #all tiles start unexplored
        self.explored = False
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
 
class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None, chartype=None, 
                 monstype=None, variables=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self
 
        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self
 
        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self
 
        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self
 
            #there must be an Item component for the Equipment component to work properly
            self.item = Item()
            self.item.owner = self

        self.chartype = chartype
        self.monstype = monstype
        self.variables = variables
 
    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
 
    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
 
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
        fov = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
 
        #Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(MAP_HEIGHT):
            for x1 in range(MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].block_sight, not map[x1][y1].blocked)
 
        #Scan all the objects to see if there are objects that must be navigated around
        #Check also that the object isn't self or the target (so that the start and the end points are free)
        #The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
        for obj in objects:
            if obj.blocks and obj != self and obj != target:
                #Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
 
        #Allocate a A* path
        #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)
 
        #Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)
 
        #Check if the path exists, and in this case, also the path is shorter than 25 tiles
        #The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        #It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away        
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
        	
    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
 
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
 
    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)
 
    def draw(self):
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
            (x, y) = to_camera_coordinates(self.x, self.y, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT)

            if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
			        (self.always_visible and map[self.x][self.y].explored)) and (x != None and y != None):
               #set the color and then draw the character that represents this object at its position
               libtcod.console_set_default_foreground(con, self.color)
               if x == None: print x,y,self.char,self.x, self.y,camera_x,camera_y,CAMERA_WIDTH,CAMERA_HEIGHT
               libtcod.console_put_char(con, x, y, self.char, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        (x, y) = to_camera_coordinates(self.x, self.y, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT)
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, libtcod.black)
 
 
class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, reflex, weapon_skill, shield_skill, speed_value, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.base_reflex = reflex
        self.base_weapon_skill = weapon_skill
        self.base_shield_skill = shield_skill
        self.speed_value = speed_value
        self.xp = xp

        self.death_function = death_function
 
    @property
    def power(self):  #return actual power, by summing up the bonuses from all equipped items
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus
 
    @property
    def defense(self):  #return actual defense, by summing up the bonuses from all equipped items
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus
 
    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus
 
    @property
    def reflex(self): #return actual reflex, by summing up the bonuses from all equipped items
        bonus = sum(equipment.reflex_bonus for equipment in get_all_equipped(self.owner))
        return self.base_reflex + bonus

    @property
    def weapon_skill(self): #return actual weapon skill, by summing up the bonuses from all equipped items
        bonus = sum(equipment.weapon_skill_bonus for equipment in get_all_equipped(self.owner))
        return self.base_weapon_skill + bonus

    @property
    def shield_skill(self): #return actual shield skill, by summing up bonuses etc.
        bonus = sum(equipment.shield_skill_bonus for equipment in get_all_equipped(self.owner))
        return self.base_shield_skill + bonus
 
    def attack(self, target):
        #a formula for attack damage
        hit = (self.reflex + self.weapon_skill) - (target.fighter.reflex + target.fighter.weapon_skill)
        damage = (random.randint(1, 6) + self.power) - target.fighter.defense 

        if hit > 0: #attack will hit
            if damage > 0:
                #make the target take some damage
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                target.fighter.take_damage(damage)
            else:
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
 
        elif hit == 0: #attack has 50% chance of hitting
            if libtcod.random_get_int(0, 0, 1) == 1:
                if damage > 0:
                   #make the target take some damage
                   message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                   target.fighter.take_damage(damage)
                else:
                   message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
            else:
                  message(self.owner.name.capitalize() + ' missed!')
 
        elif hit < 0: #attack has 25% chance of hitting
            if libtcod.random_get_int(0, 1, 4) == 4:
                if damage > 0:
                  #make the target take some damage
                  message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                  target.fighter.take_damage(damage)
                else:
                  message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
            else:
               message(self.owner.name.capitalize() + ' missed!')
 
    def ranged_attack(self, target):
        #a formula for ranged attack damage
        hit = (self.reflex + self.weapon_skill) - (target.fighter.reflex + target.fighter.weapon_skill)
        damage = self.power - target.fighter.defense
 
        if hit > 0: #attack will hit
            if damage > 0:
                #make the target take some damage
                message(self.owner.name.capitalize() + 's ' + ' arrow ' + ' hits ' + target.name + ' for ' + str(damage) + ' hit points.')
                target.fighter.take_damage(damage)
            else:
                message(self.owner.name.capitalize() + 's ' + ' arrow ' + ' hits ' + target.name + ' but it has no effect!')
 
        elif hit == 0: #attack has 50% chance of hitting
            if libtcod.random_get_int(0, 0, 1) == 1:
                if damage > 0:
                   #make the target take some damage
                   message(self.owner.name.capitalize() + 's ' + 'arrow ' + ' hits ' + target.name + ' for ' + str(damage) + ' hit points.')
                   target.fighter.take_damage(damage)
                else:
                   message(self.owner.name.capitalize() + 's ' + ' arrow ' + ' hits ' + target.name + ' but it has no effect!')
            else:
                  message(self.owner.name.capitalize() + 's ' + ' arrow' + ' missed!')
 
        elif hit < 0: #attack has 25% chance of hitting
            if libtcod.random_get_int(0, 1, 4) == 4:
                if damage > 0:
                  #make the target take some damage
                  message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                  target.fighter.take_damage(damage)
                else:
                  message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
            else:
               message(self.owner.name.capitalize() + ' missed!')
 
    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
 
            #check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
 
                if self.owner != player:  #yield experience to the player
                    player.fighter.xp += self.xp
 
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


class Variables:
    #class for variables
    def __init__(self, strength_var, agility_var, alertness_var, weapon_skill_var, shield_skill_var):
        self.strength_var = strength_var
        self.agility_var = agility_var
        self.alertness_var = alertness_var
        self.weapon_skill_var = weapon_skill_var
        self.shield_skill_var = shield_skill_var
 
class BasicMonster:
    #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. if you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_astar(player)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

class RangedMonster:
    #AI for monster using ranged attacks.
    def take_turn(self):
        #monster takes it's turn. if you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(player) >= 10:
                monster.move_astar(player)

            #player is closing in, decide whether you should retreat
            elif monster.distance_to(player) == 3 and player.fighter.hp > 0:
                diceresult = libtcod.random_get_int(0, 1, 3)
                #fall back!
                if diceresult == 1:
                    monster.move_away(player.x, player.y)

                #continue shooting arrows
                elif diceresult == 2:
                    if player.fighter.hp > 0:
                        monster.fighter.ranged_attack(player)

                #move to close combat
                elif diceresult == 3:
                    monster.move_astar(player)

            #player is too close, melee them(if player is still alive)
            elif monster.distance_to(player) < 2 and player.fighter.hp > 0:
                monster.fighter.attack(player)

            #close enough, shoot arrows!(if player is still alive)
            elif player.fighter.hp > 0:
                monster.fighter.ranged_attack(player)

class StationaryMonster:
    #AI for stationary monster.
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
           
           if (monster.distance_to(player) < 2) and player.fighter.hp > 0:
              monster.fighter.attack(player)
			  
class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
 
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class ParalyzedMonster:
    #AI for a temporarily paralyzed monster(reverts to previous AI after while).
    def __init__(self, old_ai, old_reflex, old_weapon_skill, num_turns=PARALYZE_NUM_TURNS):
        self.old_ai = old_ai
        self.old_reflex = old_reflex
        self.old_weapon_skill = old_weapon_skill
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #still paralyzed
            print "before"
            print self.num_turns
            print self.owner.fighter.reflex
            print self.owner.fighter.weapon_skill
            #monster is paralyzed and therefore can't do anything
            message('The ' + self.owner.name + ' is paralyzed!', libtcod.yellow)
            self.owner.fighter.reflex = 0
            print "after"
            self.owner.fighter.weapon_skill = 0
            print self.num_turns
            print self.owner.fighter.reflex
            print self.owner.fighter.weapon_skill
            self.num_turns -= 1

        else:  #restore previous AI (this one is deleted because reasons).
            self.owner.ai = self.old_ai
            self.owner.reflex = self.old_reflex
            self.owner.weapon_skill = self.old_weapon_skill
            message('The ' + self.owner.name + ' is no longer paralyzed!', libtcod.red)
			
class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function
 
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)
 
            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()
 
    def drop(self):
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()
 
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)
 
    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
 
        #just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
 
class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, power_bonus=0, defense_bonus=0, reflex_bonus=0, weapon_skill_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.reflex_bonus = reflex_bonus
        self.weapon_skill_bonus = weapon_skill_bonus
        self.max_hp_bonus = max_hp_bonus
 
        self.slot = slot
        self.is_equipped = False
 
    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
 
    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
 
        #equip object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
 
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

#    #monster abilities
#   def __init__(self, doppelganger=0):
#        self.doppelganger = doppelganger
#
#    def doppelganger():
#        if doppelganger == 1:
#            set self.monster.stat == player.stat
#            set notYetUpdated == 0

#class ItemAbility:
#    #item abilities
#    def __init__(self, piercing=False):
#        self.piercing = piercing
#
#    def piercing():
#        if piercing is True:
#        target.fighter.defense = 0
 
def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None
 
def get_all_equipped(obj):  #returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list        

    else:
        return []  #other objects have no equipment
 
def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False
 
def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False
 
def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def make_map():
    global map, objects, stairs
 
    #the list of objects with just the player
    objects = [player]
 
    #fill map with "blocked" tiles
    map = [[ Tile(True)
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]
 
    rooms = []
    num_rooms = 0
    special_monster_room = 1
    #special_monster = None
    if dungeon_level == 10:
        special_monster = 'Ogre'
        print(dungeon_level,special_monster)
    elif dungeon_level == 20:
        special_monster = 'Giant'
    else:
        special_monster = None
 
    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 2)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 2)
 
        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
 
        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            create_room(new_room)
 
            #add some contents to this room, such as monsters
            if r == special_monster_room:
                place_objects(new_room, special_monster)
                print(new_room, special_monster, r)
            else:
                place_objects(new_room, None)
                print(new_room, None, r)
 
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
 
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()
 
                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
 
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
 
    #create stairs at the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters
    for y in range(0, MAP_HEIGHT):
        for x in range(0, MAP_WIDTH):
            if map[x][y].blocked:
                sys.stdout.write("B")
            else:
                sys.stdout.write(".")
        print
    return map, Object, stairs
 
def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
 
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]
 
def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0
 
def place_objects(room, special_monster):
    #this is where we decide the chance of each monster or item appearing.
    print(special_monster)
    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
 
    #chance of each monster
    monster_chances = {}
    monster_chances['orc'] = from_dungeon_level([[60, 2], [70, 3], [80, 4]])
    monster_chances['troll'] = from_dungeon_level([[15, 5], [30, 7], [60, 9]])
    monster_chances['hideous'] = from_dungeon_level([[20, 4], [40, 6], [70, 8]])
    monster_chances['ettin'] = from_dungeon_level([[15, 6], [30, 8], [60, 10]])
    monster_chances['melted one'] = from_dungeon_level([[15, 5], [30, 7], [60, 10]])
    monster_chances['flayed one'] = from_dungeon_level([[15, 8], [30, 10], [60, 11]])
    monster_chances['goblin'] = 80
    monster_chances['goblin archer'] = 30
    #monster_chances['rat'] = 50
 
    #maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])
 
    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 40  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 3]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[50, 2]])
    item_chances['magic missile'] = from_dungeon_level([[5, 10]])
    item_chances['sword'] =     from_dungeon_level([[5, 4]])
    item_chances['shield'] =    from_dungeon_level([[15, 8]])
    item_chances['helm'] =      from_dungeon_level([[50, 2]])
    item_chances['armor'] =     from_dungeon_level([[10, 9]])
    item_chances['sword of slaying'] = from_dungeon_level([[5, 10]])
    item_chances['greater heal'] = from_dungeon_level([[25, 6]])
    item_chances['cloak'] = 30
    item_chances['paralyze'] = 90

    if special_monster is not None:
        print(special_monster)
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        if special_monster == 'Giant':
            fighter_component = Fighter(hp=200, defense=20, power=20, reflex=10, weapon_skill=10, shield_skill=0, speed_value=0, xp=100, death_function=monster_death)
            ai_component = BasicMonster()

            monster = Object(x, y, 'G', 'Giant', libtcod.gold,
                             blocks=True, fighter=fighter_component, ai=ai_component)
            objects.append(monster)

        elif special_monster == 'Ogre':
            fighter_component = Fighter(hp=150, defense=15, power=15, reflex=10, xp=500, weapon_skill=0, shield_skill=0, speed_value=0, death_function=monster_death)
            ai_component = BasicMonster()

            monster = Object(x, y, 'O', 'Ogre', libtcod.gold,
                             blocks=True, fighter=fighter_component, ai=ai_component)
            objects.append(monster)
	
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':
                #create an orc
                fighter_component = Fighter(hp=15, defense=1, power=5, reflex=3, weapon_skill=0, shield_skill=0, speed_value=0, xp=40, death_function=monster_death)
                ai_component = BasicMonster()
 
                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
 
            elif choice == 'troll':
                #create a troll
                fighter_component = Fighter(hp=20, defense=2, power=8, reflex=3, weapon_skill=0, shield_skill=0, speed_value=0, xp=105, death_function=monster_death)
                ai_component = BasicMonster()
 
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
 
            elif choice == 'hideous':
                #create a hideous
                fighter_component = Fighter(hp=15, defense=1, power=6, reflex=4, weapon_skill=0, shield_skill=0, speed_value=0, xp=55, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'h', 'hideous', libtcod.darker_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
 
            elif choice == 'ettin':
                #create an ettin
                fighter_component = Fighter(hp=30, defense=3, power=9, reflex=5, weapon_skill=0, shield_skill=0, speed_value=0, xp=155, death_function=monster_death)
                ai_component = BasicMonster()
 
                monster = Object(x, y, 'E', 'ettin', libtcod.pink,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'melted one':
                #create a melted one
                fighter_component = Fighter(hp=40, defense=4, power=8, reflex=0, weapon_skill=0, shield_skill=0, speed_value=0, xp=150, death_function=monster_death)
                ai_component = StationaryMonster()
                
                monster = Object(x, y, 'X', 'Melted one', libtcod.lighter_red,
				                 blocks=True, fighter=fighter_component, ai=ai_component, monstype='stationary')

            elif choice == 'goblin':
                #create goblin
                fighter_component = Fighter(hp=10, defense=1, power=3, reflex=2, weapon_skill=1, shield_skill=0, speed_value=0, xp=200, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'g', 'goblin', libtcod.light_blue,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
								 
            elif choice == 'rat':
                #create a rat
                fighter_component = Fighter(hp=5, defense=0, power=1, reflex=1, weapon_skill=0, shield_skill=0, speed_value=0, xp=25, death_function=monster_death)
                ai_component = BasicMonster()
            
                monster = Object(x, y, 'r', 'rat', libtcod.light_grey,
                                blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'flayed one':
                #create flayed one
                fighter_component = Fighter(hp=40, defense=6, power=10, reflex=5, weapon_skill=0, shield_skill=0, speed_value=0, xp=160, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'f', 'flayed one', libtcod.light_purple,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'goblin archer':
                #create goblin archer
                fighter_component = Fighter(hp=10, defense=1, power=3, reflex=2, weapon_skill=0, shield_skill=0, speed_value=0, xp=200, death_function=monster_death)
                ai_component = RangedMonster()

                monster = Object(x, y, 'g', 'goblin archer', libtcod.light_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
            objects.append(monster)
 
    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)
 
    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
			
            elif choice == 'greater heal':
			     #create potion of greater healing
				 item_component = Item(use_function=cast_greaterheal)
				 item = Object(x, y, '!', 'potion of greater healing', libtcod.violet, item=item_component)
 
            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)
 
            elif choice == 'fireball':
                #create a fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_red, item=item_component)
 
            elif choice == 'confuse':
                #create a confuse scroll
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

            elif choice == 'paralyze':
                #create scroll of paralyzation
                item_component = Item(use_function=cast_paralyze)
                item = Object(x, y, '#', 'scroll of paralyzation', libtcod.red, item=item_component)
 
            elif choice == 'magic missile':
                #create a magic missile scroll
                item_component = Item(use_function=cast_magicmissile)
                item = Object(x, y, '#', 'scroll of magic missile', libtcod.pink, item=item_component)
 
            elif choice == 'sword':
                #create a sword
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
 
            elif choice == 'shield':
                #create a shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
 
            elif choice == 'helm':
                #create a helm
                equipment_component = Equipment(slot='head', defense_bonus=1)
                item = Object(x, y, 'Q', 'helm', libtcod.darker_orange, equipment=equipment_component)
 
            elif choice == 'armor':
                #create an armor
                equipment_component = Equipment(slot='body', defense_bonus=3)
                item = Object(x, y, '}', 'armor', libtcod.gold, equipment=equipment_component)
 
            elif choice == 'sword of slaying':
                #create a sword of slaying
                equipment_component = Equipment(slot='right hand', power_bonus=6)
                item = Object(x, y, '/', 'sword of slaying', libtcod.brass, equipment=equipment_component)
 
            elif choice == 'cloak':
                #create a cloak
                equipment_component = Equipment(slot='cloaks', reflex_bonus=1)
                item = Object(x, y, ']', 'cloak', libtcod.light_red, equipment=equipment_component)
 
            objects.append(item)
            item.send_to_back()  #items appear below other objects
            item.always_visible = True  #items are visible even out-of-FOV, if in an explored area
 
 
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
 
    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))
 
def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse
 
    (x, y) = (mouse.cx, mouse.cy)
    (x, y) = (camera_x + x, camera_y + y)
 
    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
 
    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def move_camera(target_x, target_y, MAP_WIDTH, MAP_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT):
    global camera_x, camera_y, fov_recompute
 
    #new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - CAMERA_HEIGHT / 2
 
    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH - 1: x = MAP_WIDTH - CAMERA_WIDTH - 1
    if y > MAP_HEIGHT - CAMERA_HEIGHT - 1: y = MAP_HEIGHT - CAMERA_HEIGHT - 1
 
    if x != camera_x or y != camera_y: fov_recompute = True
 
    (camera_x, camera_y) = (x, y)
 
def to_camera_coordinates(x, y, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - camera_x, y - camera_y)
 
    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
            return (None, None)  #if it's outside the view, return nothing
 
    return (x, y)
 
def render_all():
    global fov_map
    global fov_recompute
 
    move_camera(player.x, player.y, MAP_WIDTH, MAP_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT)
  
    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        libtcod.console_clear(con)#what does do?
 
        #go through all tiles, and set their background color according to the FOV
        for y in range(CAMERA_HEIGHT):
            for x in range(CAMERA_WIDTH):
                    (map_x, map_y) = (camera_x + x, camera_y + y)
                    visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)
                    wall = map[map_x][map_y].block_sight
                    if not visible:
                       #if it's not visible right now, the player can only see it if it's explored
                       if map[map_x][map_y].explored:
                           if wall:
                               libtcod.console_put_char_ex(con, x, y, '#', libtcod.white, libtcod.black)
                           else:
                               libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, libtcod.black)
                    else:
                       #it's visible
                       if wall:
                           libtcod.console_put_char_ex(con, x, y, '#', libtcod.white, libtcod.black)
                       else:
                           libtcod.console_put_char_ex(con, x, y, '.', libtcod.white, libtcod.black )
                           #since it's visible, explore it
                       map[map_x][map_y].explored = True
 
    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()
 
    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
 
 
    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
 
    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT,line)
        y += 1
 
    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level) + '\nattack ' + str(player.fighter.power) +
                             '\nDefense ' + str(player.fighter.defense) + '\nAlertness ' + str(player.fighter.reflex) + '   [h]elp')
 
    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
 
    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
 
 
def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )
 
 
def player_move_or_attack(dx, dy):
    global fov_recompute
 
    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy
 
    #try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break
 
    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True
 
 
def menu(header, options, width):
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    print(header,options,width)
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
 
    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
 
    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
 
    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
 
    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
 
    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    print("before key")
    while key.vk == libtcod.KEY_NONE:
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
    #key = libtcod.console_wait_for_keypress(True)
    print("after key")
    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen)
 
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None
 
def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
 
    index = menu(header, options, INVENTORY_WIDTH)
 
    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item
 
def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"
 
def handle_keys(key):
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
 
    if game_state == 'playing':
        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP5:
            pass  #do nothing ie wait for the monster to come to you
        else:
            #test for other keys
            key_char = chr(key.c)
 
            if key_char == ',':
                #pick up an item
                for object in objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
 
            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
 
            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
 
            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                       '\nExperience to level up: ' + str(level_up_xp) + '\n\nbase stats   stat bonuses' + '\nattack: ' + str(player.fighter.base_power) + 
                       '\ndefense: ' + str(player.fighter.base_defense) + '\nalertness: ' + str(player.fighter.base_reflex) + 
					   '\n\nWeapon skill ' + str(player.fighter.weapon_skill) , CHARACTER_SCREEN_WIDTH)
 
            if key_char == 'h':
                #show help menu
				msgbox('alt+enter toggles fullscreen. \nUse either directional buttons, or numpad(recommended) to move'
                       '\nPress , to pick up items. \nPress i to open inventory. \nPress d to drop items. \nPress c to display character stats'
                       '\nPress < to go down the stairs. \nYou can press 5 to skip your turn. \nHover the mouse pointer over object to show its name.'
                       '\nPress esc to quit the game. Game saves automatically upon exit.')
 
            if key_char == '<':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
 
            return 'didnt-take-turn'
 
def check_level_up():
    # see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        # it is! level up and ask to raise some stats
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', libtcod.yellow)
 
        # don't need this any more: current_menu_item = 0 # we need to track the size of the menu
        m = []
        hp_menu = menu_item_add(m, 'Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')') # only first item always in menu
        
        # if allowed to add power, then append Strength question to menu, set strength_menu to the next number in squence, and add 1 to size of menu
        strength_menu = optional_menu_item_add(m, 'Strength (+1 attack, from ' + str(player.fighter.power) + ')', 
                                               (player.fighter.power < (player.level+player.variables.strength_var)))
        agility_menu =  optional_menu_item_add(m, 'Agility (+1 defense, from ' + str(player.fighter.defense) + ')',
                                               (player.fighter.defense < (player.level+player.variables.agility_var)))
        alertness_menu = optional_menu_item_add(m, 'Alertness (+1 alertness, from ' + str(player.fighter.reflex) + ')', 
                                                (player.fighter.reflex < (player.level+player.variables.alertness_var)))
        weapon_skill_menu = optional_menu_item_add(m, 'Weapon skill (+1 weapon skill, from ' + str(player.fighter.weapon_skill) + ')', 
                                                   (player.fighter.weapon_skill < (player.level+player.variables.weapon_skill_var)))
 
        choice = None
        while choice == None:  # keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                          m, LEVEL_SCREEN_WIDTH)
 
            if choice == hp_menu:
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == strength_menu:
                player.fighter.base_power += 1
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == agility_menu:
                player.fighter.base_defense += 1
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == alertness_menu:
                player.fighter.base_reflex += 1
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == weapon_skill_menu:
                player.fighter.base_weapon_skill += 1
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20

def menu_item_add(menu,text):
    menu.append(text)
    return len(menu)-1
    
def optional_menu_item_add(menu,text,test):
    if (test):
        return menu_item_add(menu,text)
    else:
        return -1

 
def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()
 
def target_tile(max_range=None):
    global key, mouse
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()
 
        (x, y) = (mouse.cx, mouse.cy)
        (x, y) = (camera_x + x, camera_y + y)
 
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
 
def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None
 
        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj
 
def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy
 
def cast_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health!', libtcod.red)
        return 'cancelled'
 
    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

def cast_greaterheal():
    #heal the player moar
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health!', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel much better!', libtcod.light_violet)
    player.fighter.heal(GREATHEAL_AMOUNT)
	
def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
 
    #zap it!
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)
 
def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
 
    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)
 
def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    print(monster)
    if monster is None: return 'cancelled'
    print(monster.monstype)
    if monster.monstype=='stationary': return 'immune'
 
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_paralyze():
    #ask player for target to confuse
    message('Left-click on an enemy to paralyze it, or right-click to cancel it.', libtcod.light_cyan)
    monster = target_monster(PARALYZE_RANGE)
    if monster is None: return 'cancelled'

    #replace the monster's AI with paralyzed one
    old_ai = monster.ai
    old_reflex = monster.fighter.reflex
    old_weapon_skill = monster.fighter.weapon_skill
    monster.ai = ParalyzedMonster(old_ai, old_reflex, old_weapon_skill)
    monster.ai.owner = monster #tell the new component who owns it.
    message('The ' + monster.name + ' suddenly falls to the ground, unable to do anything!', libtcod.light_green)
	
def cast_magicmissile():
    #for now ask a player for target to destroy
    message('Double left-click an enemy to hurt it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(MAGICMISSILE_RANGE)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The ' + monster.name + ' is hit by powerfull stream of energy for ' + str(MAGICMISSILE_DAMAGE) + ' hit points.', libtcod.pink) 
    monster.fighter.take_damage(MAGICMISSILE_DAMAGE)
 
def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['stairs_index'] = objects.index(stairs)  #same for the stairs
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()
 
def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, stairs, inventory, game_msgs, game_state, dungeon_level
 
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    stairs = objects[file['stairs_index']]  #same for the stairs
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    file.close()
 
    initialize_fov()

#def princess():
#    skills_component = Skills(weapon_skill=100, shield_skill=100)
#    fighter_component = Fighter(hp=100, defense=100, power=100, reflex=100, xp=1000, skills=skills_component)
#    ai_component = PrincessAI()
#    princess = Object(0, 0, '@', 'princess', libtcod.blue, blocks=True, fighter=fighter_component, ai=ai_component)

def warrior_class():
    global player
    fighter_component = Fighter(hp=20, defense=2, power=2, reflex=2, weapon_skill=2, shield_skill=0, speed_value=0, xp=0, death_function=player_death)
    variables_component = Variables(strength_var=1, agility_var=1, alertness_var=1, weapon_skill_var=1, shield_skill_var=3)
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, variables=variables_component, chartype='warrior')

def scholar_class():
    global player
    fighter_component = Fighter(hp=10, defense=2, power=1, reflex=2, weapon_skill=1, shield_skill=0, speed_value=0, xp=0, death_function=player_death)
    variables_component = Variables(strength_var=0, agility_var=0, alertness_var=1, weapon_skill_var=1, shield_skill_var=1)
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, variables=variables_component, chartype='scholar')

def char_creation(): #player chooses their character class
    img = libtcod.image_load('menu_background.png')

    
    #show background image, twice the regular console resolution
    libtcod.image_blit_2x(img, 0, 0, 0)
    #show character creation screen
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                             'CHARACTER CREATION \n\nPlease choose a character:')

    choice = menu('', ['warrior', 'scholar'], 24)

    if choice == 0:   #warrior class is chosen
        warrior_class()
    if choice == 1:   #scholar class is chosen
        scholar_class()

def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level
 
    #create object representing the player
    player
 
    player.level = 1
 
    #generate map (at this point it's not drawn to the screen)
    dungeon_level = 1
    make_map()
    initialize_fov()
 
    game_state = 'playing'
    inventory = []
 
    #create the list of game messages and their colors, starts empty
    game_msgs = []
 
    #a warm welcoming message!
    message('Welcome stranger to the the eternal, twisted and slimy realm of noodles. Press h for help', libtcod.red)
 
    #initial equipment:
    if player.chartype == 'warrior':
        equipment_component = Equipment(slot='right hand', power_bonus=3)
        obj1 = Object(0, 0, '/', 'sword', libtcod.sky, equipment=equipment_component)
        inventory.append(obj1)
        equipment_component.equip()
        obj1.always_visible = True
    elif player.chartype == 'scholar':
        equipment_component = Equipment(slot='right hand', power_bonus=2)
        obj2 = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
        inventory.append(obj2)
        equipment_component.equip()
        obj2.always_visible = True
    print(player, inventory)

#def end_game():
    #end of game
    #if dungeon_level == 10
	
def next_level():
    #advance to the next level
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%
 
    dungeon_level += 1
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    make_map()  #create a fresh new level!
    initialize_fov()
 
def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True
 
    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].blocked, not map[x][y].block_sight)
 
    libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)
 
def play_game():
    global camera_x, camera_y, key, mouse
 
    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()
 
    (camera_x, camera_y) = (0, 0)

    #main loop
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        #render the screen
        render_all()
 
        libtcod.console_flush()
 
        #level up if needed
        check_level_up()
 
        #erase all objects at their old locations, before they move
        for object in objects:
            object.clear()
 
        #handle keys and exit game if needed
        player_action = handle_keys(key)
        if player_action == 'exit':
            save_game()
            break
 
        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

def help_menu():
    img = libtcod.image_load('menu_background.png')
    
    #show the background image, at twice the regural console resolution
    libtcod.image_blit_2x(img, 0, 0, 0)
    
    #help menu
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                             'HELP MENU')
 
    choice = menu('', ['controlls', 'back to main menu'], 24)
    if choice == 0: #controlls
        msgbox('alt+enter toggles fullscreen. \nUse either directional buttons, or numpad(recommended) to move'
           '\nPress , to pick up items. \nPress i to open inventory. \nPress d to drop items. \nPress c to display character stats'
           '\nPress < to go down the stairs. \nYou can press 5 to skip your turn. \nHover the mouse pointer over object to show its name.'
           '\nPress esc to quit the game. Game saves automatically upon exit.')
    if choice == 1: #back to mainmenu
        main_menu()

def main_menu():
    img = libtcod.image_load('menu_background.png')
 
    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)
 
        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'INFINITE CAVERNS OF NOODLES')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Kopu, with help of hkas and roguelike tutorial.')
 
        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Help menu', 'Quit'], 24)
 
        if choice == 0:  #new game
            char_creation()
            new_game()
            print(player, inventory)
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        if choice == 2:  #help menu
            help_menu()
        elif choice == 3:  #quit
            break
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'the noodlegame', False)
libtcod.console_credits()
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
#myRnd = libtcod.random_new_from_seed()
 
main_menu()