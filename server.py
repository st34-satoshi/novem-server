import asyncio
import json
import websockets
from room import Room


USERS = set()
ROOMS = {}  # {room id: Room}


def action_event():
    # got an action
    return json.dumps({"next_state": "state"})


async def notify_action():
    # TODO:
    if USERS:
        message = action_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    # TODO:
    print(f'add user {websocket}')
    print(f'number of users is {len(USERS)}')
    USERS.add(websocket)


async def unregister(websocket):
    print(f'add user {websocket}')
    print(f'number of users is {len(USERS)}')
    USERS.remove(websocket)


async def server(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(action_event())
        async for message in websocket:  # receive message
            data = json.loads(message)
            print(f'receive data = {data}')
            # if data[""] == "":
            #     pass
            #     # await fun()
    finally:
        await unregister(websocket)


start_server = websockets.serve(server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()