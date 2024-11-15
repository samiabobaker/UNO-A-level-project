from secrets import token_hex
from __init__ import players, games, game_codes
from objects.uno import UNO
import constants

class Game:


    

    def __init__(self, owner):
        self._players = {}
        self._player_names = {}
        self._owner = owner    
        self._game_code = token_hex(4)
        self._id = token_hex(16)
        self._options = {
            "maxPlayers": 4,
            "startingPlayer": self._owner,
            "initialNumberOfCards":7,
            "initialDirection": constants.CLOCKWISE,
            "canStackSpecials":True,
            "canRejoin":True,
            "customisableCards": {
                "shuffleHands": False,
                "lastColour": False,
                "threeCards": False,
                "sevenCards": False
            }
        }
        self._state = {
            "gameStarted": False,
            "gameEnded": False,
            "uno": None
        }
        self.add_player(owner)


    def is_owner(self, id):
        if self.get_owner() == id:
            return True
        else:
            return False

    def get_options(self):
        return {
            "maxPlayers": self.get_max_players(),
            "startingPlayer": self.get_starting_player(),
            "initialNumberOfCards": self.get_initial_number_of_cards(),
            "initialDirection": self.get_initial_direction().capitalize(),
            "canStackSpecials": self.can_stack_specials(),
            "canRejoin": self.can_rejoin(),
            "customisableCards": self.get_customisable()

        }

    def get_starting_player(self):
        return self._options["startingPlayer"].get_name()


    def set_starting_player(self, name):
        if name in self.get_player_names():
            player_id = self.get_player_from_name(name)
            self._options["startingPlayer"] = self._players[player_id]

    #Returns a list of the customisable cards in the game.
    def get_customisable(self):
        c = self.get_customisable_dict()
        return [p for p in c if c[p]]

    def get_customisable_dict(self):
        return self._options["customisableCards"]

    def set_customisable(self, card, in_game):
        if card in self.get_customisable_dict() and type(in_game) == bool:
            self._options["customisableCards"][card] = in_game

    def get_initial_direction(self):
        return self._options["initialDirection"]

    def set_initial_direction(self, direction):
        if direction == constants.CLOCKWISE or direction == constants.ANTICLOCKWISE:
            self._options["initialDirection"] = direction

    def can_stack_specials(self):
        return self._options["canStackSpecials"]

    def set_can_stack_specials(self, can_stack):
        if type(can_stack) == bool:
            self._options["canStackSpecials"] = can_stack


    def can_rejoin(self):
        return self._options["canRejoin"]

    def set_can_rejoin(self, can_rejoin):
        if type(can_rejoin) == bool:
            self._options["canRejoin"] = can_rejoin


    def add_player(self, player):
        if not self.is_full():
            player.set_game(self._id)
            player_id = player.get_id()
            player_name = player.get_name()
            self._players[player_id] = player
            self._player_names[player_name] = player_id
        
            return player_id, player
        else:
            return False #Returns false if the game is full

    def set_max_players(self, max_players):
        if type(max_players) == int and self.get_number_of_players() <= min(10, max_players):
            self._options["maxPlayers"] = max_players

    def get_max_players(self):
        return self._options["maxPlayers"]

    def set_initial_number_of_cards(self, cards):
        if type(cards == int) and cards>=2 and cards <= 7:
            self._options["initialNumberOfCards"] = cards

    def get_initial_number_of_cards(self):
        return self._options["initialNumberOfCards"]

    def get_player_names(self):
        return self._player_names.keys()

    def remove_player(self, player_id):
        player_name = self._players[player_id].get_name()
        if self.is_owner(player_id) and not self.has_ended():
            self.end()
        else:
            del self._players[player_id]
            del players[player_id]
            del self._player_names[player_name]

    def get_number_of_players(self):
        return len(self._players)

    def is_full(self):
        return self.get_number_of_players() >= self.get_max_players()



    def get_players(self):
        return self._players

    #Gets the waiting room data for each player in the game
    def get_players_waiting_room_data(self):
        return [p.get_public_waiting_room_data() for p in self.get_players().values()]

    def get_owner(self):
        return self._owner.get_id()

    def get_id(self):
        return self._id

    def get_player_ids(self):
        return list(self._players.keys())

    def get_game_code(self):
        return self._game_code


    def get_waiting_room_data(self):
        return {
                "gamecode": self.get_game_code(),
                "players": self.get_players_waiting_room_data(),
                "options": self.get_options()
            }

    def get_player_from_name(self, name):
        return self._player_names[name]

    def get_player_name(self, id):
        if id in self.get_player_ids():
            return self.get_players()[id].get_name

    def is_ready_to_play(self):
        ready_to_play = True

        if self.get_number_of_players() < 2:
            return False

        for p in self.get_players().values():
                if not p.is_ready_to_play():
                    ready_to_play = False

        return ready_to_play

    def start(self):
        if self.has_started():
            return
        self._state["gameStarted"] = True
        self._state["uno"] = UNO(self.get_id(), self._options, list(self.get_players().values())) #Creates uno object passing in id, options and list of player objects
        for player in self.get_players().values():
            player.start(self._state["uno"])

    def return_to_waiting_room(self):
        if self.has_started():
            self._state["gameStarted"] = False
            self._state["uno"] = None
        for player in self.get_players().values():
            player.end_current_game()


    def end(self):
        if not self.has_ended():
            self._state["gameEnded"] = True
            player_ids = self.get_player_ids()
            for p in player_ids:
                self.remove_player(p)
            del game_codes[self._game_code]
            del games[self._id]

    def has_ended(self):
        return self._state["gameEnded"]

    def has_started(self):
        return self._state["gameStarted"]

    def get_game_data(self):
        return {
            "id": self.get_id(),
            "players": self.get_players_game_data(),
            "topcard": self._state["uno"].get_top_card().get_data(),
            "currentTurn": self._state["uno"].get_current_turn()
        }

    def get_players_game_data(self):
        return [p.get_public_game_data() for p in self.get_players().values()]
