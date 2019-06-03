class Card:

    __slots__ = ["suit", "value"]

    def __init__(self, suit: str, value: str):
        self.suit: str = suit
        self.value: str = value

    def __str__(self) -> str:
        return self.value + self.suit
