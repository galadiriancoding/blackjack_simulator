from ..game.dealer import Dealer
from ..game.player import Player


class Ai:
    @staticmethod
    def get_bet(player: Player, dealer: Dealer) -> float:
        raise NotImplementedError

    @staticmethod
    def get_insurance(player: Player, dealer: Dealer) -> float:
        raise NotImplementedError

    @staticmethod
    def get_early_surrender(player: Player, dealer: Dealer) -> bool:
        raise NotImplementedError

    @staticmethod
    def get_action(hand_name: str, player: Player, dealer: Dealer) -> str:
        raise NotImplementedError
