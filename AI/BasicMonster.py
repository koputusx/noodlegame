import libtcodpy as libtcod
import settings
import actions
from component import *

class BasicMonster(Component):

    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(settings.fov_map, monster.x, monster.y):
            if monster.distance_to(settings.player) > 1.5:
                actions.move_towards_n(monster, settings.player)

            elif monster.distance_to(settings.player) <= 1.5 and settings.player.fighter.hp > 0: 
                monster.fighter.attack_n(settings.player)

#so I don't forget this
#class NormalMonster(BasicMonster):
"""
TYPICAL AI
    if damage > morale:
        if can_run_away_from_player:
            run_away_from_player
        else if can_attack_player:
            attack_player
    elif too_far_from_player and can_attack_player and can_move_toward_player:
        if  random < charge_probability:
            move_toward_player
        else:
            attack_player
    elif too_close_to_character and can_attack_player and can_move_away_from_player:
        if random < retreat_probability:
            move_away_from_player
        else:
            attack_player
    elif can_attack_player:
        attack_player
    elif too_far_from_player and can_move_toward_player:
        move_toward_player
    elif too_close_to_player and can_move_away_from_player:
        move_away_from_player
    else stand_still
"""