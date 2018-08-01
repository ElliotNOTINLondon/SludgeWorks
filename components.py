"""
Simple entity system: any renderable Object can have
a number of Components attached.
"""
import math


class Object:
    """
    This is a generic object: the player, a monster, an item, the stairs...
    It's always represented by a character on screen.
    """
    def __init__(self, pos, char, name, color,
                 blocks=False, always_visible=False,
                 fighter=None, ai=None, item=None, equipment=None):
        self.pos = pos
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible

        self.fighter = fighter
        self._ensure_ownership(fighter)
        self.ai = ai
        self._ensure_ownership(ai)
        self.item = item
        self._ensure_ownership(item)
        self.equipment = equipment
        self._ensure_ownership(equipment)

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    def _ensure_ownership(self, component):
        if (component):
            component.set_owner(self)

    def distance_to(self, other):
        """
        Return the distance to another object.
        """
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        """
        Return the distance to some coordinates.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance(self, pos):
        """
        Return the distance to some coordinates.
        """
        return math.sqrt((pos.x - self.x) ** 2 + (pos.y - self.y) ** 2)


class Component:
    """
    Base class for components to minimize boilerplate.
    """
    def set_owner(self, entity):
        self.owner = entity


class Fighter(Component):
    """
    Combat-related properties and methods (monster, player, NPC).
    """
    def __init__(self, hp, xp,
                 damage_dice, damage_sides,
                 strength, agility, vitality, intellect, perception, death_function=None,):
        self.base_max_hp = hp
        self.hp = hp
        self.xp = xp
        self.base_damage_dice = damage_dice
        self.base_damage_sides = damage_sides
        self.death_function = death_function
        self.base_strength = strength
        self.base_agility = agility
        self.base_vitality = vitality
        self.base_intellect = intellect
        self.base_perception = perception

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    @property
    def strength(self):
        bonus = sum(equipment.strength_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_strength + bonus

    @property
    def agility(self):
        bonus = sum(equipment.agility_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_agility + bonus

    @property
    def vitality(self):
        bonus = sum(equipment.vitality_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_vitality + bonus

    @property
    def intellect(self):
        bonus = sum(equipment.intellect_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_intellect + bonus

    @property
    def perception(self):
        bonus = sum(equipment.perception_bonus for equipment
                    in _get_all_equipped(self.owner))
        return self.base_perception + bonus


class Item(Component):
    """
    An item that can be picked up and used.
    """
    def __init__(self, description=None, count=1, use_function=None):
        self.description = description
        self.use_function = use_function
        self.count = count

    def can_combine(self, other):
        """
        Returns true if other can stack with self.
        Terribly simple for now.
        """
        return other.item and other.name == self.owner.name


class Equipment(Component):
    """
    An object that can be equipped, yielding bonuses.
    Requires an Item component.
    """
    def __init__(self, slot, damage_dice=0, damage_sides=0, max_hp_bonus=0,
                 strength_bonus=0, agility_bonus=0, vitality_bonus=0, intellect_bonus=0, perception_bonus=0):
        self.slot = slot
        self.damage_dice = damage_dice
        self.damage_sides = damage_sides
        self.max_hp_bonus = max_hp_bonus
        self.strength_bonus = strength_bonus
        self.agility_bonus = agility_bonus
        self.vitality_bonus = vitality_bonus
        self.intellect_bonus = intellect_bonus
        self.perception_bonus = perception_bonus
        self.is_equipped = False

    def set_owner(self, entity):
        Component.set_owner(self, entity)

        # There must be an Item component for the Equipment
        # component to work properly.
        if entity.item is None:
            entity.item = Item()
            entity.item.set_owner(entity)


class AI(Component):
    def __init__(self, take_turn, metadata=None):
        self._turn_function = take_turn
        self._metadata = metadata

    def take_turn(self, player):
        self._turn_function(self.owner, player, self._metadata)


def _get_all_equipped(obj):
    """
    Returns a list of all equipped items.
    """
    if hasattr(obj, 'inventory'):
        equipped_list = []
        for item in obj.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []
