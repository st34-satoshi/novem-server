import asyncio
import json
import websockets
import logging
from room import Room
from player import Player


PLAYERS = {}  # {websocket: Player}
ROOMS = {}  # {room id: Room}


def action_event():
    # got an action
    return json.dumps({"next_state": "state"})


def room_response(room_id, player_type):
    return json.dumps({"action": "room_link", "room_id": room_id, "player_type": player_type})


def error_response():
    return json.dumps({"action": "error"})


async def notify_action():
    pass
    # # TODO:
    # if USERS:
    #     message = action_event()
    #     await asyncio.wait([user.send(message) for user in USERS])


async def send_error(websocket):
    await asyncio.wait([websocket.send(error_response())])


async def send_room_link(room_id, player_type, websocket):
    # type is Row, Column, or Viewer
    if player_type not in ["Row", "Column", "Viewer"]:
        logging.error(f"unexpected player type. {player_type}")
        await send_error(websocket)
        return
    message = room_response(room_id, player_type)
    await asyncio.wait([websocket.send(message)])


async def make_room(websocket, data):
    # handle data
    if "player_type" not in data:
        logging.error(f"No player_type in data when making room. {data}")
        await send_error(websocket)
        return
    player_type = data["player_type"]
    if "handicap" not in data:
        logging.error(f"No handicap in data when making room. {data}")
        await send_error(websocket)
        return
    player_handicap = data["handicap"]

    # make a room
    room = Room(len(ROOMS)+1, player_handicap)
    ROOMS[room.room_id] = room

    # send the link to the room to websocket player
    await send_room_link(room.room_id, player_type, websocket)


async def register(websocket):
    # TODO:
    print(f'add user {websocket}')
    print(f'number of users is {len(PLAYERS)}')
    PLAYERS[websocket] = Player(websocket)


async def unregister(websocket):
    print(f'add user {websocket}')
    print(f'number of users is {len(PLAYERS)}')
    if websocket not in PLAYERS:
        logging.error("No player ID when unregister.")
        return
    remove_player = PLAYERS.pop(websocket)
    remove_player.remove()


async def server(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(action_event())
        async for message in websocket:  # receive message
            data = json.loads(message)
            print(f'receive data = {data}')
            if 'action' not in data:
                logging.error(f"No action in request data. {data}")
                continue
            if data["action"] == "make-room":
                # TODO:
                await make_room(websocket, data)
            else:
                logging.error(f"Unexpected action request. {data}")
    finally:
        await unregister(websocket)


start_server = websockets.serve(server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()