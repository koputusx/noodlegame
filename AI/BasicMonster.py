import libtcodpy as libtcod
import settings
from component import *

class BasicMonster(Component):

    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(settings.fov_map, monster.x, monster.y):
            if monster.distance_to(settings.player) >= 2:
                monster.move_towards_n(settings.player)

            elif monster.distance_to(settings.player) < 2 and settings.player.fighter.hp > 0: 
                monster.fighter.attack(settings.player)

#so I don't forget this
#class NormalMonster(BasicMonster):