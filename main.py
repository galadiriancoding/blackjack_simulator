from src.custom_types import Deck
from src.dealer import Dealer
from src.game import Game
from src.player import Player
from src.setup import build_shoe, discard_all_cards


def main():
    player = Player(True, 1000.0)
    dealer = Dealer()
    shoe = build_shoe()
    discard_pile: Deck = []
    play_again = True
    while play_again:
        game = Game(player, dealer, shoe)
        game.play()
        discard_pile = discard_all_cards(player, dealer, discard_pile)
        if len(discard_pile) >= 3 * len(shoe):
            if player.is_human:
                print("Re-shuffling shoe...")
            discard_pile = []
            shoe = build_shoe()
        if player.is_human:
            play_again = input("Do you wish to play again? y/N: ")[0].upper() == "Y"


if __name__ == "__main__":
    main()
