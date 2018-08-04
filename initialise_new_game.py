import libtcodpy as libtcod

import actions
import items
from inventory import Inventory
from components import Object, Fighter, Level
from game_messages import MessageLog
from game_states import GameStates
from game_map import GameMap
from render_functions import RenderOrder


def get_constants():
    window_title = 'sludgeWorks'

    screen_width = 80
    screen_height = 52

    bar_width = int(screen_width / 4)
    panel_height = round(screen_height / 8)
    panel_y = screen_height - panel_height

    message_x = int(bar_width + 2)
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = int(screen_width)
    map_height = int(screen_height - panel_height)

    room_max_size = map_width / 5
    room_min_size = map_width / 10
    max_rooms = 50

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 4
    max_items_per_room = 2

    colours = {
        'dark_wall': libtcod.dark_grey,
        'light_wall': libtcod.Color(150, 100, 50),
        'dark_ground': libtcod.black,
        'light_ground': libtcod.dark_grey,
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colours': colours
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(hp=100, xp=0,
                                damage_dice=1, damage_sides=2,
                                strength=1, agility=1, vitality=1, intellect=1, perception=1)
    inventory_component = Inventory(26)
    player = Object(0, 0, '@', 'Player', libtcod.white, blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component,)
    entities = [player]

    starting_weapon = items.dagger()
    player.level = Level()
    player.inventory.add_item(starting_weapon)
    actions._toggle_equip(player, starting_weapon)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
