import asyncio
import json
import logging
from room import Room
from player import Player
from player_type import PlayerType
import websockets
logging.basicConfig(level=logging.INFO)

PLAYERS = {}  # {websocket: Player}
ROOMS = {}  # {room id: Room}


def action_event():
    # got an action
    return json.dumps({"next_state": "state"})


def room_response(room_id, player_type):
    return json.dumps({"action": "room_link", "room_id": room_id, "player_type": player_type})


def room_list_response():
    message = {"action": "room_list"}
    for room in ROOMS.values():
        message[room.room_id] = room.information()
    return json.dumps(message)


def error_response(message=""):
    return json.dumps({"action": "error", "message": message})


async def send_error(websocket, message=""):
    await asyncio.wait([websocket.send(error_response(message))])


async def play_action(websocket, data):
    if "room_id" not in data:
        logging.error(f"No room id in data when next action. {data}")
        await send_error(websocket, "no room id")
        return
    room_id = data["room_id"]
    if "play_action" not in data:
        logging.error(f"No play action in data when next action. {data}")
        await send_error(websocket, "no play_action")
        return
    action = data["play_action"]

    if room_id not in ROOMS:
        await send_error(websocket, "room id is wrong")
        return
    room = ROOMS[room_id]
    if websocket not in PLAYERS:
        await send_error(websocket, "No player")
        logging.error("This player does not exist.")
        return
    player = PLAYERS[websocket]

    await room.next_action(player, action)


async def send_rooms_list(websocket=None):
    # Send the rooms list to all players
    # This is called when a room is created
    # If websocket is not None, send the information to the player
    message = room_list_response()
    if websocket is not None:
        await asyncio.wait([websocket.send(message)])
    else:
        await asyncio.wait([player.websocket.send(message) for player in PLAYERS])


async def make_room(websocket, data):
    # handle data
    if "player_type" not in data:
        logging.error(f"No player_type in data when making room. {data}")
        await send_error(websocket)
        return
    player_type = PlayerType(data["player_type"])
    if "handicap" not in data:
        logging.error(f"No handicap in data when making room. {data}")
        await send_error(websocket)
        return
    player_handicap = data["handicap"]
    if "name" not in data:
        logging.error(f"No name in data when making room. {data}")
        player_name = None
    else:
        player_name = data["name"]
    if websocket not in PLAYERS:
        logging.error(f"No player {websocket} when making room. {data}")
        await send_error(websocket)
        return
    player = PLAYERS[websocket]

    # set name
    if player_name is not None:
        if player_name == "None":  # None is not allowed
            player_name = "None1"
        player.name = player_name

    # make a room
    room = Room(str(len(ROOMS)+1), player_handicap)
    ROOMS[room.room_id] = room

    # add the player to the room
    ok = room.add_player(player, player_type)
    if not ok:
        send_error(websocket)
        return

    # Send the play information
    await room.send_playing()


async def join_room(websocket, data):
    # handle data
    if "player_type" not in data:
        logging.error(f"No player_type in data when joining room. {data}")
        await send_error(websocket)
        return
    player_type = PlayerType(data["player_type"])
    if "room_id" not in data:
        logging.error(f"No room id in data when joining room. {data}")
        await send_error(websocket)
        return
    room_id = data["room_id"]
    if "name" not in data:
        logging.error(f"No name in data when joining room. {data}")
        player_name = None
    else:
        player_name = data["name"]
    if websocket not in PLAYERS:
        logging.error(f"No player {websocket} when joining room. {data}")
        await send_error(websocket)
        return
    player = PLAYERS[websocket]

    # set name
    if player_name is not None:
        if player_name == "None":  # None is not allowed
            player_name = "None1"
        player.name = player_name

    if room_id not in ROOMS:
        logging.error(f"No room id in ROOMS when joining room. {data}")
        await send_error(websocket, "no room id in Rooms joining room")
        return
    room = ROOMS[room_id]

    # add the player to the room
    ok = room.add_player(player, player_type)
    if not ok:
        send_error(websocket, "This player cannot join the room.")
        return

    # Send the play information
    await room.send_playing()


async def register(websocket):
    PLAYERS[websocket] = Player(websocket)
    logging.info(f"add user {websocket}")


async def unregister(websocket):
    if websocket not in PLAYERS:
        logging.error("No player ID when unregister.")
        return
    remove_player = PLAYERS.pop(websocket)
    remove_player.remove()


async def server(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await send_rooms_list(websocket)  # send the information of rooms
        async for message in websocket:  # receive message
            data = json.loads(message)
            print(f'receive data = {data}')
            if 'action' not in data:
                logging.error(f"No action in request data. {data}")
                continue
            if data["action"] == "make-room":
                await make_room(websocket, data)
            elif data["action"] == "join-room":
                await join_room(websocket, data)
            elif data["action"] == "play-action":
                await play_action(websocket, data)
            else:
                logging.error(f"Unexpected action request. {data}")
    finally:
        await unregister(websocket)


start_server = websockets.serve(server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()