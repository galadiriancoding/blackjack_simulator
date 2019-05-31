class Card:

    __slots__ = ["suit", "value", "face_up"]

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
