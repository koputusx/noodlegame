import targeting
import settings
import color
from message import message

def cast_heal():
    if settings.player.fighter.hp == settings.player.fighter.max_hp:
        message('You are already at full health.', color.red)
        return 'cancel'
    
    message('Your wounds start to feel better.', color.light_violet)
    settings.player.fighter.heal(settings.HEAL_AMOUNT)

def cast_lightning():
    monster = targeting.closest_monster(settings.LIGHTNING_RANGE)
    if monster is None:
        message('No enemy is close enough to strike.', color.red)
        return 'cancelled'
    
    message('A lightning bolt strikes the ' + monster.name +
            ' with a loud thunder! the damage is ' +
            str(settings.LIGHTNING_DAMAGE) + ' hit points.',
            color.light_blue)
    monster.fighter.take_damage(settings.LIGHTNING_DAMAGE)
    
def cast_fireball():
    message('Left-click a target tile for the fireball,' +
            ' or right-click to cancel.', color.light_cyan)
    (x, y) = targeting.target_tile()
    if x is None:
        return 'cancelled'
    message('The fireball explodes, burning everything within ' +
            str(settings.FIREBALL_RADIUS) + ' tiles.', color.orange)
    
    for obj in settings.objects:
        if obj.distance(x, y) <= settings.FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' +
                    str(settings.FIREBALL_DAMAGE) +
                    ' hit points.', color.orange)
            obj.fighter.take_damage(settings.FIREBALL_DAMAGE)

def cast_acidball():
    message('Huge acid globe expands from your hand, ebgulfing everything within ' +
            str(settings.ACIDBALL_RADIUS) + ' tiles.', color.orange)
    
    for obj in settings.objects:
        if obj.distance_to(settings.player) <= settings.ACIDBALL_RADIUS and obj.fighter and obj.fighter != settings.player:
            message('The ' + obj.name + ' is burned by acid for ' +
                    str(settings.ACIDBALL_DAMAGE) +
                    ' hit points.', color.orange)
            obj.fighter.take_damage(settings.ACIDBALL_DAMAGE)


#def cast_frostbolt():
    ##this casts frostbolt, that damages everything on line between player and target tile
    #message('Left-click for target tile for the frostbolt, or right click to cancel.', color.light_cyan)
    #(x, y) targeting.target_tile()
    #if x is None:
        #return 'cancelled'
    #message('You cast the frostbolt, damaging everyone in range', color.orange)
    
    #for obj in settings.objects:
        #if obj.distance(x, y) <= settings.FROSTBOLT_RANGE and obj.fighter:
            #message()
            #obj.fighter.take_damage(settings.FROSTBOLT_DAMAGE)

def cast_magicmissile():
    #for now ask a player for target to destroy
    MAGICMISSILE_DAMAGE = settings.player.level ** settings.player.level
    message('Double left-click an enemy to hurt it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(MAGICMISSILE_RANGE)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The ' + monster.name + ' is hit by powerfull stream of energy for ' + str(MAGICMISSILE_DAMAGE) + ' hit points.', libtcod.pink) 
    monster.fighter.take_damage(MAGICMISSILE_DAMAGE)

def cast_confuse():
    from AI import ConfusedMonster
    monster = targeting.closest_monster(settings.CONFUSE_RANGE)
    message('Left-click an enemy to confuse it, or right-click to cancel.',
            color.light_cyan)
    monster = targeting.target_monster(settings.CONFUSE_RANGE)
    if monster is None:
        return 'cancelled'

    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster
    message('The eyes of the ' + monster.name +
            ' look vacant, as he starts to stumble around.',
            color.light_green)

#def cast_paralyze():
    #ask player for target to paralyze
    #from AI import ParalyzedMonster
    #message('Left-click on an enemy to paralyze it, or right-click to cancel it.', color.light_cyan)
    #monster = targeting.target_monster(settings.PARALYZE_RANGE)
    #if monster is None: return 'cancelled'

    #replace the monster's AI with paralyzed one
    #old_ai = monster.ai
    #old_reflex = monster.fighter.reflex
    #old_weapon_skill = monster.fighter.weapon_skill
    #old_move_probability = monster.fighter.move_probability
    #monster.ai = ParalyzedMonster(old_ai, old_reflex, old_weapon_skill, old_move_probability)
    #monster.ai.owner = monster #tell the new component who owns it.
    #message('The ' + monster.name + ' suddenly falls to the ground, unable to do anything!', libtcod.light_green)


def cast_self_destruct(self):
    x = self.owner.x
    y = self.owner.y
    for obj in settings.objects:
        if obj.distance(x, y) <= 2 and obj.fighter:
            message('The ' + obj.name + ' gets burned for 5 hit points.',
                    color.orange)
            obj.fighter.take_damage(5)

    if not self.owner.fighter:
        self.owner.char = '~'
        self.owner.color = color.darker_red
        self.owner.blocks = False
        self.owner.fighter = None
        self.owner.ai = None
        self.owner.name = 'Remains too destroyed to identify'