from .player import Player
from .dealer import Dealer
from .custom_types import Deck
from .settings import BLACKJACK_PAYOUT, SURRENDER, HIT_ON_SOFT_17
from typing import Dict


def get_bet(player: Player) -> float:
    bet = 5.00
    if player.is_human:
        try:
            print(f"You have ${player.wallet} to play with")
            bet = float(input("Set your bet: $"))
        except ValueError:
            print(f"That entry wasn't valid. Betting ${bet}.")
    player.bet(bet)
    return bet


def get_insurance(player: Player) -> float:
    insurance = 0.0
    if player.is_human:
        try:
            insurance = float(input("Set your insurance bet: $"))
        except ValueError:
            print(f"That entry wasn't valid. Refusing insurance")
    player.bet(insurance)
    return insurance


def play_split_game(player: Player) -> Dict[str, float]:
    return {}


def play_dealer_and_get_score(dealer: Dealer, shoe: Deck) -> int:
    while True:
        dealer_hard_score = dealer.get_hard_score()
        dealer_soft_score = dealer.get_soft_score()

        if dealer_soft_score > 17:
            return dealer_soft_score
        if dealer_soft_score == 17 and not HIT_ON_SOFT_17:
            return 17
        if dealer_hard_score >= 17:
            return dealer_hard_score

        dealer.deal_card(shoe.pop())


def get_action(player: Player, dealer: Dealer, hand_name: str) -> str:
    hand = player.hands[hand_name]
    if player.is_human:
        print(f"Your cards are: ")
        for c in hand:
            print(c.value + c.suit, end=" ")
        print(f"Dealer has a {dealer.hand[0].value + dealer.hand[0].suit}")
        options: str = "Would you like to (H)it, (S)tand"
        if player.can_double(hand_name):
            options += ", (D)ouble"
        if player.can_split(hand_name):
            options += ", S(P)lit"
        if player.can_surrender(hand_name):
            options += " Su(R)render"
        options += ": "

        option = input(options)[0].upper()
        if option in ["H", "S"]:
            return option
        if option == "D" and player.can_double(hand_name):
            return option
        if option == "P" and player.can_split(hand_name):
            return option
        if option == "R" and player.can_surrender(hand_name):
            return option
        else:
            print("Invalid selection. Standing")
            return "S"

    return "S"


def play(player: Player, dealer: Dealer, shoe: Deck):  # noqa: C901

    winner = None
    bet: float = get_bet(player)
    insurance: float = 0.0

    HAND_NAME = "original_hand"
    local_pots: Dict[str, float] = {}
    local_pots[HAND_NAME] = bet

    player.add_hand(HAND_NAME)

    player.deal_card(HAND_NAME, shoe.pop())
    dealer.deal_card(shoe.pop())
    player.deal_card(HAND_NAME, shoe.pop())
    dealer.deal_card(shoe.pop())

    if player.is_human:
        print(f"Your cards are: ")
        for c in player.hands[HAND_NAME]:
            print(c.value + c.suit, end=" ")
        print(f"Dealer has a {dealer.hand[0].value + dealer.hand[0].suit}")

    if player.has_blackjack(HAND_NAME):
        winner = Player
        winnings = bet * (BLACKJACK_PAYOUT + 1)
        player.payout(winnings)
        return winner

    if dealer.hand[0].value == "A":
        if player.is_human and SURRENDER == "early":
            do_surrender = input("Do you wish to surrender? y/N")[0].upper()
            if do_surrender == "Y":
                winner = dealer
                player.payout(0.5 * bet)
        else:
            insurance = get_insurance(player)
            if dealer.has_blackjack():
                winner = dealer
                player.payout(insurance)

    playing = True
    while playing:
        action = get_action(player, dealer, HAND_NAME)
        if action == "H":
            player.deal_card(HAND_NAME, shoe.pop())
            if player.get_hard_score(HAND_NAME) > 21:
                winner = dealer
                playing = False

        elif action == "D":
            player.bet(bet)
            bet *= 2
            local_pots[HAND_NAME] = bet
            player.deal_card(HAND_NAME, shoe.pop())
            if player.get_hard_score(HAND_NAME) > 21:
                winner = dealer
            playing = False

        elif action == "R":
            winner = dealer
            playing = False
            player.payout(0.5 * bet)

        elif action == "P":
            local_pots.update(play_split_game(player))
            playing = False

        if action == "S":
            playing = False

    if winner is None:
        dealer_score = play_dealer_and_get_score(dealer, shoe)
        player_scores: Dict[str, int] = {}
        for hand in player.hands.keys():
            best_score = max(player.get_hard_score[hand], player.get_soft_score[hand])
            if best_score > 21:
                best_score = -1
            player_scores[hand] = best_score

        for hand, score in player_scores.items():
            if dealer_score == score:
                player.payout(local_pots[hand])
            elif dealer_score < score:
                player.payout(2 * local_pots[hand])
