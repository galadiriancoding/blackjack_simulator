from src.blackjack.player import Player
from src.blackjack.dealer import Dealer


class Ai:
    @staticmethod
    def get_bet() -> float:
        raise NotImplementedError

    @staticmethod
    def get_insurance() -> float:
        raise NotImplementedError

    @staticmethod
    def get_early_surrender(player: Player, dealer: Dealer) -> str:
        raise NotImplementedError

    @staticmethod
    def get_action(hand_name: str, player: Player, dealer: Dealer) -> str:
        raise NotImplementedError
