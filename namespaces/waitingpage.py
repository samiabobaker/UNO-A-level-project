from flask_socketio import Namespace, join_room, emit
from flask import request
from __init__ import players, games

class WaitingPageNamespace(Namespace):


    session_ids = {}

    #Sends  out an event to all players in the game of the game_id when a player has join or left
    def update_players_list(self, game_id):
        emit("updatePlayersList", games[game_id].get_waiting_room_data(), broadcast=True, namespace="/waitingpage", room=game_id)

    def update_options(self, game_id):
        print("Game options:", games[game_id].get_options())
        emit("updateOptions", games[game_id].get_options(), broadcast=True, namespace="/waitingpage", room=game_id)


    def on_join(self, data):
        player_id = data["playerID"]

        if player_id not in players:
            emit("notInGame")
        else:
            
            player = players[player_id]
            game_id = player.get_game_id()
            game = games[game_id]
            if not game.has_started():
                join_room(game_id)
                self.update_players_list(game_id)
            self.session_ids[request.sid] = player_id

    def on_disconnect(self):
        player_id = self.session_ids[request.sid]
        if player_id in players:
            player = players[player_id]
            game_id = player.get_game_id()
            game = games[game_id]
            game_owner_id = game.get_owner()

            if not game.has_started():
                game.remove_player(player_id)


                if game_owner_id == player_id:
                    game.end()
                    emit("gameEnded", broadcast=True, namespace="/waitingpage", room=game_id)
                else:
                    self.update_players_list(game_id)
        del self.session_ids[request.sid]

    def on_readyToPlay(self, data):
        player_id = data["playerID"]
        ready_to_play = data["readyToPlay"]
        player = players[player_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if not game.has_started():
            player.set_ready_to_play(ready_to_play)
            self.update_players_list(game_id)
            if game.is_ready_to_play():
                game.start()
                emit("gameStarted", broadcast = True, namespace = "/waitingpage", room=game_id)
                

    def on_kickPlayer(self, data):
        owner_id = data["playerID"]
        player_name = data["name"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            player_id = game.get_player_from_name(player_name)
            game.remove_player(player_id)
            self.update_players_list(game_id)

    def on_setMaxPlayers(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id)and not game.has_started():
            game.set_max_players(int(data["numOfPlayers"]))
            self.update_options(game_id)

    def on_setInitialNumberOfCards(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id)and not game.has_started():
            game.set_initial_number_of_cards(int(data["numOfCards"]))
            self.update_options(game_id)

    def on_setCanStack(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id)and not game.has_started():
            game.set_can_stack_specials(data["canStack"])
            self.update_options(game_id)

    def on_setCanRejoin(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_can_rejoin(data["canRejoin"])
            self.update_options(game_id)

    def on_setDirection(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_initial_direction(data["newDirection"])
            self.update_options(game_id)

    def on_setCanShuffleHands(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_customisable("shuffleHands", data["shuffleHands"])
            self.update_options(game_id)

    def on_setCanLastColour(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_customisable("lastColour", data["lastColour"])
            self.update_options(game_id)
    
    def on_setCanThreeCards(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_customisable("threeCards", data["threeCards"])
            self.update_options(game_id)
    
    def on_setCanSevenCards(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_customisable("sevenCards", data["sevenCards"])
            self.update_options(game_id)

    def on_setStartingPlayer(self, data):
        owner_id = data["playerID"]
        player = players[owner_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(owner_id) and not game.has_started():
            game.set_starting_player(data["startingPlayer"])
            self.update_options(game_id)

        
