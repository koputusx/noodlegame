import color
import settings
import message
from component import *
from actions import get_equipped_in_slot
from Item import Item

class Equipment(Component):

    def __init__(self, slot, strength_bonus=0, defense_bonus=0, reflex_bonus=0, max_hp_bonus=0):
        self.strength_bonus = strength_bonus
        self.defense_bonus = defense_bonus
        self.reflex_bonus = reflex_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False

    
    def set_owner(self, entity):
        Component.set_owner(self, entity)
        
        #There must be an Item component for the Equipment component to work properly
        if entity.item is None:
            entity.item = Item()
            entity.item.set_owner(entity)

#class MeleeWeapon(Component):
    #def __init__(self, slot, strength_bonus=0, on_strike=None):
        #self.slot = slot
        #self.strength_bonus = strength_bonus
        #self.on_strike = on_strike
        #self.is_equipped = False


    #def set_owner(self, entity):
        #Component.set_owner(self, entity)
        #if entity.equipment is None:
            #entity.equipment = Equipment('right hand')
            #entity.equipment.set_owner(entity)



