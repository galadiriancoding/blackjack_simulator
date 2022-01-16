from .game.custom_types import Deck
from .game.dealer import Dealer
from .game.game import Game
from .game.player import Player
from .game.setup import build_shoe, discard_all_cards
from .intel.ai import Ai
from .intel.basic_strategy_ai import BasicStrategyAi
from .config import Config


def main():
    config = Config.config()
    player: Player = Player(config)
    dealer: Dealer = Dealer()
    shoe: Deck = build_shoe(config["TABLE"].getint("DECK_COUNT", fallback=8))
    ai: Ai = BasicStrategyAi()
    discard_pile: Deck = []
    play_again: bool = True
    total_value: float = 0.0
    average_value: float = 0.0
    count: int = 0
    while (
        play_again
        and player.wallet >= config["TABLE"].getfloat("TABLE_MINIMUM", fallback=10.0)
        and count < config["TABLE"].getint("MAX_PLAYS", fallback=10000000)
    ):
        game: Game = Game(player, dealer, shoe, ai, config)
        value: float = game.play()
        total_value += value
        count += 1
        average_value = total_value / count
        discard_pile = discard_all_cards(player, dealer, discard_pile)
        if len(discard_pile) >= 3 * len(shoe):
            if player.is_human:
                print("Re-shuffling shoe...")
            discard_pile = []
            shoe = build_shoe(config["TABLE"].getint("DECK_COUNT", fallback=8))
        if config["MISC"].getboolean("SHOW_STATS", fallback=True):
            print(f"Game value: ${value:.2f}. Total funds: ${player.wallet:.2f}")
            print(
                f"Total Value: ${total_value:.2f}. "
                + f"Average value per game: ${average_value:.10f}"
            )
        if player.is_human:
            play_again_input = input("Do you wish to play again? y/N: ")
            play_again = (
                len(play_again_input) > 0 and play_again_input[0].upper() == "Y"
            )

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
