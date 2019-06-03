from src.blackjack.custom_types import Deck
from src.blackjack.dealer import Dealer
from src.blackjack.game import Game
from src.blackjack.player import Player
from src.blackjack.setup import build_shoe, discard_all_cards
from src.intel.basic_strategy_ai import BasicStrategyAi
from src.blackjack.settings import TABLE_MINIMUM, SHOW_STATS, STARTING_WALLET, MAX_PLAYS


def main():
    player: Player = Player(False, STARTING_WALLET)
    dealer: Dealer = Dealer()
    shoe: Deck = build_shoe()
    discard_pile: Deck = []
    play_again: bool = True
    total_value: float = 0.0
    average_value: float = 0.0
    count: int = 0
    while play_again and player.wallet >= TABLE_MINIMUM and count < MAX_PLAYS:
        game: Game = Game(player, dealer, shoe, BasicStrategyAi())
        value: float = game.play()
        total_value += value
        count += 1
        average_value = total_value / count
        discard_pile = discard_all_cards(player, dealer, discard_pile)
        if len(discard_pile) >= 3 * len(shoe):
            if player.is_human:
                print("Re-shuffling shoe...")
            discard_pile = []
            shoe = build_shoe()
        if SHOW_STATS:
            print(f"Game value: ${value:.2f}. Total funds: ${player.wallet:.2f}")
            print(
                f"Total Value: ${total_value:.2f}. "
                + f"Average value per game: ${average_value:.10f}"
            )
        if player.is_human:
            play_again = input("Do you wish to play again? y/N: ")[0].upper() == "Y"

    if player.is_human:
        print(f"You cash out with ${player.wallet:.2f}.")
        print("Come back soon!")

    print(f"Final funds: ${player.wallet:.2f}")
    print(
        f"Total Value: ${total_value:.2f}. "
        + f"Average value per game: ${average_value:.10f}"
    )
    print(f"Total games playerd: {count}")


if __name__ == "__main__":
    main()
