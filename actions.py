import settings
import message
from component import *



#def pick_up(actor, o, report=True):
    #Add an Object to the actor's inventory and remove from the map.
    #for p in actor.inventory:
        #if o.item.can_combine(p):
            #p.item.count += o.item.count
            #actor.current_map.objects.remove(o)
            #if report:
                #log.message(actor.name.capitalize() + ' picked up a ' + o.name + '!', libtcod.green)
            #return True

    #if len(actor.inventory) >= 22:
        #if report:
            #log.message(actor.name.capitalize() + ' inventory is full, cannot pick up ' +
                        #o.name + '.', libtcod.red)
        #return False
    #else:
        #actor.inventory.append(o)
        #actor.current_map.objects.remove(o)
        #if report:
            #log.message(actor.name.capitalize() + ' picked up a ' + o.name + '!', libtcod.green)

        # Special case: automatically equip if the corresponding equipment slot is unused.
        #equipment = o.equipment
        #if equipment and _get_equipped_in_slot(actor, equipment.slot) is None:
            #equip(actor, equipment)
        #return True




def get_equipped_in_slot(slot):
    for obj in settings.inventory:
        if (obj.equipment and obj.equipment.slot == slot and
                obj.equipment.is_equipped):
            return obj.equipment


#def toggle_equip(actor, eqp):
    #if eqp.is_equipped:
        #dequip(actor, eqp)
    #else:
        #equip(actor, eqp)

#def equip(actor, eqp):
    #old_equipment = get_equipped_in_slot(actor, actor.slot)
    #if old_equipment is not None:
        #dequip(actor, old_equipment)

    #eqp.is_equipped = True
    #message.message('Equipped ' + eqp.owner.name + ' on ' +
                    #eqp.slot + '.', color.light_green)

#def dequip(actor, eqp):
    #if not eqp.is_equipped:
        #return
    #eqp.is_equipped = False
    #message.message('Dequipped ' + eqp.owner.name + ' from ' +
                    #eqp.slot + '.', color.yellow)

#def get_equipped_in_slot(actor, slot):
    #if hasttr(actor, 'inventory'):
        #for obj in actor.inventory:
            #if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                #return obj.equipment
    #return None