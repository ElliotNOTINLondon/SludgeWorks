import libtcodpy as libtcod

import spells
from components import Object, Item, Equipment
from render_functions import RenderOrder


# Consumables
def healing_potion(x=0, y=0):
    return Object(x, y, '!', 'healing potion', libtcod.violet, render_order=RenderOrder.ITEM,
                  item=Item(use_function=spells.cast_heal,
                            description='A violet flask that you recognise to be a healing potion. This will help '
                                        'heal your wounds. ' + str(spells.HEAL_AMOUNT) + ' HP'))


def lightning_scroll(x=0, y=0):
    return Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                  item=Item(use_function=spells.cast_lightning,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, deals ' + str(spells.LIGHTNING_DAMAGE) + ' damage.'))


def fireball_scroll(x=0, y=0):
    return Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                  item=Item(use_function=spells.cast_fireball,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, envelopes an area with fire, causing ' + str(spells.FIREBALL_DAMAGE) +
                            ' damage to on nearby creatures.'))


def confusion_scroll(x=0, y=0):
    return Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                  item=Item(use_function=spells.cast_confuse,
                            description='A scroll containing an ancient text that you somehow understand the meaning ' +
                            'of. When invoked, this scroll will cause an enemy to wander aimlessly for 10 turns.'))


# Equipment
def dagger():
    return Object(0, 0, '-', 'dagger', libtcod.sky,
                  item=Item(description='A short blade ideal for swift stabbing attacks. ' +
                                        '+2 STR, [1d4]'),
                  equipment=Equipment(slot='main hand', strength_bonus=2, damage_dice=1, damage_sides=4))


def sword(x=0, y=0):
    return Object(x, y, '/', 'sword', libtcod.sky, render_order=RenderOrder.ITEM,
                  item=Item(description='A rusted and dirt-caked longsword. It\'s fairly blunt, but much better than ' +
                                        'nothing. +3 STR [1d6]'),
                  equipment=Equipment(slot='right hand', strength_bonus=3, damage_dice=1, damage_sides=6))


def helm(x=0, y=0):
    return Object(x, y, '^', 'helm', libtcod.darker_orange, render_order=RenderOrder.ITEM,
                  item=Item(description='A leather helmet designed to help minimise head wounds. +1 AGI'),
                  equipment=Equipment(slot='head', agility_bonus=1))


def shield(x=0, y=0):
    return Object(x, y, '[', 'shield', libtcod.darker_orange, render_order=RenderOrder.ITEM,
                  item=Item(description='A small buckler that can be attached to the arm and used to deflect attacks. '
                            + '+1 AGI'),
                  equipment=Equipment(slot='left hand', defence_bonus=1))
