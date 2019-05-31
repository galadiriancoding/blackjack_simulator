class Card:

    __slots__ = ["suit", "value", "face_up"]

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return self.value + self.suit
