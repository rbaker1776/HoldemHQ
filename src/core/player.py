from src.core.cards import Card


class Player:
    def __init__(self, player_id: int, name: str, chips: int) -> None:
        assert chips >= 0, f"Invalid chip count: {chips}"
        assert len(name.strip()) > 0, "Player name cannot be empty"

        self.player_id: int = player_id
        self.name: str = name.strip()
        self.chips: int = chips
        self.hole_cards: list[Card] = []
        self.current_bet: int = 0
        self.total_bet_this_hand: int = 0
        self.is_all_in: bool = False
        self.is_folded: bool = False
        self.is_sitting_out: bool = False

    def deal_hole_cards(self, cards: List[Card]) -> None:
        assert len(cards) == 2, f"Must deal exactly 2 cards, got {len(cards)}"
        self.hole_cards = cards.copy()

    def bet(self, amount: int) -> int:
        assert amount > 0, f"Bet amount must be positive: {amount}"
        assert not self.is_folded, "Folded player cannot bet"
        assert not self.is_all_in, "All-in player cannot bet more"
        assert not self.is_sitting_out, "Away player cannot bet"
        
        actual_bet: int = min(amount, self.chips)
        
        self.chips -= actual_bet
        self.current_bet += actual_bet
        self.total_bet_this_hand += actual_bet
        self.is_all_in = self.chips == 0
        
        return actual_bet

    def call(self, call_amount: int) -> int:
        assert call_amount >= 0, f"Call amount cannot be negative: {call_amount}"
        assert not self.is_folded, "Folded player cannot call"
        assert not self.is_sitting_out, "Away player cannot call"
        
        needed: int = max(0, call_amount - self.current_bet)
        actual_call: int = min(needed, self.chips)
        
        self.chips -= actual_call
        self.current_bet += actual_call
        self.total_bet_this_hand += actual_call
        self.is_all_in = self.chips == 0
        
        return actual_call

    def fold(self) -> None:
        assert not self.is_folded, "Player already folded"
        assert not self.is_sitting_out, "Away player cannot fold"
        self.is_folded = True

    def check(self) -> None:
        assert not self.is_folded, "Folded player cannot check"
        assert not self.is_all_in, "All-in player cannot check"
        assert not self.is_sitting_out, "Away player cannot check"

    def go_all_in(self) -> int:
        assert not self.is_folded, "Folded player cannot go all-in"
        assert self.chips > 0, "Player has no chips to go all-in"
        return self.bet(self.chips)

    def add_chips(self, amount: int) -> None:
        assert amount > 0, f"Cannot add negative chips: {amount}"
        self.chips += amount

    def reset(self) -> None:
        self.hole_cards.clear()
        self.current_bet = 0
        self.total_bet_this_hand = 0
        self.is_all_in = False
        self.is_folded = False

    def can_act(self) -> bool:
        return not self.is_folded and not self.is_all_in and not self.is_sitting_out

    def has_chips(self) -> bool:
        return self.chips > 0

    def is_active(self) -> bool:
        return not self.is_folded and not self.is_sitting_out

    def sit_out(self) -> None:
        self.is_sitting_out = True
    
    def sit_in(self) -> None:
        self.is_sitting_out = False

    def __str__(self) -> str:
        status = []
        if self.is_folded:
            status.append("FOLDED")
        if self.is_all_in:
            status.append("ALL-IN")
        if self.is_sitting_out:
            status.append("SITTING OUT")
        
        status_str = f" ({', '.join(status)})" if status else ""
        return f"{self.name}: ${self.chips}{status_str}"
    
    def __repr__(self) -> str:
        return f"Player(id={self.player_id}, name='{self.name}', chips={self.chips})"
