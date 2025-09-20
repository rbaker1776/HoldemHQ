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

    def deal_to_hand(self, hand: "Hand", count: int = 1) -> None:
        """Deal cards directly to a hand."""
        cards = self.deal(count)
        hand.extend(cards)
    
    def deal_hand(self, count: int = 1) -> "Hand":
        """Deal cards and return a new Hand object."""
        cards = self.deal(count)
        return Hand(cards)
    
    def deal_one(self) -> Card:
        """Deal a single card (for backward compatibility)."""
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
    def __init__(self, cards: list[Card] = None) -> None:
        self.cards: list[Card] = cards.copy() if cards else []

    def append(self, card: Card) -> None:
        self.cards.append(card)
    
    def extend(self, cards: list[Card]) -> None:
        """Add multiple cards to the hand."""
        self.cards.extend(cards)
    
    def remove(self, card: Card) -> None:
        """Remove a specific card from the hand."""
        self.cards.remove(card)
    
    def pop(self, index: int = -1) -> Card:
        """Remove and return a card at the given index (last by default)."""
        return self.cards.pop(index)

    def reset(self) -> None:
        self.cards.clear()
    
    def copy(self) -> "Hand":
        """Create a copy of the hand."""
        return Hand(self.cards)
    
    def sort(self, reverse: bool = False) -> None:
        """Sort cards by rank."""
        self.cards.sort(reverse=reverse)
    
    def sorted(self, reverse: bool = False) -> "Hand":
        """Return a new sorted hand without modifying the original."""
        new_hand = self.copy()
        new_hand.sort(reverse=reverse)
        return new_hand
    
    def to_list(self) -> list[Card]:
        """Convert hand to a list of cards (for compatibility)."""
        return self.cards.copy()
    
    def value(self) -> int:
        """Evaluate the hand and return its numeric value."""
        from .evaluator import evaluate_hand
        return evaluate_hand(self.cards)
    
    def description(self) -> str:
        """Get a human-readable description of the hand."""
        from .evaluator import get_hand_description
        return get_hand_description(self.cards)
    
    def best_five_cards(self) -> "Hand":
        """Return the best 5-card hand from this hand.
        
        For hands with more than 5 cards, this evaluates all possible
        5-card combinations and returns the best one.
        """
        if len(self.cards) <= 5:
            return self.copy()
        
        from itertools import combinations
        from .evaluator import evaluate_hand
        
        best_score = float('inf')
        best_hand = None
        
        for combo in combinations(self.cards, 5):
            score = evaluate_hand(list(combo))
            if score < best_score:  # Lower scores are better
                best_score = score
                best_hand = list(combo)
        
        return Hand(best_hand) if best_hand else Hand()
    
    def __len__(self) -> int:
        return len(self.cards)

    def __bool__(self) -> bool:
        return len(self.cards) > 0

    def __iter__(self):
        return iter(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    def __setitem__(self, index, value):
        self.cards[index] = value
    
    def __contains__(self, card: Card) -> bool:
        return card in self.cards
    
    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)

    def __repr__(self) -> str:
        return f"Hand({len(self.cards)} cards: {str(self)})"
