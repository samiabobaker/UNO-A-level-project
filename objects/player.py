from secrets import token_hex
import constants

class Player:
    def __init__(self, name, owner=False):
        self._name = name
        self._is_owner = owner
        self._id = token_hex(16)
        self._game_id = None
        self._state = {
            "readyToPlay": False,
            "deck": None,
            "gameStarted": False,
            "gameWon": False,
            "isPlaying": False,
            "isDisconnected": False,
            "lastUno": None,
            "shouldHaveSaidUno": None,
            "punishedAlready": False
        }

    def get_deck(self):
        return self._state["deck"]
    
    def set_deck(self, deck):
        self._state["deck"] = deck

    def missed_an_uno(self):
        if self._state["punishedAlready"]:
            return False
        shouldHaveSaidUno = self._state["shouldHaveSaidUno"]
        lastUno = self._state["lastUno"]
        if shouldHaveSaidUno == None:
            return False
        if lastUno == None:
            self._state["punishedAlready"] = True
            return True
        if lastUno < shouldHaveSaidUno-1:
            self._state["punishedAlready"] = True
            return True
        return False

    def say_uno(self, round):
        self._state["lastUno"] = round

    def is_disconnected(self):
        return self._state["isDisconnected"]

    def disconnect(self):
        self._state["isDisconnected"] = True
        self._state["isPlaying"] = False

    def connect(self):
        self._state["isDisconnected"] = False
        self._state["isPlaying"] = True


    #Checks if the player is the current player
    def is_current_player(self):
        return self._state["uno"].get_current_player() == self.get_id()

    def is_owner(self):
        return self._is_owner

    def has_won(self):
        return self._state["gameWon"]


    def start(self, uno):
        self._state["gameStarted"] = True
        self._state["isPlaying"] = True
        self._state["uno"] = uno
        self._state["deck"] = uno.give_player_cards()

    def end_current_game(self):
        self._state["gameStarted"] = False
        self._state["isPlaying"] = False
        self._state["uno"] = None
        self._state["deck"] = None
        self._state["readyToPlay"] = False


    def is_playing(self):
        return self._state["isPlaying"]

    
    
    def get_card(self, index):
        card = self._state["deck"].get_card_with_index(index)
        return card

    def put_card_on(self, index, pile, current_turn):
        card = self._state["deck"].get_card_with_index(index)
        effects = card.get_effects(pile, self._state["deck"], current_turn)
        self._state["deck"].remove_card_with_index(index)
        if self._state["deck"].get_number_of_cards() == 1:
            self._state["shouldHaveSaidUno"] = current_turn["round"]
            self._state["punishedAlready"] = False
        pile.add_card(card)
        return effects

    def pick_up_card(self):
        card = self._state["uno"].give_card()
        self._state["deck"].add_card(card)

    def pick_up_card_until_colour(self, colour):
        last_colour = None
        while last_colour != colour:
            card = self._state["uno"].give_card()
            data = card.get_data()
            if "colour" in data:
                last_colour = data["colour"]
            self._state["deck"].add_card(card)


    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def set_game(self, game_id):
        self._game_id = game_id


    def get_game_id(self):
        return self._game_id


    def get_private_waiting_room_data(self):
        return {
                "name": self.get_name(),
                "id": self.get_id(),
                "readyToPlay": self.is_ready_to_play()
            }

    def get_public_waiting_room_data(self):
        return {
                "name": self.get_name(),
                "readyToPlay": self.is_ready_to_play()
            }

    def get_private_game_data(self):
        return {
            "name": self.get_name(),
            "id": self.get_id(),
            "owner": self.is_owner(),
            "cards": self.get_private_card_data(),
            "currentPlayer": self.is_current_player(),
            "gameWon": self.has_won()
        }

    def get_public_game_data(self):
        return {
            "name": self.get_name(),
            "cards": self.get_public_card_data(),
            "currentPlayer": self.is_current_player(),
            "gameWon": self.has_won()
        }


    def get_private_card_data(self):
        return self._state["deck"].get_private_card_data()

    def get_public_card_data(self):
        return self._state["deck"].get_public_card_data()

    def set_ready_to_play(self, ready_to_play):
        if ready_to_play == True or ready_to_play == False:
            self._state["readyToPlay"] = ready_to_play


    def is_ready_to_play(self):
        return self._state["readyToPlay"]

    def get_uno(self):
        return self._state["uno"]

    def should_win(self, current_turn):
        if self._state["deck"] == None:
            return False
        if self._state["deck"].is_empty() and not current_turn[constants.CHOOSE_COLOUR]:
            return True
        return False

    def win(self):
        self._state["gameWon"] = True
        self._state["isPlaying"] = False
