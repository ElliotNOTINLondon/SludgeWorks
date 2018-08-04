import libtcodpy as libtcod
from random import randint

from ai import Aggressive, Stationary
from components import Fighter, Object
import items
from stairs import Stairs
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder

import algebra


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = algebra.Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break

            else:
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        print('Stairs placed')
        down_stairs = Object(center_of_last_room_x, center_of_last_room_y, '<', libtcod.white, 'Downward stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):
        max_plants_per_room = 0
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        # Get a random number of monsters
        number_of_plants = randint(0, max_plants_per_room)
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        loot_values = {
            # Consumables
            'healing_potion': items.healing_potion,
            'lightning_scroll': items.lightning_scroll,
            'fireball_scroll': items.fireball_scroll,
            'confusion_scroll': items.confusion_scroll,
            # Equipment
            'sword': items.sword,
            'helm': items.helm,
            'shield': items.shield
        }

        monster_chances = {
            'Wretch': 80,
            'Hunchback': from_dungeon_level([[10, 2], [25, 4], [80, 6], [40, 10]], self.dungeon_level),
            'Thresher': from_dungeon_level([[5, 4], [15, 6], [30, 8], [50, 10]], self.dungeon_level)
        }

        item_chances = {}
        # Consumables
        item_chances['healing_potion'] = 35
        item_chances['lightning_scroll'] = from_dungeon_level([[25, 4]], self.dungeon_level),
        item_chances['fireball_scroll'] = from_dungeon_level([[25, 6]], self.dungeon_level),
        item_chances['confusion_scroll'] = from_dungeon_level([[10, 2]], self.dungeon_level)
        # Equipment
        item_chances['sword'] = from_dungeon_level([[10, 0]], self.dungeon_level),
        item_chances['helm'] = from_dungeon_level([[5, 0], [10, 3]], self.dungeon_level),
        item_chances['shield'] = from_dungeon_level([[5, 3], [10, 6]], self.dungeon_level)

        # Item dictionary
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level([[10, 0]], self.dungeon_level),
            'helm': from_dungeon_level([[5, 0], [10, 3]], self.dungeon_level),
            'shield': from_dungeon_level([[5, 3], [10, 6]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        # Place stationary monsters (plants) independent of monster number
        for i in range(number_of_plants):
            # Choose a random location in the room around the edges
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                fighter_component = Fighter(hp=10, strength=3, agility=1, vitality=1, intellect=1, perception=1, xp=20)
                ai_component = Stationary()
                monster = Object(x, y, 'V', 'Whip Vine', libtcod.light_grey, render_order=RenderOrder.ACTOR,
                                 blocks=True, fighter=fighter_component, ai=ai_component)

                entities.append(monster)

        # Place monsters with random spawning chances
        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'Wretch':
                    fighter_component = Fighter(hp=10, xp=30,
                                                damage_dice=1, damage_sides=4,
                                                strength=4, agility=0, vitality=1, intellect=1, perception=1)
                    ai_component = Aggressive()
                    monster = Object(x, y, 'w', 'Wretch', libtcod.darker_red, render_order=RenderOrder.ACTOR,
                                     blocks=True, fighter=fighter_component, ai=ai_component)

                elif monster_choice == 'Hunchback':
                    fighter_component = Fighter(hp=20, xp=75,
                                                damage_dice=2, damage_sides=6,
                                                strength=7, agility=1, vitality=1, intellect=1, perception=1)
                    ai_component = Aggressive()
                    monster = Object(x, y, 'H', 'Hunchback', libtcod.brass, render_order=RenderOrder.ACTOR,
                                     blocks=True, fighter=fighter_component, ai=ai_component)

                elif monster_choice == 'Thresher':
                    fighter_component = Fighter(hp=50, xp=150,
                                                damage_dice=3, damage_sides=4,
                                                strength=5, agility=4, vitality=1, intellect=1, perception=1)
                    ai_component = Aggressive()
                    monster = Object(x, y, 'T', 'Thresher', libtcod.dark_azure, render_order=RenderOrder.ACTOR,
                                     blocks=True, fighter=fighter_component, ai=ai_component)

                entities.append(monster)

        # Place items
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                item = loot_values[item_choice](x=x, y=y)
                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

        # Heal on change of floors?
        # player.fighter.heal(player.fighter.max_hp // 2)

        return entities


class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        # Change this if you wish to see everything!
        self.explored = False
