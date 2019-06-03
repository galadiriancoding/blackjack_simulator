from .ai import Ai
from src.blackjack.player import Player
from src.blackjack.dealer import Dealer
from .basic_strategy_ai_actions import (
    HIT_HARD_ACTIONS,
    HIT_SOFT_ACTIONS,
    HIT_SPLIT_ACTIONS,
    STAND_HARD_ACTIONS,
    STAND_SOFT_ACTIONS,
    STAND_SPLIT_ACTIONS,
)
from src.blackjack.settings import DOUBLE_AFTER_SPLIT, HIT_ON_SOFT_17, TABLE_MINIMUM


class BasicStrategyAi(Ai):
    def __init__(self):
        pass

    @staticmethod
    def get_bet(player: Player, dealer: Dealer) -> float:
        return TABLE_MINIMUM

    @staticmethod
    def get_insurance(player: Player, dealer: Dealer) -> float:
        return 0.0

    @staticmethod
    def get_early_surrender(player: Player, dealer: Dealer) -> str:
        if (
            player.get_hard_score in [15, 16, 17]
            and not player.contains_ace()
            and player.can_surrender()
            and dealer.hand[0].value == "A"
        ):
            return "Y"
        return "N"

    @staticmethod
    def evaluate_action_code(hand_name: str, action: str, player: Player) -> str:
        if action in ["H", "S"]:
            return action
        if action in ["Dh", "Ds"]:
            if player.can_double(hand_name):
                return "D"
            return action[1].upper()
        if action in ["Rh", "Rs"]:
            if player.can_surrender(hand_name):
                return "R"
            return action[1].upper()
        if action in ["Ph", "Ps"]:
            if player.can_split(hand_name):
                return "P"
            return action[1].upper()
        if action in ["Lh", "Ls"]:
            if player.can_split(hand_name) and DOUBLE_AFTER_SPLIT:
                return "P"
            return action[1].upper()
        if action in ["Rph", "Rps"]:
            if player.can_surrender(hand_name):
                return "R"
            if player.can_split(hand_name):
                return "P"
            return action[2].upper()
        return "S"

    @staticmethod
    def get_action(hand_name: str, player: Player, dealer: Dealer) -> str:
        player_hard: int = player.get_hard_score(hand_name)
        player_soft: int = player.get_soft_score(hand_name)

        action: str = ""

        dealer_card_value: str = dealer.hand[0].value
        if player.can_split(hand_name):
            if HIT_ON_SOFT_17:
                action = HIT_SPLIT_ACTIONS[(player_hard, dealer_card_value)]
            else:
                action = STAND_SPLIT_ACTIONS[(player_hard, dealer_card_value)]
        elif player.has_soft_score(hand_name):
            if HIT_ON_SOFT_17:
                action = HIT_SOFT_ACTIONS[(player_soft, dealer_card_value)]
            else:
                action = STAND_SOFT_ACTIONS[(player_soft, dealer_card_value)]
        else:
            if HIT_ON_SOFT_17:
                action = HIT_HARD_ACTIONS[(player_hard, dealer_card_value)]
            else:
                action = STAND_HARD_ACTIONS[(player_hard, dealer_card_value)]

        return BasicStrategyAi.evaluate_action_code(hand_name, action, player)