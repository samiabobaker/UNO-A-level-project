import constants

class Effect:
    def __init__(self, type):
        self._type = type

    def get_type(self):
        return self._type

class ChangePropertyEffect(Effect):
    def __init__(self, property, new):
        super().__init__(constants.CHANGE_PROPERTY)
        self._property = property
        self._new = new

    def get_property(self):
        return self._property

    def get_new(self):
        return self._new

class AddPenaltyEffect(Effect):
    def __init__(self, penalty):
        super().__init__(constants.ADD_PENALTY)
        self._penalty = penalty

    def get_penalty(self):
        return self._penalty
    
class PickUpOrWithdrawEffect(Effect):
    def __init__(self, number):
        super().__init__(constants.PICK_UP_OR_WITHDRAW)
        self._number = number
    
    def get_number(self):
        return self._number
    

class PickUpUntilColourEffect(Effect):
    def __init__(self, colour):
        super().__init__(constants.PICK_UP_UNTIL_COLOUR)
        self._colour = colour

    def get_colour(self):
        return self._colour
    
