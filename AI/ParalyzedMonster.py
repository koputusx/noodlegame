
import libtcodpy as libtcod
import message

class ParalyzedMonster:
    def __init__(self, old_ai, old_reflex, old_weapon_skill, 
                 old_move_probability, num_turns=10)
        self.old_ai = old_ai
        self.old_reflex = old_reflex
        self.old_weapon_skill = old_weapon_skill
        self.old_move_probability = old_move_probability
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #still paralyzed
            #print "before"
            #print self.num_turns
            #print self.owner.fighter.reflex
            #print self.owner.fighter.weapon_skill
            #monster is paralyzed and therefore can't do anything
            message.message('The ' + self.owner.name + ' is paralyzed!', libtcod.yellow)
            self.owner.fighter.reflex = 0
            #print "after"
            self.owner.fighter.weapon_skill = 0
            self.owner.fighter.move_probability = 0
            #print self.num_turns
            #print self.owner.fighter.reflex
            #print self.owner.fighter.weapon_skill
            self.num_turns -= 1

        else:  #restore previous AI (this one is deleted because reasons).
            self.owner.ai = self.old_ai
            self.owner.reflex = self.old_reflex
            self.owner.weapon_skill = self.old_weapon_skill
            self.owner.move_probability = self.old_move_probability
            message.message('The ' + self.owner.name + ' is no longer paralyzed!', libtcod.red)