from typing import List

from .card import Card
from .constants import POINTS


class Dealer:
    __slots__ = ["hand", "hidden_second_card"]

    def __init__(self):
        self.hand: List[Card] = []
        self.hidden_second_card: bool = True

    def deal_card(self, card: Card) -> None:
        self.hand.append(card)

    def clear_hand(self) -> None:
        self.hand = []

    def contains_ace(self) -> bool:
        return any(c.value == "A" for c in self.hand)

    def get_hard_score(self) -> int:
        hard_score = 0
        for card in self.hand:
            hard_score += POINTS[card.value]
        return hard_score

    def has_soft_score(self) -> bool:
        hard_score = self.get_hard_score()
        return self.contains_ace() and hard_score + 10 < 21

    def get_soft_score(self) -> int:
        hard_score = self.get_hard_score()
        if not self.has_soft_score():
            return hard_score
        return hard_score + 10

    def has_blackjack(self) -> bool:
        return (
            len(self.hand) == 2
            and self.contains_ace()
            and any(c.value in ["T", "J", "Q", "K"] for c in self.hand)
        )
