from objects.deck import Deck
from objects.pile import Pile
from objects.effects import Effect,ChangePropertyEffect,AddPenaltyEffect
from __init__ import games, players

import constants

class UNO:



    def __init__(self, game_id, options, players):
        self._game_id = game_id
        self._options = options
        self._players = players
        self._current_turn = {
            constants.MODE: constants.PASSIVE,
            constants.PENALTY: 0,
            "canStackSpecials": self._options["canStackSpecials"],
            "currentPlayer": self._players.index(self._options["startingPlayer"]), #Points to the index of the current player (initially the starting player)
            "playing": len(self._players),
            constants.DIRECTION: 1 if self._options["initialDirection"] == constants.CLOCKWISE else -1, #1 if clockwise, -1 if anticlockwise
            constants.SKIPPABLE: False,
            constants.STACK_BY_NUMBER: False,
            constants.CAN_PICK_UP: True,
            constants.COLOURED_ONLY: False,
            constants.CHOOSE_COLOUR: False,
            "winners": [],
            "won": False,
            "gameEnded": False,
            "round": 0
        }
        print(self._options["customisableCards"])
        self._deck = Deck(self._options["customisableCards"])
        self._pile = Pile()
        top_card = self._deck.generate_random_standard_card()
        self._pile.add_card(top_card)

    def game_ended(self):
        return self._current_turn["gameEnded"]

    def player_disconnected(self, player_id):
        if not self._options["canRejoin"]:
            self.remove_player(player_id)
        else:
            self.disconnect_player(player_id)

    def disconnect_player(self, player_id):
            player = players[player_id]
            current_player = self._players[self._current_turn["currentPlayer"]]
            if current_player == player:
                self.next_go()
            player.disconnect()
            self._current_turn["playing"] -= 1
            if self._current_turn["playing"] <= 1:
                self.end_game()

    def connect_player(self, player_id):
            player = players[player_id]
            player.connect()
            self._current_turn["playing"] += 1

    def remove_player(self, player_id):
        player = players[player_id]
        current_player = self._players[self._current_turn["currentPlayer"]]
        if current_player == player:
            self.next_go()
        current_player = self._players[self._current_turn["currentPlayer"]]
        if player in self._players:
            game = games[self._game_id]
            game.remove_player(player_id)
            self._current_turn["playing"] -= 1
            self._players.remove(player)
            self._players.index(current_player)
            if self._current_turn["playing"] <= 1:
                self.end_game()

    def invoke_action(self, action):
        current_player = self.get_current_player()
        player = self._players[self._current_turn["currentPlayer"]]
        if action["player"] == current_player:
            effects = self.execute_action(action)
            if player.should_win(self._current_turn):
                player.win()
                if player.get_name() not in self._current_turn["winners"]:
                    self._current_turn["winners"].append(player.get_name())
                self._current_turn["playing"] -= 1
                if self._current_turn["playing"] < 2:
                    self.win()
            successful = True
            for effect in effects:
                if effect.get_type() == constants.ACTION_FAILED:
                    successful = False
                self.execute_effect(effect)
            if successful:
                self._current_turn["round"] += 1
            if self._current_turn[constants.MODE] == constants.ATTACKING:
                if self._current_turn["canStackSpecials"] == False:
                    self._current_turn[constants.MODE] = constants.PUNISHING

    def say_uno(self, player):
        player.say_uno(self._current_turn["round"])

    def pick_up_or_withdraw(self, player, number):
        change = player.get_public_card_data()["number"] - number
        if change <= 0:
            for i in range(-change):
                player.pick_up_card()
        else:
            for i in range(change):
                player.put_card_on(0, self._pile, self._current_turn)

    def report_uno(self, player_index):
        player = self._players[player_index]
        if player.missed_an_uno() and player.is_playing():
            player.pick_up_card()
            player.pick_up_card()
                

    def execute_effect(self, effect):
        effect_type = effect.get_type()
        match effect_type:
            case constants.NEXT_GO:
                self.next_go()
            case constants.CHANGE_PROPERTY:
                property = effect.get_property()
                new_value = effect.get_new()
                self._current_turn[property] = new_value
            case constants.ADD_PENALTY:
                penalty = effect.get_penalty()
                self._current_turn[constants.PENALTY] += penalty
            case constants.CHECK_TO_PUNISH:
                if self._current_turn[constants.PENALTY] == 0:
                    self._current_turn[constants.MODE] = constants.PASSIVE
                    self.next_go()
            case constants.REVERSE:
                self.reverse()
            case constants.PICK_UP_OR_WITHDRAW:
                number = effect.get_number()
                for p in self._players:
                    if p.is_playing():
                        self.pick_up_or_withdraw(p, number)
            case constants.PICK_UP_UNTIL_COLOUR:
                colour = effect.get_colour()
                player = self._players[self._current_turn["currentPlayer"]]
                player.pick_up_card_until_colour(colour)
            case constants.SHUFFLE_HANDS:
                self.shuffle_hands()


    

    def execute_action(self, action):

        if not self.action_fits_game_restrictions(action):
            return (Effect(constants.ACTION_FAILED),)
        
        if action["type"] == constants.PLACE_DOWN_CARD:
            return self.place_down_card(action["index"])
        elif action["type"] == constants.PICK_UP_CARD:
            return self.pick_up_card()
        elif action["type"] == constants.CHOOSE_COLOUR:
            return self.choose_colour(action["colour"])
        elif action["type"] == constants.SKIP:
            return self.skip_go()
        

    def win(self):
        self.next_go()
        player = self._players[self._current_turn["currentPlayer"]]
        self._current_turn["winners"].append(player.get_name())
        self._current_turn["won"] = True

    def has_won(self):
        return self._current_turn["won"]

    def end_game(self):
        self._current_turn["gameEnded"] = True
        
        
        game = games[self._game_id]

        game.end()


    def new_game(self):
        self._current_turn["gameEnded"] = True

        game = games[self._game_id]
        game.return_to_waiting_room()

        


        
    def choose_colour(self, colour):
        self._pile.set_top_colour(colour)
        return (
            ChangePropertyEffect(constants.CHOOSE_COLOUR, False),
            ChangePropertyEffect(constants.CAN_PICK_UP, True),
            ChangePropertyEffect(constants.COLOURED_ONLY, False),
            Effect(constants.NEXT_GO)
        )

    def skip_go(self):
        if self._current_turn[constants.SKIPPABLE]:
            return (
                Effect(constants.NEXT_GO), 
                ChangePropertyEffect(constants.SKIPPABLE, False), 
                ChangePropertyEffect(constants.STACK_BY_NUMBER, False), 
                ChangePropertyEffect(constants.CAN_PICK_UP, True)
            )
        else:
            return (Effect(constants.ACTION_FAILED),)

    def reverse(self):
        self._current_turn[constants.DIRECTION] *= -1
        if (self._current_turn["playing"] > 2) or self._current_turn[constants.MODE] == constants.ATTACKING:
            self.next_go()

    def shuffle_hands(self):
        players = self.get_playing_players()
        decks = [player.get_deck() for player in players]
        for i in range(len(players)):
            player_index = (i + self._current_turn[constants.DIRECTION]) % len(players) 
            player = players[player_index]
            player.set_deck(decks[i])


    def get_playing_players(self):
        players =  []
        for player in self._players:
            if player.is_playing():
                players.append(player)
        return players





    #Called when the player chooses to place down a card
    def place_down_card(self, index):
        player = self._players[self._current_turn["currentPlayer"]]
        card = player.get_card(index)
        top_card = self._pile.get_top_card()
        if card.can_be_put_on(self._current_turn, top_card) and self.card_fits_game_restrictions(card):
            effects = player.put_card_on(index, self._pile, self._current_turn)
            return effects
        return (Effect(constants.ACTION_FAILED),)


    #Called when the player has to pick up a card because they have no cards to put down
    def pick_up_card(self):
        if self._current_turn[constants.MODE] == constants.ATTACKING:
            player = self._players[self._current_turn["currentPlayer"]]
            player.pick_up_card()
            return (
                ChangePropertyEffect(constants.MODE, constants.PUNISHING),
                AddPenaltyEffect(-1)
            )
        if self._current_turn[constants.MODE] == constants.PUNISHING:
            player = self._players[self._current_turn["currentPlayer"]]
            player.pick_up_card()
            return (
                AddPenaltyEffect(-1),
                Effect(constants.CHECK_TO_PUNISH)
            )
        if self._current_turn[constants.CAN_PICK_UP]:
            player = self._players[self._current_turn["currentPlayer"]]
            player.pick_up_card()
            return (Effect(constants.NEXT_GO),)
        else:
            return (Effect(constants.ACTION_FAILED),)

    #Checks if the action fits the current restrictions of the state of the game right now.
    def action_fits_game_restrictions(self, action):
        if self._current_turn[constants.MODE] == constants.PUNISHING and action["type"] != constants.PICK_UP_CARD:
            return False
        if self._current_turn[constants.CHOOSE_COLOUR] and action["type"] != constants.CHOOSE_COLOUR:
            return False
        if not self._current_turn[constants.CHOOSE_COLOUR] and action["type"] == constants.CHOOSE_COLOUR:
            return False
        if self._current_turn["won"]:
            return False
        return True


    #Checks if the card fits the current restrictions of the state of the game right now.
    def card_fits_game_restrictions(self, card):
        card_data = card.get_data()
        if self._current_turn[constants.COLOURED_ONLY] and ("colour" not in card_data):
            return False
        if self._current_turn[constants.STACK_BY_NUMBER]:
            if "number" not in card_data:
                return False
            if card_data["number"] != self._pile.get_top_card().get_data()["number"]:
                return False
        return True

    def get_current_player(self):
        return self._players[self._current_turn["currentPlayer"]].get_id()

    #Loops round the players in the direction of self._direction
    def next_go(self):
        self._current_turn["currentPlayer"] = (self._current_turn["currentPlayer"] + self._current_turn[constants.DIRECTION]) % (len(self._players))
        while not self._players[self._current_turn["currentPlayer"]].is_playing():
            self._current_turn["currentPlayer"] = (self._current_turn["currentPlayer"] + self._current_turn[constants.DIRECTION]) % (len(self._players))


    def get_top_card(self):
        return self._pile.get_top_card()

    def give_player_cards(self):
        return self._deck.give_player_cards(self._options["initialNumberOfCards"])

    def give_card(self):
        return self._deck.generate_random_card()

    def get_current_turn(self):
        return self._current_turn
