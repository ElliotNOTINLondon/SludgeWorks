import libtcodpy as libtcod

import log
import algebra
from components import *
import actions
import map
import spells


def dagger():
    return Object(algebra.Location(0, 0), '-', 'dagger', libtcod.sky,
                  item=Item(description='A short blade ideal for swift stabbing attacks. ' +
                                        '+2 STR, [1d4]'),
                  equipment=Equipment(slot='main hand', strength_bonus=2, damage_dice=1, damage_sides=4))


def healing_potion(pos=algebra.Location(0, 0)):
    return Object(pos, '!', 'healing potion', libtcod.violet,
                  item=Item(use_function=spells.cast_heal,
                            description='A violet flask that you recognise to be a healing potion. This will help '
                                        'heal your wounds. ' + str(spells.HEAL_AMOUNT) + ' HP'))


def lightning_scroll(pos=algebra.Location(0, 0)):
    return Object(pos, '#', 'scroll of lightning bolt', libtcod.light_yellow,
                  item=Item(use_function=spells.cast_lightning,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, deals ' + str(spells.LIGHTNING_DAMAGE) + ' damage.'))


def fireball_scroll(pos=algebra.Location(0, 0)):
    return Object(pos, '#', 'scroll of fireball', libtcod.light_yellow,
                  item=Item(use_function=spells.cast_fireball,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, envelopes an area with fire, causing ' + str(spells.FIREBALL_DAMAGE) +
                            ' damage to on nearby creatures.'))


def confusion_scroll(pos=algebra.Location(0, 0)):
    return Object(pos, '#', 'scroll of confusion', libtcod.light_yellow,
                  item=Item(use_function=spells.cast_confuse,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, this scroll will cause an enemy to wander aimlessly for 10 turns.'))


def sword(pos=algebra.Location(0, 0)):
    return Object(pos, '/', 'sword', libtcod.sky,
                  item=Item(description='A rusted and dirt-caked longsword. It\'s fairly blunt, but much better than ' +
                                        'nothing. +3 STR [1d6]'),
                  equipment=Equipment(slot='right hand', strength_bonus=3, damage_dice=1, damage_sides=6))


def helm(pos=algebra.Location(0, 0)):
    return Object(pos, '^', 'helm', libtcod.darker_orange,
                  item=Item(description='A leather helmet designed to help minimise head wounds. +1 AGI'),
                  equipment=Equipment(slot='head', agility_bonus=1))


def shield(pos=algebra.Location(0, 0)):
    return Object(pos, '[', 'shield', libtcod.darker_orange,
                  item=Item(description='A small buckler that can be attached to the arm and used to deflect attacks. '
                            + '+1 AGI'),
                  equipment=Equipment(slot='left hand', defence_bonus=1))

