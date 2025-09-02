import random
from typing import List

class Card:
    def __init__(self, n: int) -> None:
        self.n: int = n

    def __repr__(self) -> str:
        suits: list[str] = ["♠︎", "❤︎", "♦︎", "♣︎"]
        ranks: list[str] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        return ranks[self.n % 13] + suits[self.n // 13]

class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = [Card(n) for n in range(52)]
        self.shuffle()

    def shuffle(self):
        self.cards: List[Card] = [Card(n) for n in range(52)]
        random.shuffle(self.cards)

    def draw_cards(self, n: int = 1) -> List[Card]:
        top_cards: List[Card] = [self.cards.pop(0) for _ in range(n)]
        return top_cards

    def draw_card(self) -> Card:
        return self.draw_cards(1)[0]

    def __len__(self) -> int:
        return len(self.cards)

if __name__ == "__main__":
    deck: Deck = Deck()
