from configparser import ConfigParser, SectionProxy
from .card import Card
from .constants import ORIGINAL_HAND, POINTS
from .custom_types import Hand
from .enums import Value


class Player:
    __slots__ = ["hands", "is_human", "wallet", "game_conf"]

    def __init__(self, config: ConfigParser):
        self.hands: dict[str, Hand] = {}
        self.is_human: bool = config["PLAYER"].getboolean("HUMAN_PLAYER", fallback=True)
        self.wallet: float = config["PLAYER"].getfloat(
            "STARTING_WALLET", fallback=100000.0
        )
        self.game_conf: SectionProxy = config["GAME"]

    def add_hand(self, hand_name: str) -> None:
        self.hands[hand_name] = []

    def clear_hands(self) -> None:
        self.hands = {}

    def deal_card(self, hand_name: str, card: Card) -> None:
        if not self.hands[hand_name]:
            self.add_hand(hand_name)
        self.hands[hand_name].append(card)

    def clear_hand(self, hand_name: str) -> None:
        self.hands[hand_name] = []

    def contains_ace(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        return any(c.value == Value.ACE for c in self.hands[hand_name])

    def get_hard_score(self, hand_name: str) -> int:
        if not self.hands[hand_name]:
            return 0
        hard_score = 0
        for card in self.hands[hand_name]:
            hard_score += POINTS[card.value]
        return hard_score

    def has_soft_score(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        hard_score = self.get_hard_score(hand_name)
        return self.contains_ace(hand_name) and hard_score + 10 <= 21

    def get_soft_score(self, hand_name: str) -> int:
        if not self.hands[hand_name]:
            return 0
        hard_score = self.get_hard_score(hand_name)
        if not self.has_soft_score(hand_name):
            return hard_score
        return hard_score + 10

    def bet(self, amount: float) -> None:
        self.wallet -= amount

    def payout(self, amount: float) -> None:
        self.wallet += amount

    def has_blackjack(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        return (
            len(self.hands[hand_name]) == 2
            and self.contains_ace(hand_name)
            and any(
                c.value in [Value.TEN, Value.JACK, Value.QUEEN, Value.KING]
                for c in self.hands[hand_name]
            )
        )

    def can_split(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        split_lint = self.game_conf.getint("SPLIT_LIMIT", fallback=0)
        return (
            len(self.hands[hand_name]) == 2
            and self.hands[hand_name][0].value == self.hands[hand_name][1].value
            and (split_lint == 0 or len(self.hands) <= split_lint)
            and (
                hand_name == ORIGINAL_HAND
                or self.game_conf.getboolean("RESPLIT_ACES", fallback=False)
                or self.hands[hand_name][0].value != Value.ACE
            )
        )

    def can_double(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        return len(self.hands[hand_name]) == 2 and (
            self.game_conf.getboolean("DOUBLE_AFTER_SPLIT", fallback=True)
            or hand_name == ORIGINAL_HAND
        )

    def can_surrender(self, hand_name: str) -> bool:
        if not self.hands[hand_name]:
            return False
        return (
            len(self.hands[hand_name]) == 2
            and self.game_conf.get("SURRENDER", fallback="early") != "None"
            and hand_name == ORIGINAL_HAND
        )
