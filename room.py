from player_type import PlayerType
import logging
import asyncio
import json


class Room:

    def __init__(self, room_id, handicap=0):
        self.room_id = room_id
        self.players = {PlayerType.Row: None, PlayerType.Column: None, PlayerType.Viewer: []}  # Player class
        self.handicap = handicap

        # board information
        self.round = 0
        self.row_point = 0
        self.column_point = 0
        self.board_bottom = [[1, 5, 9], [6, 7, 2], [8, 3, 4]]
        self.board_top = [[9, 5, 1], [4, 3, 8], [2, 7, 6]]

    def information(self):
        # Used for the information of room list in the Home View
        ans = {"room_id": self.room_id, "Row": self.row_name(), "Column": self.column_name(), "Round": self.round}
        return ans

    def add_player(self, player, player_type):
        if player_type == PlayerType.Viewer:
            self.players[PlayerType.Viewer].append(player)
        elif self.players[player_type] is None:
            self.players[player_type] = player
        else:
            # player already exists
            logging.info(f"{player_type} already exists. "
                         f"The player can not join this room. {player.websocket}, {self.room_id}")
            return False
        player.join_room(self.room_id)
        return True

    def all_players(self):
        players = self.players[PlayerType.Viewer]
        if self.players[PlayerType.Row] is not None:
            players.append(self.players[PlayerType.Row])
        if self.players[PlayerType.Column] is not None:
            players.append(self.players[PlayerType.Column])
        return players

    def board_information(self):
        # board --> string. bottom top left --> right, down
        # Initial board is 159672834951438276
        board_info = ""
        for row in self.board_bottom:
            for n in row:
                board_info += str(n)
        for row in self.board_top:
            for n in row:
                board_info += str(n)
        return board_info

    def row_name(self):
        if self.players[PlayerType.Row] is not None:
            return self.players[PlayerType.Row].name
        return "None"

    def column_name(self):
        if self.players[PlayerType.Column] is not None:
            return self.players[PlayerType.Column].name
        return "None"

    def playing_information(self):
        # Information: room id, board, round, point, and player name.
        return json.dumps({"action": "playing",
                           "room_id": self.room_id,
                           "board": self.board_information(),
                           "round": self.round,
                           "row_point": self.row_point,
                           "column_point": self.column_point,
                           "row_name": self.row_name(),
                           "column_name": self.column_name()})

    async def send_playing(self):
        # Send all information of this state to all players in this room.
        # Information: room id, board, round, point, and player name.
        message = self.playing_information()
        await asyncio.wait([player.websocket.send(message) for player in self.all_players()])
