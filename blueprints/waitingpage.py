from flask import Blueprint, jsonify, render_template, request, redirect
from __init__ import games, players, game_codes
from objects.game import Game
from objects.player import Player

waiting_page = Blueprint('waiting_page', __name__, template_folder='templates')

@waiting_page.post("/createGame")
def create_game():

    data = request.json


    player = Player(data["name"], owner=True)

    game = Game(player)

    game_id = game.get_id()
    game_code = game.get_game_code()

    player_id = player.get_id()

    games[game_id] = game
    game_codes[game_code] = game_id
    players[player_id] = player

    url = "/waiting/" + player_id

    return_data = {
            "goto": url

        }

    print("Games list:", games)
    print("Players list:", players)
    
    return jsonify(return_data)




@waiting_page.post("/joinGame")
def join_game():
    data = request.json
    name = data["name"]

    if data["gamecode"] not in game_codes:
        return jsonify ({
            "gamefound": False,
            "message": "The gamecode you entered does not exist."
        })

    
    game_code = data["gamecode"]
    game_id = game_codes[game_code]
    game = games[game_id]

    if game.is_full():
        return jsonify ({
            "gamefound": False,
            "message": "The game you are trying to enter is full."
        })

    if name in game.get_player_names():
        return jsonify ({
            "gamefound": False,
            "message": "That name is already used in this game."
            })

    if game.has_started():
        return jsonify({
            "gamefound": False,
            "message": "The game you are trying to enter has already started."
        })
          

    player = Player(name)
    player_id = player.get_id()
    players[player_id] = player


    game.add_player(player)

    

    url = "/waiting/" + player_id

    print("Games list:", games)
    print("Players list:", players)

    
    return jsonify({
        "goto": url,
        "gamefound": True
    })




@waiting_page.route("/waiting/<player_id>")
def lobby(player_id):
    if player_id not in players:
        return redirect("/")
    player = players[player_id]
    game_id = player.get_game_id()
    game = games[game_id]
    game_owner = game.get_owner()

    if game.has_started():
        return redirect("/gamepage/"+player_id)

    if game_owner == player_id:


        data = {

            "player": player.get_private_waiting_room_data(),
            "game": game.get_waiting_room_data()

        }

        
        return render_template("owner_waiting_page.html", data=data)

    else:


        data = {

            "player": player.get_private_waiting_room_data(),
            "game": game.get_waiting_room_data()

        }


        
        return render_template("waiting_page.html", data=data)

