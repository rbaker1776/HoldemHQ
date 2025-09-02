import random
from typing import List

class Deck:
    def __init__(self) -> None:
        self.cards = list(range(52))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> int | List[int]:
        top_cards: List[int] = [self.cards.pop(0) for _ in range(n)]
        self.cards += top_cards
        return top_cards if n > 1 else top_cards[0]

if __name__ == "__main__":
    deck: Deck = Deck()
