"""
Implementation of actions.
Includes those which might be used by the AI (movement and combat)
and those which are currently only offered to the player.
Magical effects and targeting (spells.py) could also live here.
Conditionals and interfaces for the player sit up top in roguelike.py.
"""
import libtcodpy as libtcod
import copy
from random import randint

from game_messages import Message
from components import Object
from render_functions import RenderOrder


def move(self, dx, dy, game_map):
    if not game_map.is_blocked(self.x, self.y + dy):
        self.y += dy
    if not game_map.is_blocked(self.x + dx, self.y):
        self.x += dx


def move_towards(self, target_x, target_y, game_map):
    dx = target_x - self.x
    dy = target_y - self.y
    if dx > 0:
        dx = 1
    if dx < 0:
        dx = -1
    if dy > 0:
        dy = 1
    if dy < 0:
        dy = -1
    self.move(dx, dy, game_map)


def move_astar(self, target, entities, game_map):
    # Create a FOV map that has the dimensions of the map
    fov = libtcod.map_new(game_map.width, game_map.height)

    # Scan the current map each turn and set all the walls as unwalkable
    for y1 in range(game_map.height):
        for x1 in range(game_map.width):
            libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                       not game_map.tiles[x1][y1].blocked)

    # Scan all the objects to see if there are objects that must be navigated around
    for entity in entities:
        if entity.blocks and entity != self and entity != target:
            # Set the tile as a wall so it must be navigated around
            libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

    # Allocate a A* path
    # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
    my_path = libtcod.path_new_using_map(fov, 1.41)

    # Compute the path between self's coordinates and the target's coordinates
    libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

    # Check if the path exists, and in this case, also the path is shorter than 25 tiles
    if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
        # Find the next coordinates in the computed full path
        x, y = libtcod.path_walk(my_path, True)
        if x or y:
            # Set self's coordinates to the next path tile
            self.x = x
            self.y = y
    else:
        # Keep the old move function as a backup so that if there are no paths
        move_towards(target.x, target.y, game_map)

        # Delete the path to free memory
    libtcod.path_delete(my_path)


def take_damage(self, amount):
    results = []

    self.hp -= amount

    if self.hp <= 0:
        self.hp = 0
        results.append({'dead': self.owner, 'xp': self.xp})

    return results


def heal(self, amount):
    self.hp += amount

    if self.hp > self.max_hp:
        self.hp = self.max_hp


def attack(fighter, target):
    results = []

    # Roll to see if hit
    attack_roll = randint(1, 20) + fighter.strength
    defence_roll = randint(1, 20) + target.fighter.agility

    if attack_roll > defence_roll:
        damage = fighter.damage
        if damage > 0:
            results.append({'message': Message('{0} attacks {1} for {2} hit points. ([{3} vs. {4}])'.format(
                fighter.owner.name.capitalize(), target.name, str(damage), attack_roll, defence_roll), libtcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage. ([{2} vs. {3}])'.format(
                fighter.owner.name.capitalize(), target.name, attack_roll, defence_roll), libtcod.grey)})
    else:
        results.append({'message': Message('{0} attacks {1} and misses. ([{2} vs. {3}])'.format(
            fighter.owner.name.capitalize(), target.name, attack_roll, defence_roll), libtcod.grey)})

    return results


def pick_up(actor, o, report=True):
    """
    Add an Object to the actor's inventory and remove from the map.
    """
    results = []

    for p in actor.inventory:
        if o.item.can_combine(p):
            p.item.count += o.item.count
            actor.current_map.objects.remove(o)
            if report:
                results.append({'message': Message('{0} picked up a {1}!'.format(
                                actor.name.capitalize(), o.name), libtcod.green)})
            return results

    if len(actor.inventory) >= 24:
        if report:
            results.append({'message': Message('{0}\'s inventory is full, cannot pick up {1}.'.format(
                            actor.name.capitalize(), o.name), libtcod.red)})
        return False
    else:
        actor.inventory.append(o)
        actor.current_map.objects.remove(o)
        if report:
            results.append({'message': Message('{0} picked up a {1}!'.format(
                            actor.name.capitalize(), o.name), libtcod.green)})

        # Special case: automatically equip if the corresponding equipment slot is unused.
        equipment = o.equipment
        if equipment and _get_equipped_in_slot(actor, equipment.slot) is None:
            equip(actor, equipment)
            if report:
                results.append({'message': Message('{0} equips the a {1}!'.format(
                    actor.name.capitalize(), o.name), libtcod.green)})
    return results


def drop(actor, o, report=True):
    """
    Remove an Object from the actor's inventory and add it to the map
    at the player's coordinates.
    If it's equipment, dequip before dropping.
    """
    results = []

    must_split = False
    if o.item.count > 1:
        o.item.count -= 1
        must_split = True
    else:
        if o.equipment:
            dequip(actor, o.equipment, True)
        actor.inventory.remove(o)

    combined = False
    for p in actor.inventory:
        if p.pos == actor.pos and o.item.can_combine(p):
            p.item.count += 1
            combined = True
            break

    if not combined:
        new_o = o
        if must_split:
            new_o = copy.deepcopy(o)
        new_o.item.count = 1
        new_o.pos = actor.pos
        actor.current_map.objects.append(new_o)

    if report:
        results.append({'message': Message('{0} drops a {1}.'.format(
            actor.name.capitalize(), o.name), libtcod.yellow)})


def use(actor, o, report=True):
    """
    If the object has the Equipment component, toggle equip/dequip.
    Otherwise invoke its use_function and (if not cancelled) destroy it.
    """
    results = []

    if o.equipment:
        _toggle_equip(actor, o.equipment, report)
        return
    if o.item.use_function is None:
        if report:
            results.append({'message': Message('The {0} cannot be used.'.format(
                o.name), libtcod.light_green)})
    else:
        if o.item.use_function(actor) != 'cancelled':
            if o.item.count > 1:
                o.item.count -= 1
            else:
                actor.inventory.remove(o)


def _toggle_equip(actor, eqp, report=True):
    if eqp.is_equipped:
        dequip(actor, eqp, report)
    else:
        equip(actor, eqp, report)


def equip(actor, eqp, report=True):
    """
    Equip the object (and log unless report=False).
    Ensure only one object per slot.
    """
    results = []

    old_equipment = _get_equipped_in_slot(actor, eqp.slot)
    if old_equipment is not None:
        dequip(actor, old_equipment, report)

    eqp.is_equipped = True
    if report:
        results.append({'message': Message('{0} equipped {1}.'.format(
            actor.name.capitalize(), eqp.owner.name), libtcod.light_green)})

    return results


def dequip(actor, eqp, report=True):
    """
    Dequip the object (and log).
    """
    results = []

    if not eqp.is_equipped:
        return
    eqp.is_equipped = False
    if report:
        results.append({'message': Message('{0} Dequipped {1}.'.format(
            actor.name.capitalize(), eqp.owner.name), libtcod.light_yellow)})

    return results


def _get_equipped_in_slot(actor, slot):
    """
    Returns Equipment in a slot, or None.
    """
    if hasattr(actor, 'inventory'):
        for obj in actor.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
    return None


def kill_monster(monster, entities):
    death_message = Message('The {0} dies!'.format(monster.name.capitalize()), libtcod.orange)

    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.char = ' '

    # Generate a corpse as an item
    if monster.name[0].lower() in 'aeiou':
        monster.corpse_name = 'An ' + monster.name + ' corpse'
    else:
        monster.corpse_name = 'A ' + monster.name + ' corpse'
    item_component = ()
    item = Object(monster.x, monster.y, '%', libtcod.dark_red, monster.corpse_name,
                  render_order=RenderOrder.ITEM, item=item_component)

    entities.remove(monster)
    entities.append(item)

    monster.render_order = RenderOrder.CORPSE

    return death_message
