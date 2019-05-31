from typing import Any, Dict
from uuid import uuid4

from .constants import ORIGINAL_HAND
from .custom_types import Deck
from .dealer import Dealer
from .player import Player
from .settings import (BLACKJACK_PAYOUT, DEFAULT_BET, DEFAULT_INSURANCE,
                       HIT_ON_SOFT_17, SURRENDER, TABLE_MAXIMUM, TABLE_MINIMUM)


class Game:
    __slots__ = ["player", "dealer", "shoe", "local_pots"]

    def __init__(self, player: Player, dealer: Dealer, shoe: Deck) -> None:
        self.player: Player = player
        self.dealer: Dealer = dealer
        self.shoe: Deck = shoe
        self.local_pots: Dict[str, float] = {}

    def get_bet(self) -> float:
        bet = DEFAULT_BET
        if self.player.is_human:
            try:
                print(f"You have ${self.player.wallet:.2f} to play with")
                bet = abs(float(input("Set your bet: $")))
                if bet > self.player.wallet:
                    print(f"Bet was larger than your wallet. Betting whole wallet.")
                    bet = self.player.wallet
                if bet > TABLE_MAXIMUM:
                    print(
                        "Bet was larger than table maximum. "
                        + f"Betting ${TABLE_MAXIMUM:.2f}"
                    )
                if bet < TABLE_MINIMUM:
                    print(
                        "Bet was smaller than table minimum. "
                        + f"Betting ${min(TABLE_MINIMUM, self.player.wallet):.2f}"
                    )
            except ValueError:
                print(f"That entry wasn't valid. Betting ${bet:.2f}.")
        self.player.bet(bet)
        return bet

    def get_insurance(self) -> float:
        insurance: float = DEFAULT_INSURANCE
        if self.player.is_human:
            try:
                insurance += float(input("Set your insurance bet: $"))
            except ValueError:
                print("That entry wasn't valid. Refusing insurance")
        self.player.bet(insurance)
        return insurance

    def get_early_surrender(self) -> str:
        surrender = "N"
        if self.player.is_human:
            surrender = input("Do you wish to surrender? y/N")[0].upper()
        return surrender

    def play_dealer_and_get_score(self) -> int:
        while True:
            dealer_hard_score = self.dealer.get_hard_score()
            dealer_soft_score = self.dealer.get_soft_score()

            if dealer_hard_score > 21:
                return 0
            if dealer_soft_score > 17:
                return dealer_soft_score
            if dealer_soft_score == 17 and not HIT_ON_SOFT_17:
                return 17
            if dealer_hard_score >= 17:
                return dealer_hard_score

            self.dealer.deal_card(self.shoe.pop())

    def print_hands(self, hand_name: str, show_scond_card: bool) -> None:
        if self.player.is_human:
            hand = self.player.hands[hand_name]
            print(f"Your cards are: {[c.value + c.suit for c in hand]}")
            if show_scond_card:
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

        return "S"

    def bust(self, hand_name: str) -> None:
        if self.player.is_human:
            self.print_hands(hand_name, False)
            print("Busted!")

    def resolve_player_actions(self, hand_name: str, bet: float) -> Any:
        winner: Any = None
        playing = True
        while playing:
            action = self.get_action(hand_name)
            if action == "H":
                self.player.deal_card(hand_name, self.shoe.pop())
                if self.player.get_hard_score(hand_name) > 21:
                    winner = self.dealer
                    playing = False
                    self.bust(hand_name)

            elif action == "D":
                self.player.bet(bet)
                bet *= 2
                self.local_pots[hand_name] = bet
                self.player.deal_card(hand_name, self.shoe.pop())
                if self.player.get_hard_score(hand_name) > 21:
                    winner = self.dealer
                    self.bust(hand_name)
                playing = False

            elif action == "R":
                winner = self.dealer
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
        player_scores: Dict[str, int] = {}
        for hand in self.player.hands.keys():
            best_score = self.player.get_soft_score(hand)
            if best_score > 21:
                best_score = -1
            player_scores[hand] = best_score

        for hand, score in player_scores.items():
            if self.player.is_human:
                self.print_hands(hand, True)

            if dealer_score == score:
                self.player.payout(self.local_pots[hand])
                if self.player.is_human:
                    print("PUSH!")
            elif dealer_score < score:
                self.player.payout(2 * self.local_pots[hand])
                if self.player.is_human:
                    print(f"You win ${self.local_pots[hand]:.2f}")
            else:
                if self.player.is_human:
                    print("You lose! Better luck next time!")

    def resolve_player_blackjack(self, bet: float) -> Any:
        winner: Any = Player
        winnings = bet * (BLACKJACK_PAYOUT + 1)
        self.player.payout(winnings)
        if self.player.is_human:
            print(f"You got blackjack! You win ${(bet * BLACKJACK_PAYOUT):.2f}")
        return winner

    def resolve_insurance_scenario(self, bet: float) -> Any:
        winner: Any = None
        if SURRENDER == "early":
            do_surrender = self.get_early_surrender()
            if do_surrender == "Y":
                winner = self.dealer
                self.player.payout(0.5 * bet)
                if self.player.is_human:
                    print(f"You surrender. You recieve back ${(0.5 * bet):.2f}.")
                return winner
        insurance = self.get_insurance()
        if self.dealer.has_blackjack():
            self.print_hands(ORIGINAL_HAND, True)
            winner = self.dealer
            self.player.payout(2 * insurance)
            if self.player.is_human:
                print("Dealer has Blackjack.")
                if insurance > 0.0:
                    print(f"You get ${insurance:.2f} from your insurance bet")
        return winner

    def play_split_game(self, bet: float, hand_name: str) -> None:
        self.player.bet(bet)

        card1 = self.player.hands[hand_name][0]
        card2 = self.player.hands[hand_name][1]
        self.player.hands.pop(hand_name)
        self.local_pots.pop(hand_name)
        hand1_name = "Split " + str(uuid4())
        hand2_name = "Split " + str(uuid4())
        self.player.hands[hand1_name] = [card1]
        self.player.hands[hand2_name] = [card2]

        self.local_pots[hand1_name] = bet
        self.local_pots[hand2_name] = bet

        self.player.deal_card(hand1_name, self.shoe.pop())
        self.player.deal_card(hand2_name, self.shoe.pop())

        if self.player.is_human:
            self.print_hands(hand1_name, False)
            self.print_hands(hand2_name, False)

        if card1.value != "A":
            self.resolve_player_actions(hand1_name, bet)
        if card2.value != "A":
            self.resolve_player_actions(hand2_name, bet)

    def play(self) -> None:

        winner = None
        bet: float = self.get_bet()

        self.local_pots[ORIGINAL_HAND] = bet

        self.player.add_hand(ORIGINAL_HAND)

        self.player.deal_card(ORIGINAL_HAND, self.shoe.pop())
        self.dealer.deal_card(self.shoe.pop())
        self.player.deal_card(ORIGINAL_HAND, self.shoe.pop())
        self.dealer.deal_card(self.shoe.pop())

        if self.player.is_human:
            self.print_hands(ORIGINAL_HAND, False)

        if self.player.has_blackjack(ORIGINAL_HAND):
            winner = self.resolve_player_blackjack(bet)

        if self.dealer.hand[0].value == "A":
            winner = self.resolve_insurance_scenario(bet)

        if winner is None:
            winner = self.resolve_player_actions(ORIGINAL_HAND, bet)

        if winner is None:
            self.resolve_payouts()
