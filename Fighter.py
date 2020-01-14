from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range
from past.utils import old_div
import libtcodpy as libtcod

import settings
import message
import random
from component import *

class Fighter(Component):
    def __init__(self, hp, defense, strength, reflex, regen_rate, regen_amount,
                 xp, wound_counter, move_probability=0, attack_number=0, death_function=None, skills={}, status_effects={}): #movesSinceLastHit, 
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_strength = strength
        self.base_reflex = reflex
        self.regen_rate = regen_rate
        self.regen_amount = regen_amount
        #self.movesSinceLastHit = movesSinceLastHit
        self.move_probability = move_probability
        self.attack_number = attack_number
        self.xp = xp
        self.wound_counter = wound_counter
        self.death_function = death_function
        self.skills = skills
        self.status_effects = status_effects

    @property
    def strength(self):
        bonus = sum(equipment.strength_bonus for 
                    equipment in get_all_equipped(self.owner))
        return self.base_strength + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for 
                    equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def reflex(self):
        bonus = sum(equipment.reflex_bonus for 
                    equipment in get_all_equipped(self.owner))
        return self.base_reflex + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for
                    equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus
    
    # @property
    # def movesSinceLastHit(self):
        # return self.movesSinceLastHit

    def attack_n(self, target): #attack n amount of times as determined by attack_number
        for x in range(self.attack_number):
            self.attack(target)

    def attack(self, target):
        #a formula for attack damage
        #attacker to-hit roll:
        to_hit_roll = random.randint(1, 6) + self.reflex
        #defender evasion roll:
        evasion_roll = random.randint(1, 6) + target.fighter.reflex
        #damage roll:
        damage_roll = random.randint(1, 6) + self.strength
        #defense roll:
        defense_roll = random.randint(1, 6) + target.fighter.defense
		#damage:
        damage = damage_roll - defense_roll

        if to_hit_roll > evasion_roll: #attack will hit
            if damage_roll > defense_roll:
                #make the target take some damage
                message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                target.fighter.take_damage(damage)
            else:
                message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
 
        elif to_hit_roll == evasion_roll: #attack has 50% chance of hitting
            if libtcod.random_get_int(0, 0, 1) == 1:
                if damage_roll >  defense_roll:
                   #make the target take some damage
                   message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
                   target.fighter.take_damage(damage)
                else:
                   message.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
            else:
                  message.message(self.owner.name.capitalize() + ' missed!')
 
        else: #attack misses
            message.message(self.owner.name.capitalize() + ' missed!')

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != settings.player:
                    settings.player.fighter.xp += self.xp


    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


    # @property
    # def health_regen(self):
      # #if hp is less than maximum, heal regen_amount (usually 1) of health every X turn until max hp is reached
      # #when last damage is inflicted, it start to count every turn until it reaches (HP_REGEN_TIME / fighter.regen_rate)(usually 100)
      # #when (HP_REGEN_TIME / regen_rate) is reached fighter is healed by regen_amount
      # #then the counter is set back to 0
      # #this will continue until max hp is reached
        # print(self.movesSinceLastHit,'104')
        # print(settings.HP_REGEN_TIME)
        # print(self.regen_rate)
        # print(self.regen_amount)
        # if self.hp < self.max_hp:
            # if self.movesSinceLastHit >= (old_div(settings.HP_REGEN_TIME, self.regen_rate)):
                # self.heal(self.regen_amount)
                # self.movesSinceLastHit = 0
            # else:
                # self.movesSinceLastHit += 1
                # print(self.movesSinceLastHit,'114')
        # if self.movesSinceLastHit > 0 and self.take_damage(self.damage) > 0: #if fighter takes damage, movesSinceLastHit reverts to 0
            # self.movesSinceLastHit = 0
            # print(self.movesSinceLastHit,'line117')


def get_all_equipped(obj):
    #Return list of all equipped items
    if hasattr(obj, 'inventory'):
        equipped_list = []
        for item in obj.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []