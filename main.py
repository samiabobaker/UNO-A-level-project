from flask import Flask, render_template
from flask_socketio import SocketIO
from blueprints.waitingpage import waiting_page
from blueprints.gamepage import game_page
from namespaces.waitingpage import WaitingPageNamespace
from namespaces.gamepage import GamePageNamespace
from objects.deck import Deck 



#Generates json file storing types of each card
Deck.generate_deck_file()


app = Flask (__name__)
socketio = SocketIO(app, static_folder="static", template_folder = "templates")


@app.route("/")
def starting_page():
    return render_template("starting_page.html")


#Connect blueprints
app.register_blueprint(waiting_page)
app.register_blueprint(game_page)


#Connect namespaces
socketio.on_namespace(WaitingPageNamespace("/waitingpage"))
socketio.on_namespace(GamePageNamespace("/gamepage"))




socketio.run(app, host='0.0.0.0')
