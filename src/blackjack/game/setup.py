from random import shuffle

from .card import Card
from .constants import SUITS, VALUES
from .custom_types import Deck
from .dealer import Dealer
from .player import Player


def build_single_deck() -> Deck:
    deck: Deck = []
    for suit in SUITS:
        for value in VALUES:
            card: Card = Card(suit, value)
            deck.append(card)
    shuffle(deck)
    return deck


def build_shoe(deck_count: int) -> Deck:
    shoe: Deck = []
    for _ in range(deck_count):
        deck: Deck = build_single_deck()
        shoe.extend(deck)
    shuffle(shoe)
    return shoe


def discard_all_cards(player: Player, dealer: Dealer, discard_pile: Deck) -> Deck:
    discard_pile.extend(dealer.hand)
    dealer.clear_hand()
    for hand in player.hands.values():
        discard_pile.extend(hand)
    player.clear_hands()
    return discard_pile
