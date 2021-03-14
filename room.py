class Room:

    def __init__(self, room_id, handicap=0):
        self.room_id = room_id
        self.players = {'row': None, 'column': None}
        self.handicap = handicap
