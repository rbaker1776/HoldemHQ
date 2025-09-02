from src.player import Player
from src.card_deck import CardDeck
from typing import List

class HoldemGame:
    def __init__(self, players: List[Player]) -> None:
        self.players: List[Player] = players
        self.deck: CardDeck = CardDeck()
