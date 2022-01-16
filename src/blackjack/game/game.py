from configparser import ConfigParser
from uuid import uuid4

from ..intel.ai import Ai

from .constants import INSURANCE_PAYOUT, ORIGINAL_HAND
from .custom_types import Deck
from .dealer import Dealer
from .enums import Value
from .player import Player


class Game:
    __slots__ = [
        "player",
        "dealer",
        "shoe",
        "pots",
        "ai",
        "default_bet",
        "table_minimum",
        "table_maximum",
        "default_insurance",
        "hit_on_soft_17",
        "blackjack_payout",
        "surrender",
    ]

    def __init__(
        self, player: Player, dealer: Dealer, shoe: Deck, ai: Ai, config: ConfigParser
    ) -> None:
        self.player: Player = player
        self.dealer: Dealer = dealer
        self.shoe: Deck = shoe
        self.pots: dict[str, float] = {}
        self.ai: Ai = ai
        self.default_bet: float = config["PLAYER"].getfloat(
            "DEFAULT_BET", fallback=10.0
        )
        self.table_minimum: float = config["TABLE"].getfloat(
            "TABLE_MINIMUM", fallback=10.0
        )
        self.table_maximum: float = config["TABLE"].getfloat(
            "TABLE_MAXIMUM", fallback=10.0
        )
        self.default_insurance: float = config["PLAYER"].getfloat(
            "DEFAULT_INSURANCE", fallback=0
        )
        self.hit_on_soft_17: bool = config["GAME"].getboolean(
            "HIT_ON_SOFT_17", fallback=True
        )
        self.blackjack_payout: float = config["GAME"].getfloat(
            "BLACKJACK_PAYOUT", fallback=3.0 / 2.0
        )
        self.surrender: str = config["GAME"].get("SURRENDER", fallback="early")

    def get_bet(self) -> float:
        bet = self.default_bet
        if self.player.wallet < self.table_minimum:
            if self.player.is_human:
                print(
                    f"I'm sorry you need at leats ${self.table_minimum:.2f} to play"
                    + f" You only have ${self.player.wallet:.2f}."
                )
            return 0.0
        if self.player.is_human:
            try:
                print(f"You have ${self.player.wallet:.2f} to play with")
                bet = abs(float(input("Set your bet: $")))
                if bet > self.player.wallet:
                    print("Bet was larger than your wallet. Betting whole wallet.")
                    bet = self.player.wallet
                if bet > self.table_maximum:
                    print(
                        "Bet was larger than table maximum. "
                        + f"Betting ${self.table_maximum:.2f}"
                    )
                if bet < self.table_minimum:
                    print(
                        "Bet was smaller than table minimum. "
                        + f"Betting ${self.table_minimum:.2f}"
                    )
            except ValueError:
                print(f"That entry wasn't valid. Betting ${bet:.2f}.")
        else:
            bet = self.ai.get_bet(self.player, self.dealer)
        self.player.bet(bet)
        return bet

    def get_insurance(self) -> float:
        insurance: float = self.default_insurance
        if self.player.is_human:
            try:
                insurance += float(input("Set your insurance bet: $"))
            except ValueError:
                print("That entry wasn't valid. Refusing insurance")
        else:
            insurance = self.ai.get_insurance(self.player, self.dealer)
        self.player.bet(insurance)
        return insurance

    def get_early_surrender(self) -> bool:
        surrender = False
        if self.player.is_human:
            surrender = input("Do you wish to surrender? y/N")[0].upper() == "Y"
        else:
            surrender = self.ai.get_early_surrender(self.player, self.dealer)
        return surrender

    def play_dealer_and_get_score(self) -> int:
        while True:
            dealer_hard_score = self.dealer.get_hard_score()
            dealer_soft_score = self.dealer.get_soft_score()

            if dealer_hard_score > 21:
                return 0
            if dealer_soft_score > 17:
                return dealer_soft_score
            if dealer_soft_score == 17 and not self.hit_on_soft_17:
                return 17
            if dealer_hard_score >= 17:
                return dealer_hard_score

            self.dealer.deal_card(self.shoe.pop())

    def print_hands(self, hand_name: str, show_second_card: bool) -> None:
        if self.player.is_human:
            hand = self.player.hands[hand_name]
            print(f"Your cards are: {[c.value + c.suit for c in hand]}")
            if show_second_card:
                print(f"Dealer has {[c.value + c.suit for c in self.dealer.hand]}")
            else:
                print(f"Dealer has a {self.dealer.hand[0]}")

    def get_action(self, hand_name: str) -> str:
        if self.player.is_human:
            self.print_hands(hand_name, False)
            options: str = "Would you like to (H)it, (S)tand"
            if self.player.can_double(hand_name):
                options += ", (D)ouble"
            if self.player.can_split(hand_name):
                options += ", S(P)lit"
            if self.player.can_surrender(hand_name):
                options += " Su(R)render"
            options += ": "
            option = input(options)[0].upper()
        else:
            option = self.ai.get_action(hand_name, self.player, self.dealer)

        if option in ["H", "S"]:
            return option
        if option == "D" and self.player.can_double(hand_name):
            return option
        if option == "P" and self.player.can_split(hand_name):
            return option
        if option == "R" and self.player.can_surrender(hand_name):
            return option
        else:
            print("Invalid selection. Standing")
            return "S"

    def bust(self, hand_name: str) -> None:
        if self.player.is_human:
            self.print_hands(hand_name, False)
            print("Busted!")

    def resolve_player_actions(self, hand_name: str, bet: float) -> str:
        winner: str = ""
        playing = True
        while playing:
            action = self.get_action(hand_name)
            if action == "H":
                self.player.deal_card(hand_name, self.shoe.pop())
                if self.player.get_hard_score(hand_name) > 21:
                    winner = "dealer"
                    playing = False
                    self.bust(hand_name)

            elif action == "D":
                self.player.bet(bet)
                bet *= 2
                self.pots[hand_name] = bet
                self.player.deal_card(hand_name, self.shoe.pop())
                if self.player.get_hard_score(hand_name) > 21:
                    winner = "dealer"
                    self.bust(hand_name)
                playing = False

            elif action == "R":
                winner = "dealer"
                playing = False
                self.player.payout(0.5 * bet)
                if self.player.is_human:
                    print(f"You surrender. You recieve back ${(0.5 * bet):.2f}.")

            elif action == "P":
                self.play_split_game(bet, hand_name)
                playing = False

            if action == "S":
                playing = False

        return winner

    def resolve_payouts(self) -> None:
        dealer_score = self.play_dealer_and_get_score()
        player_scores: dict[str, int] = {}
        for hand in self.player.hands.keys():
            best_score = self.player.get_soft_score(hand)
            if best_score > 21:
                best_score = -1
            player_scores[hand] = best_score

        for hand, score in player_scores.items():
            if self.player.is_human:
                self.print_hands(hand, True)

            if dealer_score == score:
                self.player.payout(self.pots[hand])
                if self.player.is_human:
                    print("PUSH!")
            elif dealer_score < score:
                self.player.payout(2 * self.pots[hand])
                if self.player.is_human:
                    print(f"You win ${self.pots[hand]:.2f}")
            else:
                if self.player.is_human:
                    print("You lose! Better luck next time!")

    def resolve_player_blackjack(self, bet: float) -> str:
        winner: str = "player"
        if not self.dealer.has_blackjack:
            winnings = bet * (self.blackjack_payout + 1)
            self.player.payout(winnings)
            if self.player.is_human:
                self.print_hands(ORIGINAL_HAND, False)
                print(
                    f"You got blackjack! You win ${(bet * self.blackjack_payout):.2f}"
                )
        else:
            self.player.payout(bet)
            if self.player.is_human:
                self.print_hands(ORIGINAL_HAND, True)
                print("Both have Blackjack! Push!")
        return winner

    def resolve_insurance_scenario(self, bet: float) -> str:
        winner: str = ""
        if self.player.is_human:
            self.print_hands(ORIGINAL_HAND, False)
        if self.surrender == "early":
            do_surrender = self.get_early_surrender()
            if do_surrender:
                winner = "dealer"
                self.player.payout(0.5 * bet)
                if self.player.is_human:
                    print(f"You surrender. You recieve back ${(0.5 * bet):.2f}.")
                return winner
        if self.dealer.hand[0].value == Value.ACE:
            insurance = self.get_insurance()
            if self.dealer.has_blackjack():
                self.print_hands(ORIGINAL_HAND, True)
                winner = "dealer"
                self.player.payout(insurance * (INSURANCE_PAYOUT + 1))
                if not self.player.has_blackjack:
                    if self.player.is_human:
                        print("Dealer has Blackjack.")
                else:
                    self.player.payout(bet)
                    if self.player.is_human:
                        print("Both have Blackjack! Push!")
                if insurance > 0.0:
                    print(f"You get ${insurance:.2f} from your insurance bet")
            else:
                if self.player.is_human and insurance > 0.0:
                    print("Dealer does not have blackjack. Insurance bet lost.")
        return winner

    def play_split_game(self, bet: float, hand_name: str) -> None:
        self.player.bet(bet)

        card1 = self.player.hands[hand_name][0]
        card2 = self.player.hands[hand_name][1]
        self.player.hands.pop(hand_name)
        self.pots.pop(hand_name)
        hand1_name = "Split " + str(uuid4())
        hand2_name = "Split " + str(uuid4())
        self.player.hands[hand1_name] = [card1]
        self.player.hands[hand2_name] = [card2]

        self.pots[hand1_name] = bet
        self.pots[hand2_name] = bet

        self.player.deal_card(hand1_name, self.shoe.pop())
        self.player.deal_card(hand2_name, self.shoe.pop())

        if self.player.is_human:
            self.print_hands(hand1_name, False)
            self.print_hands(hand2_name, False)

        self.resolve_player_actions(hand1_name, bet)
        self.resolve_player_actions(hand2_name, bet)

        # if len(self.player.hands) >= 8:
        #     print(f"Large Split: {len(self.player.hands)} hands")

    def play(self) -> float:
        initial_funds = self.player.wallet

        winner = ""
        bet: float = self.get_bet()
        if bet <= 0:
            return 0.0

        self.pots[ORIGINAL_HAND] = bet

        self.player.add_hand(ORIGINAL_HAND)

        self.player.deal_card(ORIGINAL_HAND, self.shoe.pop())
        self.dealer.deal_card(self.shoe.pop())
        self.player.deal_card(ORIGINAL_HAND, self.shoe.pop())
        self.dealer.deal_card(self.shoe.pop())

        if self.dealer.hand[0].value in [
            Value.ACE,
            Value.TEN,
            Value.JACK,
            Value.QUEEN,
            Value.KING,
        ]:
            winner = self.resolve_insurance_scenario(bet)

        if winner == "" and self.player.has_blackjack(ORIGINAL_HAND):
            winner = self.resolve_player_blackjack(bet)

        if winner == "":
            winner = self.resolve_player_actions(ORIGINAL_HAND, bet)

        if winner == "":
            self.resolve_payouts()

        final_funds = self.player.wallet

        return final_funds - initial_funds
