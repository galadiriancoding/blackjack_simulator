from .card import Card
from typing import List, Dict
from .constants import POINTS
from .settings import SURRENDER


class Player:
    __slots__ = ["hands", "is_human", "wallet"]

    def __init__(self, is_human: bool, wallet: float):
        self.hands: Dict[str, List[Card]] = {}
        self.is_human: bool = is_human
        self.wallet = wallet

    def add_hand(self, hand_name: str):
        self.hands.update({hand_name: []})

    def clear_hands(self):
        self.hands = {}

    def deal_card(self, hand_name: str, card: Card) -> None:
        self.hands[hand_name].append(card)

    def clear_hand(self, hand_name: str) -> None:
        self.hands[hand_name] = []

    def contains_ace(self, hand_name: str) -> bool:
        return any(c.value == "A" for c in self.hands[hand_name])

    def get_hard_score(self, hand_name: str) -> int:
        hard_score = 0
        for card in self.hands[hand_name]:
            hard_score += POINTS[card.value]
        return hard_score

    def has_soft_score(self, hand_name: str) -> bool:
        hard_score = self.get_hard_score(hand_name)
        return self.contains_ace(hand_name) and hard_score + 10 < 21

    def get_soft_score(self, hand_name: str) -> int:
        hard_score = self.get_hard_score(hand_name)
        if not self.has_soft_score(hand_name):
            return hard_score
        return hard_score + 10

    def bet(self, amount: float) -> None:
        self.wallet -= amount

    def payout(self, amount: float) -> None:
        self.wallet += amount

    def has_blackjack(self, hand_name: str) -> bool:
        return (
            len(self.hands[hand_name]) == 2
            and self.contains_ace(hand_name)
            and any(c.value in ["T", "J", "Q", "K"] for c in self.hands[hand_name])
        )

    def can_split(self, hand_name: str) -> bool:
        return (
            len(self.hands[hand_name]) == 2
            and self.hands[hand_name][0].value == self.hands[hand_name][1].value
        )

    def can_double(self, hand_name: str) -> bool:
        return len(self.hands[hand_name]) == 2

    def can_surrender(self, hand_name: str) -> bool:
        return len(self.hands[hand_name]) == 2 and SURRENDER != "None"
