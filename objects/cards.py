from flask import url_for
from objects.effects import Effect, ChangePropertyEffect, AddPenaltyEffect, PickUpOrWithdrawEffect, PickUpUntilColourEffect
import constants

#Abstract card class
class Card:

    NO_COLOUR_CARDS = ("Wild", "PlusFour", "PickUpOrWithdrawUntil3", "PickUpOrWithdrawUntil7", "PickUpUntilLastColour", "ShuffleHands")

    def __init__(self, properties):
        if not self.is_valid_properties(properties):
            raise Exception("Invalid properties on card")
        self._properties = properties


    #Should return whether this card be put down on the given card with the given mode (passive or attacking)
    def can_be_put_on(self, current_turn, card):
        pass

    #Should return data to be sent as json to client
    def get_data(self):
        pass 

    #Should return whether a given dictionary of properties is valid or not.
    def is_valid_properties(self, properties):
        pass


    #Should return the effects of putting this card down given the current state of the game.
    def get_effects(self, pile, player_deck, current_state):
        pass


class StandardCard(Card):


    ALLOWED_COLOURS = (constants.RED, constants.GREEN, constants.BLUE, constants.YELLOW)


    def can_be_put_on(self, current_turn, card):
        if current_turn["mode"] == constants.ATTACKING:
            return False

        card_data = card.get_data()

        if current_turn[constants.STACK_BY_NUMBER] and card_data["number"] != self._properties["number"]:
            return False
        if card_data["name"] in ("PlusFour", "PickUpOrWithdrawUntil3", "PickUpOrWithdrawUntil7", "PickUpUntilLastColour", "ShuffleHands"):
            return True

        if card_data["name"] == "Wild" and "colour" not in card_data:
            return True
        if card_data["name"] == "Wild" and card_data["colour"] == self._properties["colour"]:
            return True
        if "colour" not in card_data:
            return False

        if card_data["colour"] == self._properties["colour"]:
            return True
            
        if "number" not in card_data:
            return False
        
        if card_data["number"] == self._properties["number"]:
            return True
        
        return False
        
        
    def get_data(self):
        return {
            "name": "Standard",
            "colour": self._properties["colour"],
            "number": self._properties["number"],
            "imageURL": self.get_image_url()
        }


    def get_image_url(self):
        filename = "cardassets/" + self._properties["colour"].capitalize() + "_" + str(self._properties["number"]) + ".png"
        return url_for("static", filename=filename)

    def is_valid_properties(self, properties):
        if "colour" not in properties:
            return False
        if "number" not in properties:
            return False
        if type(properties["number"]) != int:
            return False
        if properties["number"] > 9 or properties["number"] < 0:
            return False
        if properties["colour"] not in self.ALLOWED_COLOURS:
            return False
        return True

    def get_effects(self, pile, player_deck, current_state):
        number = self._properties["number"]
        cards = player_deck.get_cards()
        can_stack = False
        for card in cards:
            if card == self:
                continue
            if "number" not in card.get_data():
                continue
            if card.get_data()["number"] == number:
                can_stack = True
                break
        if can_stack:
            return (
                ChangePropertyEffect(constants.STACK_BY_NUMBER,True), 
                ChangePropertyEffect(constants.SKIPPABLE, True),
                ChangePropertyEffect(constants.CAN_PICK_UP, False),
                ChangePropertyEffect(constants.COLOURED_ONLY,False)
            )
        else:
            return (
                Effect(constants.NEXT_GO), 
                ChangePropertyEffect(constants.SKIPPABLE, False), 
                ChangePropertyEffect(constants.STACK_BY_NUMBER, False),
                ChangePropertyEffect(constants.CAN_PICK_UP, True),
                ChangePropertyEffect(constants.COLOURED_ONLY,False)
            )


class StopCard(Card):
    def get_data(self):
        return {
            "name": "Stop",
            "imageURL": self.get_image_url(),
            "colour": self._properties["colour"]
        }

    def can_be_put_on(self, current_turn, card):
        card_data = card.get_data()
        if current_turn[constants.MODE] == constants.PASSIVE:
            if card_data["name"] == "Stop":
                return True
            if "colour" not in card_data:
                if card_data["name"] in Card.NO_COLOUR_CARDS:
                    return True
                return False
            if card_data["colour"] == self._properties["colour"]:
                return True
        if current_turn [constants.MODE] == constants.ATTACKING:
            return True

    def is_valid_properties(self, properties):
        if "colour" not in properties:
            return False
        if properties["colour"] not in StandardCard.ALLOWED_COLOURS:
            return False

        return True


    def get_effects(self, pile, player_deck, current_state):
        if current_state[constants.MODE] == constants.ATTACKING:
            return (
                Effect(constants.NEXT_GO),
            )
        elif current_state[constants.MODE] == constants.PASSIVE:
            return (
                ChangePropertyEffect(constants.CAN_PICK_UP, True),
                ChangePropertyEffect(constants.COLOURED_ONLY,False),
                Effect(constants.NEXT_GO),
                Effect(constants.NEXT_GO)
            )

    def get_image_url(self):
        filename = "cardassets/" + self._properties["colour"].capitalize() + "_Skip.png"
        return url_for("static", filename=filename)


class ReverseCard(Card):
    def get_data(self):
        return {
            "name": "Reverse",
            "imageURL": self.get_image_url(),
            "colour": self._properties["colour"]
        }

    def can_be_put_on(self, current_turn, card):
        card_data = card.get_data()
        if current_turn[constants.MODE] == constants.PASSIVE:
            if card_data["name"] == "Reverse":
                return True
            if "colour" not in card_data:
                if card_data["name"] in Card.NO_COLOUR_CARDS:
                    return True
                return False
            if card_data["colour"] == self._properties["colour"]:
                return True
        if current_turn [constants.MODE] == constants.ATTACKING:
            return True

    def is_valid_properties(self, properties):
        if "colour" not in properties:
            return False
        if properties["colour"] not in StandardCard.ALLOWED_COLOURS:
            return False

        return True


    def get_effects(self, pile, player_deck, current_state):
        return (
            ChangePropertyEffect(constants.CAN_PICK_UP, True),
            ChangePropertyEffect(constants.COLOURED_ONLY,False),
            Effect(constants.REVERSE),
        )

    def get_image_url(self):
        filename = "cardassets/" + self._properties["colour"].capitalize() + "_Reverse.png"
        return url_for("static", filename=filename)

class WildCard(Card):

    def __init__(self, properties):
        super().__init__(properties)
        self._properties["colour"] = None

    #Wild cards have no properties
    def is_valid_properties(self, properties):
        return True



    def get_data(self):
        data =  {
            "name": "Wild",
            "imageURL": url_for("static", filename="cardassets/Wild.png")
        }
        if self._properties["colour"] != None:
            data["colour"] = self._properties["colour"]
        return data


    def can_be_put_on(self, current_turn, card):
        if current_turn[constants.STACK_BY_NUMBER]:
            return False
        if current_turn["mode"] == constants.PASSIVE:
            return True 
        return False

    def get_effects(self, pile, player_deck, current_state):
        cards = player_deck.get_cards()
        cards_left = False
        for card in cards:
            if "colour" in card.get_data():
                cards_left = True
                break
        if cards_left:
            return (ChangePropertyEffect(constants.COLOURED_ONLY,True),ChangePropertyEffect(constants.CAN_PICK_UP, False))
        else:
            return (ChangePropertyEffect(constants.CHOOSE_COLOUR, True),ChangePropertyEffect(constants.CAN_PICK_UP, False))

    def set_colour(self,colour):
        if colour in StandardCard.ALLOWED_COLOURS:
            self._properties["colour"] = colour


class PlusTwoCard(Card):

    def is_valid_properties(self, properties):
        if "colour" not in properties:
            return False
        if properties["colour"] not in StandardCard.ALLOWED_COLOURS:
            return False

        return True

    def get_data(self):
        return {
            "name": "PlusTwo",
            "colour": self._properties["colour"],
            "imageURL": self.get_image_url()
        }
        

    def get_image_url(self):
        filename = "cardassets/" + self._properties["colour"].capitalize() + "_Draw.png"
        return url_for("static", filename=filename)

    def can_be_put_on(self, current_turn, card):
        card_data = card.get_data()
        if current_turn[constants.MODE] == constants.PASSIVE:
            if "colour" not in card_data:
                if card_data["name"] in Card.NO_COLOUR_CARDS:
                    return True
                return False
            if card_data["colour"] == self._properties["colour"]:
                return True
        if current_turn [constants.MODE] == constants.ATTACKING:
            return True

    def get_effects(self, pile, player_deck, current_state):
        return (
            ChangePropertyEffect(constants.CAN_PICK_UP, True),
            ChangePropertyEffect(constants.COLOURED_ONLY,False),
            ChangePropertyEffect(constants.MODE, constants.ATTACKING),
            AddPenaltyEffect(2),
            Effect(constants.NEXT_GO)
        )

class PlusFourCard(Card):
    def is_valid_properties(self, properties):
        return True

    def get_data(self):
        return {
            "name": "PlusFour",
            "imageURL": self.get_image_url()
        }

    def get_image_url(self):
        filename = "cardassets/Wild_Draw.png"
        return url_for("static", filename=filename)

    def can_be_put_on(self, current_turn, card):
        return True

    def get_effects(self, pile, player_deck, current_state):
        return (
            ChangePropertyEffect(constants.MODE, constants.ATTACKING),
            AddPenaltyEffect(4),
            Effect(constants.NEXT_GO)
        )
    
class PickUpOrWithdrawUntil3Card(Card):
    def is_valid_properties(self, properties):
        return True
    
    def get_data(self):
        return {
            "name": "PickUpOrWithdrawUntil3",
            "imageURL": url_for("static", filename="cardassets/3Cards.png")
        }
    
    def can_be_put_on(self, current_turn, card):
        if current_turn[constants.MODE] == constants.PASSIVE:
            return True
        else:
            return False
    
    def get_effects(self, pile, player_deck, current_state):
        return (
            PickUpOrWithdrawEffect(3),
            Effect(constants.NEXT_GO)
        )
    

class PickUpOrWithdrawUntil7Card(Card):
    def is_valid_properties(self, properties):
        return True
    
    def get_data(self):
        return {
            "name": "PickUpOrWithdrawUntil7",
            "imageURL": url_for("static", filename="cardassets/7Cards.png")
        }
    
    def can_be_put_on(self, current_turn, card):
        if current_turn[constants.MODE] == constants.PASSIVE:
            return True
        else:
            return False
    
    def get_effects(self, pile, player_deck, current_state):
        return (
            PickUpOrWithdrawEffect(7),
            Effect(constants.NEXT_GO)
        )
    

class PickUpUntilLastColourCard(Card):
    def is_valid_properties(self, properties):
        return True
    
    def get_data(self):
        return {
            "name": "PickUpUntilLastColour",
            "imageURL": url_for("static", filename="cardassets/LastColourPlayed.png")
        }
    
    def can_be_put_on(self, current_turn, card):
        if current_turn[constants.MODE] == constants.PASSIVE:
            return True
        else:
            return False
    
    def get_effects(self, pile, player_deck, current_state):
        return (
            Effect(constants.NEXT_GO),
            PickUpUntilColourEffect(pile.get_last_colour())
            
        )
    
class ShuffleHandsCard(Card):
    def is_valid_properties(self, properties):
        return True
    
    def get_data(self):
        return {
            "name": "ShuffleHands",
            "imageURL": url_for("static", filename="cardassets/ShuffleHands.png")
        }
    
    def can_be_put_on(self, current_turn, card):
        if current_turn[constants.MODE] == constants.PASSIVE:
            return True
        else:
            return False
    
    def get_effects(self, pile, player_deck, current_state):
        return (
            Effect(constants.NEXT_GO),
            Effect(constants.SHUFFLE_HANDS)
            
        )