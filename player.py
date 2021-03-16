class Player:

    def __init__(self, websocket):
        self.websocket = websocket  # used for id
        self.rooms = set()  # room that this player join
        self.name = "Player"

    def remove(self):
        # remove this player form all rooms
        for room in self.rooms:
            room.remove_player(self)

    def join_room(self, room_id):
        self.rooms.add(room_id)
