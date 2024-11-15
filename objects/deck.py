import json
from objects.cards import *
from objects.playerdeck import PlayerDeck
import random

class Deck:

    DECK_PATH = "standarddeck.json"

    def __init__(self, custom):
        self._cards = []
        
        with open(self.DECK_PATH, mode="r") as f:
            deckfile = json.load(f)
            self._cards = deckfile["deck"]
        print("Deck cards:", self._cards)        
        self.add_custom(custom)


    def add_custom(self, custom):
        customs = {
            "threeCards": {
                "name": "PickUpOrWithdrawUntil3",
                "class": "PickUpOrWithdrawUntil3Card",
                "properties": {
            
                },
                "quantity": 1
            },
            "sevenCards": {
                "name": "PickUpOrWithdrawUntil7",
                "class": "PickUpOrWithdrawUntil7Card",
                "properties": {
            
                },
                "quantity": 1
            },
            "lastColour": {
                "name": "PickUpUntilLastColour",
                "class": "PickUpUntilLastColourCard",
                "properties": {
            
                },
                "quantity": 30
            },
            "shuffleHands": {
                "name": "ShuffleHands",
                "class": "ShuffleHandsCard",
                "properties": {
            
                },
                "quantity": 30
            }
        }
        for c in custom:
            if c in customs and custom[c]:
                self._cards.append(customs[c])


    def get_card_object(self, card_class, properties):
        match card_class:
            case "StandardCard":
                return StandardCard(properties)
            case "WildCard":
                return WildCard(properties)
            case "PlusTwoCard":
                return PlusTwoCard(properties)
            case "PlusFourCard":
                return PlusFourCard(properties)
            case "StopCard":
                return StopCard(properties)
            case "ReverseCard":
                return ReverseCard(properties)
            case "PickUpOrWithdrawUntil7Card":
                return PickUpOrWithdrawUntil7Card(properties)
            case "PickUpOrWithdrawUntil3Card":
                return PickUpOrWithdrawUntil3Card(properties)
            case "PickUpUntilLastColourCard":
                return PickUpUntilLastColourCard(properties)
            case "ShuffleHandsCard":
                return ShuffleHandsCard(properties)

    @staticmethod
    def generate_deck_file():
        cards = []

        #Generate standard cards
        colours = StandardCard.ALLOWED_COLOURS
        numbers = range(0,10)

        for c in colours:

            
            #Generate standard cards
            for n in numbers:
                if n == 0:
                    q = 1
                else:
                    q = 2
                card = {
                    "name": "Standard",
                    "class": "StandardCard",
                    "properties": {
                        "colour": c,
                        "number": n
                    },
                    "quantity": q
                }
                cards.append(card)


            #Generate plus two cards

            card = {
                "name": "PlusTwo",
                "class": "PlusTwoCard",
                "properties": {
                    "colour": c
                },
                "quantity": 1
            }
            cards.append(card)

            #Generate stop cards

            card = {
                "name": "Stop",
                "class": "StopCard",
                "properties": {
                    "colour": c
                },
                "quantity": 10
            }
            cards.append(card)

            #Generate reverse cards

            card = {
                "name": "Reverse",
                "class": "ReverseCard",
                "properties": {
                    "colour": c
                },
                "quantity": 1
            }
            cards.append(card)


        #Generate wild cards
        wild_cards = {
            "name": "Wild",
            "class": "WildCard",
            "properties": {},
            "quantity": 30

        }

        cards.append(wild_cards)

        #Generate Plus Four cards
        plus_four_cards = {
            "name": "PlusFour",
            "class": "PlusFourCard",
            "properties": {},
            "quantity": 4
        }

        cards.append(plus_four_cards)
        
        jsondata = {"deck":cards}

        with open(Deck.DECK_PATH, mode="w") as f:
            d = json.dumps(jsondata)
            f.write(d)


    def generate_random_card(self):
        weighting = [c["quantity"] for c in self._cards]
        card = random.choices(self._cards, weights = weighting)[0]
        return self.generate_card(card)

    def generate_random_standard_card(self):
        weighting = [c["quantity"] if c["name"] == "Standard" else 0 for c in self._cards]
        card = random.choices(self._cards, weights = weighting)[0]
        return self.generate_card(card)

    
    def give_player_cards(self, n):
        cards = []
        for _ in range(n):
            cards.append(self.generate_random_card())
        return PlayerDeck(cards)


    def generate_card(self, card):
        if card["quantity"] > 0:
            card_object = self.get_card_object(card["class"], dict(card["properties"]))
            card["quantity"]-=1
            if card["quantity"] == 0:
                self._cards.remove(card)
            return card_object

    
        
