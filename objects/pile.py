import constants

class Pile:
    def __init__(self):
        self._top_card = None
        self._last_colour = None
        print("Pile card: ", self._top_card)

    def get_last_colour(self):
        return self._last_colour

    def get_top_card(self):
        return self._top_card

    def add_card(self, card):
        self._top_card = card
        if "colour" in card.get_data():
            self._last_colour = card.get_data()["colour"]

    def set_top_colour(self, colour):
        top_card = self.get_top_card()
        if top_card.get_data()["name"] == "Wild":
            top_card.set_colour(colour)
