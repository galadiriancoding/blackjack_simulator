from typing import List, Dict

SUITS: List[str] = ["S", "H", "D", "C"]
VALUES: List[str] = ["2", "3", "4", "5", "6", "7", "8", "T", "J", "Q", "K", "A"]

POINTS: Dict[str, int] = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 1,
}

ACTIONS: List[str] = ["hit", "stand", "double", "split", "surrender"]

ORIGINAL_HAND = "original_hand"
