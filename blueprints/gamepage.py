from flask import Blueprint, redirect, render_template
from __init__ import players, games


game_page = Blueprint("game_page", __name__, template_folder="templates", static_folder="static")


@game_page.get("/gamepage/<player_id>")
def gamepage(player_id):
    if player_id not in players:
        return redirect("/")

    player = players[player_id]
    game_id = player.get_game_id()
    game = games[game_id]

    if not game.has_started():
        return redirect("/waiting/" + player_id)


    data = {
        "game": game.get_game_data(),
        "player": player.get_private_game_data()
    }

    return render_template("game_page.html", data = data)

