class PlayerDeck:
    def __init__(self, cards):
        self._cards = cards
        print("Player cards: ", self._cards)

    def is_empty(self):
        return len(self._cards) == 0

    def add_card(self, card):
        self._cards.append(card)

    def get_number_of_cards(self):
        return len(self._cards)

    def get_public_card_data(self):
        return {
            "number": self.get_number_of_cards()
        }

    def get_card_with_index(self, i):
        card =  self._cards[i]
        return card

    def remove_card_with_index(self, i):
        del self._cards[i]

    #Returns list of dictionaries with cards and index of each card.
    def get_private_card_data(self):
        return [{"index": i, "card": c.get_data()} for i,c in enumerate(self._cards)]

    def get_cards(self):
        return self._cards

    
