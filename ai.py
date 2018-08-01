"""
AI routines, AI data, and monster death.
"""
import libtcodpy as libtcod

import log
from components import *
import actions

# Might make sense to have this defined
# in spells.py instead, dropping the
# default argument?
CONFUSE_NUM_TURNS = 10


class BasicMonsterMetadata:
    def __init__(self, target):
        self.target = target


def aggressive(monster, player, metadata):
    """
    A basic monster takes its turn. if you can see it, it can see you.
    """
    if libtcod.map_is_in_fov(monster.current_map.fov_map,
                             monster.x, monster.y):
        if monster.distance_to(metadata.target) >= 2:
            actions.move_towards(monster, metadata.target.pos)
        elif metadata.target.fighter.hp > 0:
            actions.attack(monster.fighter, metadata.target)


def stationary(monster, player, metadata):
    """
    Monster which does not move, but attacks when enemies are in range
    """
    if libtcod.map_is_in_fov(monster.current_map.fov_map,
                             monster.x, monster.y):
        if (metadata.target.fighter.hp > 0) and (monster.distance_to(metadata.target) == 1):
            actions.attack(monster.fighter, metadata.target)


class ConfusedMonsterMetadata:
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns


def random_direction():
    return algebra.directions[libtcod.random_get_int(0, 0, 7)]


def confused_monster(monster, player, metadata):
    if metadata.num_turns > 0:
        actions.move(monster, random_direction())
        metadata.num_turns -= 1
    else:
        # Restore the previous AI (this one will be deleted
        # because it's not referenced anymore)
        monster.ai = metadata.old_ai
        log.message(monster.name.capitalize() +
                    ' is no longer confused!', libtcod.red)


def monster_death(monster):
    # Transform it into a nasty corpse! it doesn't block, can't be
    # attacked, and doesn't move.
    log.message(
        'The ' + monster.name + ' dies! You gain ' +
        str(monster.fighter.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = monster.name + ' remains.'
    monster.current_map.objects.remove(monster)
    monster.current_map.objects.insert(0, monster)
