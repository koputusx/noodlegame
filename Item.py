import settings
import message
import color
from actions import get_equipped_in_slot
from component import *

class Item(Component):
    def __init__(self, description=None, count=1, use_function=None):
        self.description = description
        self.use_function = use_function
        self.count = count
    
    def can_combine(self, other):
        #returns true if other can stack with self
        return other.item and other.name == self.owner.name

    def pick_up(self):
        for p in settings.inventory:
            if self.can_combine(p):
                p.item.count += self.count
                print(p.item.count)
                #settings.objects.remove(self.owner)
                #message.message('You picked up a ' + self.owner.name + '.',
                                #color.green)
        if len(settings.inventory) >= 26:
            message.message('Your inventory is full, you cannot pick up ' +
                            self.owner.name + '.', color.red)
        else:
            settings.inventory.append(self.owner)
            settings.objects.remove(self.owner)
            message.message('You picked up a ' + self.owner.name + '.',
                            color.green)

            equipment = self.owner.equipment
            #melee_weapon = self.owner.melee_weapon
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()
            #elif melee_weapon and get_equipped_in_melee_slot(melee_weapon.slot) is None:
                #melee_weapon.equip()

    def drop(self):
        must_split = False
        if object.item.count > 1:
            object.item.count -= 1
            must_split = True
        if self.owner.equipment:
            self.owner.equipment.dequip()
        
        #if self.owner.melee_weapon:
            #self.owner.melee_weapon.dequip()

        settings.objects.append(self.owner)
        settings.inventory.remove(self.owner)
        self.owner.x = settings.player.x
        self.owner.y = settinmgs.player.y
        message.message('You dropped a ' + self.owner.name + '.', color.yellow)

    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        
        #elif self.owner.melee_weapon:
            #self.owner.melee_weapon.toggle_equip()
            #return

        if self.use_function is None:
            message.message('The ' + self.owner.name + ' cannot be used. ')
        else:
            if self.use_function() != 'cancelled':
                settings.inventory.remove(self.owner)