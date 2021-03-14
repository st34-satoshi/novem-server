class Player:

    def __init__(self, websocket):
        self.websocket = websocket  # used for id
        self.rooms = set()  # room that this player join

    def remove(self):
        # remove this player
        pass
