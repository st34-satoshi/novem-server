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


def error_response(message=""):
    return json.dumps({"action": "error", "message": message})


async def notify_action():
    pass
    # # TODO:
    # if USERS:
    #     message = action_event()
    #     await asyncio.wait([user.send(message) for user in USERS])


async def send_error(websocket, message=""):
    await asyncio.wait([websocket.send(error_response(message))])


async def send_room_link(room_id, player_type, websocket):
    # type is Row, Column, or Viewer
    if player_type not in PlayerType:
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
    player_type = PlayerType(data["player_type"])
    if "handicap" not in data:
        logging.error(f"No handicap in data when making room. {data}")
        await send_error(websocket)
        return
    player_handicap = data["handicap"]
    if websocket not in PLAYERS:
        logging.error(f"No player {websocket} when making room. {data}")
        await send_error(websocket)
        return
    player = PLAYERS[websocket]

    # make a room
    room = Room(len(ROOMS)+1, player_handicap)
    ROOMS[room.room_id] = room

    # add the player to the room
    ok = room.add_player(player, player_type)
    if not ok:
        send_error(websocket)
        return

    # send the link to the room to websocket player
    await room.send_playing()
    # await send_room_link(room.room_id, player_type, websocket)


async def register(websocket):
    PLAYERS[websocket] = Player(websocket)
    logging.info(f"add user {websocket}")
    print("gg")


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
        await websocket.send(action_event())
        async for message in websocket:  # receive message
            data = json.loads(message)
            print(f'receive data = {data}')
            if 'action' not in data:
                logging.error(f"No action in request data. {data}")
                continue
            if data["action"] == "make-room":
                await make_room(websocket, data)
            else:
                logging.error(f"Unexpected action request. {data}")
    finally:
        await unregister(websocket)


start_server = websockets.serve(server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()