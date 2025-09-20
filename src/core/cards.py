import random
from typing import Optional, Iterator


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

    def value(self) -> int:
        return self.RANKS.index(self.rank)

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return f"Card('{self.rank}{self.suit}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.value() == other.value()

    def __lt__(self, other: "Card") -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.value() < other.value()


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

    def deal_to_hand(self, hand: "Hand", count: int = 1) -> None:
        cards = self.deal(count)
        hand.extend(cards)

    def deal_hand(self, count: int = 1) -> "Hand":
        cards = self.deal(count)
        return Hand(cards)

    def deal_one(self) -> Card:
        return self.deal(1)[0]

    def reset(self, shuffled: bool = True) -> None:
        self._init_deck()
        if shuffled:
            self.shuffle()

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self) -> str:
        return f"Deck({len(self.cards)} cards)"


class Hand:
    def __init__(self, cards: list[Card] = []) -> None:
        self.cards: list[Card] = cards.copy() if cards else []

    def append(self, card: Card) -> None:
        self.cards.append(card)

    def extend(self, cards: list[Card]) -> None:
        self.cards.extend(cards)

    def reset(self) -> None:
        self.cards.clear()

    def copy(self) -> "Hand":
        return Hand(self.cards)

    def value(self) -> int:
        from .evaluator import evaluate_hand

        return evaluate_hand(self.cards)

    def __add__(self, other: "Hand") -> "Hand":
        return Hand(self.cards + other.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self.cards)

    def __getitem__(self, index: int) -> Card:
        return self.cards[index]

    def __setitem__(self, index: int, value: Card) -> None:
        self.cards[index] = value

    def __contains__(self, card: Card) -> bool:
        return card in self.cards

    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)

    def __repr__(self) -> str:
        return f"Hand({len(self.cards)} cards: {str(self)})"
