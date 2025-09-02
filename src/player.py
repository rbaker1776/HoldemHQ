from src.cards import Card
from typing import List

class Player:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.hand: List[Card] = []

    def deal_cards(self, cards: List[Card]) -> None:
        self.hand += cards

    def reset(self) -> None:
        self.hand.clear()
