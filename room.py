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
        self.row_point = int(handicap)
        self.column_point = 0
        self.board_bottom = [[1, 5, 9], [6, 7, 2], [8, 3, 4]]
        self.board_top = [[9, 5, 1], [4, 3, 8], [2, 7, 6]]

        # next action. action is 0, 1, or 2. This is the index.
        self.row_action = None
        self.column_action = None

    def remove_player(self, player):
        if self.players[PlayerType.Row] is player:
            self.players[PlayerType.Row] = None
        if self.players[PlayerType.Column] is player:
            self.players[PlayerType.Column] = None
        if player in self.players[PlayerType.Viewer]:
            self.players[PlayerType.Viewer].remove(player)

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
        player.join_room(self)
        return True

    def all_players(self):
        players = []
        for player in self.players[PlayerType.Viewer]:
            players.append(player)
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

    def playing_information(self, player_type):
        # Information: room id, board, round, point, and player name.
        return json.dumps({"action": "playing",
                           "room_id": self.room_id,
                           "board": self.board_information(),
                           "round": self.round,
                           "row_point": self.row_point,
                           "column_point": self.column_point,
                           "row_name": self.row_name(),
                           "column_name": self.column_name(),
                           "type": player_type})

    async def send_playing(self):
        # Send all information of this state to all players in this room.
        # Information: room id, board, round, point, and player name.
        if self.players[PlayerType.Row] is not None:
            await asyncio.wait([self.players[PlayerType.Row].websocket.send(self.playing_information("Row"))])
        if self.players[PlayerType.Column] is not None:
            await asyncio.wait([self.players[PlayerType.Column].websocket.send(self.playing_information("Column"))])
        message = self.playing_information("Viewer")
        if len(self.players[PlayerType.Viewer]) > 0:
            await asyncio.wait([player.websocket.send(message) for player in self.players[PlayerType.Viewer]])

    async def next_action(self, player, action):
        """
        :param player:
        :param action: r3, r2, ..., c1.
        :return:
        If correct player, correct action --> set this action
        else --> ignore
        When both Row and Column actions are decided --> move to next state and broadcast
        """
        if len(action) != 2:
            return
        # check player
        if action[0] == 'r':
            if self.players[PlayerType.Row] is not player:
                return
        elif action[0] == 'c':
            if self.players[PlayerType.Column] is not player:
                return
        else:
            return
        # player is correct

        # check action
        if action[1] not in ["1", "2", "3"]:
            return
        # action is correct

        # set the action
        if action[0] == "r":
            self.row_action = int(action[1]) - 1
        else:
            self.column_action = int(action[1]) - 1

        # move to next state and broadcast
        if self.row_action is not None and self.column_action is not None:
            # update the board
            tile = 0
            if self.board_top[self.row_action][self.column_action] != 0:
                tile = self.board_top[self.row_action][self.column_action]
                self.board_top[self.row_action][self.column_action] = 0
            elif self.board_bottom[self.row_action][self.column_action] != 0:
                tile = self.board_bottom[self.row_action][self.column_action]
                self.board_bottom[self.row_action][self.column_action] = 0
            # update the point
            if self.round % 2 == 0:
                self.row_point += tile
            else:
                self.column_point += tile
            # update the round
            self.round += 1
            # reset next action
            self.row_action = None
            self.column_action = None
            # broadcast
            await self.send_playing()
