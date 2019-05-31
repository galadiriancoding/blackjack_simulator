from .constants import SUITS, VALUES
from .card import Card
from .custom_types import Deck
from random import shuffle
from .settings import DECK_COUNT
from .player import Player
from .dealer import Dealer


def build__single_deck() -> Deck:
    deck: Deck = []
    for suit in SUITS:
        for value in VALUES:
            card: Card = Card(suit, value)
            deck.append(card)
    shuffle(deck)
    return deck


def build_shoe() -> Deck:
    shoe: Deck = []
    for _ in range(DECK_COUNT):
        deck = build__single_deck()
        shoe.extend(deck)
    shuffle(shoe)
    return shoe


def discard_all_cards(player: Player, dealer: Dealer, discard_pile: Deck) -> Deck:
    discard_pile.extend(dealer.hand)
    dealer.clear_hand()
    for hand in player.hands.values():
        discard_pile.extend(hand)
    player.clear_hands()
