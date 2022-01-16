from .enums import Suit, Value


class Card:

    __slots__ = ["suit", "value"]

    def __init__(self, suit: Suit, value: Value):
        self.suit: Suit = suit
        self.value: Value = value

    def __str__(self) -> str:
        return f"{self.value}{self.suit}"
