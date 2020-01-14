from builtins import object
import libtcodpy as libtcod
import message

class SleepyMonster(object):

    def __init__(self, old_ai, num_turns=10):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #how to tell monster to wake up in case of damage?
            pass
        else:
            self.owner.ai = self.old_ai
            message.message('The ' + self.owner.name +
                            ' has waken up from sleep.', libtcod.red)