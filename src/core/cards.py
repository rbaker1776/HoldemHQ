import random
from typing import Optional


class Card:
    RANKS: str = "23456789TJQKA"
    SUITS: str = "shdc"

    def __init__(self, rank: str = "", suit: str = "") -> None:
        # Support both Card("Q", "d") and Card("Qd") formats
        if suit == "" and len(rank) == 2:  # Parse "Qd" format
            self.rank = rank[0]
            self.suit = rank[1]
        else:  # Use separate rank and suit
            self.rank = rank
            self.suit = suit

        assert self.rank in self.RANKS, f"Invalid rank: {self.rank}"
        assert self.suit in self.SUITS, f"Invalid suit: {self.suit}"

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return f"Card('{self.rank}{self.suit}')"

    def __abs__(self) -> int:
        return self.RANKS.index(self.rank)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank

    def __lt__(self, other: "Card") -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.__abs__() < other.__abs__()

    def __hash__(self) -> int:
        return hash(self.rank)


class Deck:
    def __init__(self, shuffled: bool = True) -> None:
        self._init_deck()
        if shuffled:
            self.shuffle()

    def _init_deck(self) -> None:
        self.cards: list[Card] = [
            Card(rank, suit) for rank in Card.RANKS for suit in Card.SUITS
        ]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, count: int = 1) -> list[Card]:
        assert count <= len(self.cards), (
            f"Cannot deal {count} card(s), only {len(self.cards)} remaining"
        )
        dealt_cards = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt_cards

    def deal_one(self) -> Card:
        return self.deal(1)[0]

    def reset(self, shuffled: bool = True) -> None:
        self._init_deck()
        if shuffled:
            self.shuffle()

    def __len__(self) -> int:
        return len(self.cards)

    def __bool__(self) -> bool:
        return self.__len__() > 0

    def __repr__(self) -> str:
        return f"Deck({len(self.cards)} cards)"


class Hand:
    def __init__(self) -> None:
        self.cards: list[Card] = []

    def append(self, card: Card) -> None:
        self.cards.append(card)

    def reset(self) -> None:
        self.cards.clear()

    def __len__(self) -> int:
        return len(self.cards)

    def __bool__(self) -> bool:
        return self.__len__() > 0

    def __repr__(self) -> str:
        return f"Hand({len(self.cards)} cards)"
