from flask_socketio import Namespace, emit,join_room
from flask import request
from __init__ import players, games


class GamePageNamespace(Namespace):

    session_ids = {}


    def update_clients(self, game_id):
        game = games[game_id]
        emit("updateGameState", game.get_game_data(), broadcast=True, namespace="/gamepage", room=game_id)

    def on_join(self, data):
        player_id = data["playerID"]

        if player_id not in players:
            emit("notInGame")
        else:
            player = players[player_id]
            game_id = player.get_game_id()
            game = games[game_id]
            
            if game.has_started():
                if player.is_disconnected() and not player.get_uno().has_won(): 
                    player.get_uno().connect_player(player_id)
                join_room(game_id)
            self.session_ids[request.sid] = player_id


    def on_disconnect(self):
        player_id = self.session_ids[request.sid]
        if player_id in players:
            player = players[player_id]
            uno = player.get_uno()
            game_id = player.get_game_id()
            game = games[game_id]
            game_owner_id = game.get_owner()
            if game_owner_id == player_id:
                uno.end_game()
                emit("goToWaitingPage", broadcast=True, namespace="/gamepage", room=game_id)
            else:
                uno.player_disconnected(player_id)
                if uno.game_ended():
                    emit("goToWaitingPage", broadcast=True, namespace="/gamepage", room=game_id)
                else:
                    self.update_clients(game_id)
        del self.session_ids[request.sid]

    def on_gameAction(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        game_id = player.get_game_id()
        if player.is_current_player():
            uno = player.get_uno()
            uno.invoke_action(data["action"])

        emit("updatePlayerState", player.get_private_game_data())

        self.update_clients(game_id)

    def on_endGame(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(player_id):
            uno = player.get_uno()
            if uno.has_won():
                uno.end_game()
                emit("goToWaitingPage", broadcast=True, namespace="/gamepage", room=game_id)

    def on_newGame(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.is_owner(player_id):
            uno = player.get_uno()
            if uno.has_won():
                uno.new_game()
                emit("goToWaitingPage", broadcast=True, namespace="/gamepage", room=game_id)

    def on_uno(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.has_started():
            uno = player.get_uno()
            uno.say_uno(player)
            emit("playerUno", player.get_name(), broadcast=True, namespace="/gamepage", room=game_id) 

    def on_reportUno(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        game_id = player.get_game_id()
        game = games[game_id]
        if game.has_started():
            uno = player.get_uno()
            uno.report_uno(data["report"])
            self.update_clients(game_id)

    def on_givePlayerState(self, data):
        player_id = data["playerID"]
        player = players[player_id]
        emit("updatePlayerState", player.get_private_game_data())         
            


