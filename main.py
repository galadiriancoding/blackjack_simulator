from src.player import Player
from src.dealer import Dealer
from src.setup import build_shoe, discard_all_cards
from src.game import play
from src.custom_types import Deck


def main():
    player = Player(True, 1000.0)
    dealer = Dealer()
    shoe = build_shoe()
    discard_pile: Deck = []
    play(player, dealer, shoe)
    discard_pile = discard_all_cards(player, dealer, discard_pile)
    if len(discard_pile) >= 3 * len(shoe):
        discard_pile = []
        shoe = build_shoe()


if __name__ == "__main__":
    main()
