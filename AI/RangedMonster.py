from builtins import object
class RangedMonster(object):
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