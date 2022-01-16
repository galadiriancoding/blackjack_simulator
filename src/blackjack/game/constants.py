from .enums import Suit, Value, Action

SUITS: list[Suit] = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]
VALUES: list[Value] = [
    Value.TWO,
    Value.THREE,
    Value.FOUR,
    Value.FIVE,
    Value.SIX,
    Value.SEVEN,
    Value.EIGHT,
    Value.NINE,
    Value.TEN,
    Value.JACK,
    Value.QUEEN,
    Value.KING,
    Value.ACE,
]

POINTS: dict[Value, int] = {
    Value.TWO: 2,
    Value.THREE: 3,
    Value.FOUR: 4,
    Value.FIVE: 5,
    Value.SIX: 6,
    Value.SEVEN: 7,
    Value.EIGHT: 8,
    Value.NINE: 9,
    Value.TEN: 10,
    Value.JACK: 10,
    Value.QUEEN: 10,
    Value.KING: 10,
    Value.ACE: 1,
}

ACTIONS: list[Action] = [
    Action.HIT,
    Action.STAND,
    Action.DOUBLE,
    Action.SPLIT,
    Action.SURRENDER,
]

ORIGINAL_HAND: str = "original_hand"

INSURANCE_PAYOUT: int = 2
