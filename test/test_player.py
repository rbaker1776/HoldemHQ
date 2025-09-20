import pytest
from src.core.cards import Card
from src.core.player import Player


class TestPlayer:
    def test_player_creation(self) -> None:
        player = Player(1, "Alice", 1000)

        assert player.player_id == 1
        assert player.name == "Alice"
        assert player.chips == 1000
        assert player.hole_cards == []
        assert player.current_bet == 0
        assert player.total_bet_this_hand == 0
        assert not player.is_all_in
        assert not player.is_folded
        assert not player.is_sitting_out

    def test_player_creation_default_chips(self) -> None:
        player = Player(1, "Bob")
        assert player.chips == Player.DEFAULT_CHIP_STACK

    def test_player_creation_invalid_chips(self) -> None:
        with pytest.raises(AssertionError, match="Invalid chip count"):
            Player(1, "Alice", -100)

    def test_player_creation_empty_name(self) -> None:
        with pytest.raises(AssertionError, match="Player name cannot be empty"):
            Player(1, "")

        with pytest.raises(AssertionError, match="Player name cannot be empty"):
            Player(1, "   ")

    def test_deal_hole_cards(self) -> None:
        player = Player(1, "Alice")
        cards = [Card("As"), Card("Kh")]

        player.deal_hole_cards(cards)

        assert len(player.hole_cards) == 2
        assert player.hole_cards[0].rank == "A"
        assert player.hole_cards[1].rank == "K"

    def test_deal_hole_cards_invalid_count(self) -> None:
        player = Player(1, "Alice")

        with pytest.raises(AssertionError, match="Must deal exactly 2 cards"):
            player.deal_hole_cards([Card("As")])

        with pytest.raises(AssertionError, match="Must deal exactly 2 cards"):
            player.deal_hole_cards([Card("As"), Card("Kh"), Card("Qd")])

    def test_bet_normal(self) -> None:
        """Test normal betting."""
        player = Player(1, "Alice", 1000)

        actual_bet = player.bet(100)

        assert actual_bet == 100
        assert player.chips == 900
        assert player.current_bet == 100
        assert player.total_bet_this_hand == 100
        assert not player.is_all_in

    def test_bet_all_chips(self) -> None:
        """Test betting all chips goes all-in."""
        player = Player(1, "Alice", 100)

        actual_bet = player.bet(100)

        assert actual_bet == 100
        assert player.chips == 0
        assert player.current_bet == 100
        assert player.total_bet_this_hand == 100
        assert player.is_all_in

    def test_bet_more_than_chips(self) -> None:
        """Test betting more than available chips."""
        player = Player(1, "Alice", 50)

        actual_bet = player.bet(100)

        assert actual_bet == 50  # Only bet what they have
        assert player.chips == 0
        assert player.current_bet == 50
        assert player.is_all_in

    def test_bet_invalid_amount(self) -> None:
        """Test that zero or negative bet raises error."""
        player = Player(1, "Alice", 1000)

        with pytest.raises(AssertionError, match="Bet amount must be positive"):
            player.bet(0)

        with pytest.raises(AssertionError, match="Bet amount must be positive"):
            player.bet(-10)

    def test_bet_when_folded(self) -> None:
        """Test that folded player cannot bet."""
        player = Player(1, "Alice", 1000)
        player.fold()

        with pytest.raises(AssertionError, match="Folded player cannot bet"):
            player.bet(100)

    def test_bet_when_all_in(self) -> None:
        """Test that all-in player cannot bet more."""
        player = Player(1, "Alice", 100)
        player.bet(100)  # Goes all-in

        with pytest.raises(AssertionError, match="All-in player cannot bet more"):
            player.bet(50)

    def test_call_normal(self) -> None:
        """Test normal call."""
        player = Player(1, "Alice", 1000)

        actual_call = player.call(100)

        assert actual_call == 100
        assert player.chips == 900
        assert player.current_bet == 100
        assert player.total_bet_this_hand == 100

    def test_call_partial_bet_already(self) -> None:
        """Test calling when player already has partial bet."""
        player = Player(1, "Alice", 1000)
        player.bet(30)  # Already bet 30

        actual_call = player.call(100)  # Call to 100 total

        assert actual_call == 70  # Only need 70 more
        assert player.chips == 900  # 1000 - 30 - 70
        assert player.current_bet == 100
        assert player.total_bet_this_hand == 100

    def test_call_insufficient_chips(self) -> None:
        """Test calling with insufficient chips."""
        player = Player(1, "Alice", 50)

        actual_call = player.call(100)

        assert actual_call == 50
        assert player.chips == 0
        assert player.current_bet == 50
        assert player.is_all_in

    def test_call_negative_amount(self) -> None:
        """Test that negative call amount raises error."""
        player = Player(1, "Alice", 1000)

        with pytest.raises(AssertionError, match="Call amount cannot be negative"):
            player.call(-10)

    def test_call_when_folded(self) -> None:
        """Test that folded player cannot call."""
        player = Player(1, "Alice", 1000)
        player.fold()

        with pytest.raises(AssertionError, match="Folded player cannot call"):
            player.call(100)

    def test_fold(self) -> None:
        """Test folding."""
        player = Player(1, "Alice", 1000)

        player.fold()

        assert player.is_folded

    def test_fold_already_folded(self) -> None:
        """Test that already folded player cannot fold again."""
        player = Player(1, "Alice", 1000)
        player.fold()

        with pytest.raises(AssertionError, match="Player already folded"):
            player.fold()

    def test_check(self) -> None:
        """Test checking."""
        player = Player(1, "Alice", 1000)

        player.check()  # Should not raise error

        assert not player.is_folded
        assert not player.is_all_in

    def test_check_when_folded(self) -> None:
        """Test that folded player cannot check."""
        player = Player(1, "Alice", 1000)
        player.fold()

        with pytest.raises(AssertionError, match="Folded player cannot check"):
            player.check()

    def test_check_when_all_in(self) -> None:
        """Test that all-in player cannot check."""
        player = Player(1, "Alice", 100)
        player.bet(100)  # Goes all-in

        with pytest.raises(AssertionError, match="All-in player cannot check"):
            player.check()

    def test_go_all_in(self) -> None:
        """Test going all-in."""
        player = Player(1, "Alice", 250)

        all_in_amount = player.go_all_in()

        assert all_in_amount == 250
        assert player.chips == 0
        assert player.current_bet == 250
        assert player.total_bet_this_hand == 250
        assert player.is_all_in

    def test_go_all_in_no_chips(self) -> None:
        """Test going all-in with no chips."""
        player = Player(1, "Alice", 0)

        with pytest.raises(AssertionError, match="Player has no chips"):
            player.go_all_in()

    def test_go_all_in_when_folded(self) -> None:
        """Test that folded player cannot go all-in."""
        player = Player(1, "Alice", 1000)
        player.fold()

        with pytest.raises(AssertionError, match="Folded player cannot go all-in"):
            player.go_all_in()

    def test_add_chips(self) -> None:
        """Test adding chips."""
        player = Player(1, "Alice", 1000)

        player.add_chips(500)

        assert player.chips == 1500

    def test_add_chips_negative(self) -> None:
        """Test that adding negative chips raises error."""
        player = Player(1, "Alice", 1000)

        with pytest.raises(AssertionError, match="Cannot add negative chips"):
            player.add_chips(-100)

    def test_reset(self) -> None:
        """Test resetting for new hand."""
        player = Player(1, "Alice", 1000)
        player.deal_hole_cards([Card("As"), Card("Kh")])
        player.bet(100)
        player.fold()

        player.reset()

        assert player.hole_cards == []
        assert player.current_bet == 0
        assert player.total_bet_this_hand == 0
        assert not player.is_all_in
        assert not player.is_folded
        # chips should remain unchanged
        assert player.chips == 900

    def test_can_act(self) -> None:
        """Test can_act method."""
        player = Player(1, "Alice", 1000)

        assert player.can_act()

        player.fold()
        assert not player.can_act()

        player.reset()
        assert player.can_act()

        player.bet(1000)  # Goes all-in
        assert not player.can_act()

        player.reset()
        player.add_chips(100)
        player.sit_out()
        assert not player.can_act()

    def test_has_chips(self) -> None:
        """Test has_chips method."""
        player = Player(1, "Alice", 100)

        assert player.has_chips()

        player.bet(100)  # All chips
        assert not player.has_chips()

    def test_is_active(self) -> None:
        """Test is_active method."""
        player = Player(1, "Alice", 1000)

        assert player.is_active()

        player.fold()
        assert not player.is_active()

        player.reset()
        assert player.is_active()

        player.sit_out()
        assert not player.is_active()

    def test_sit_out_sit_in(self) -> None:
        """Test sitting out and sitting back in."""
        player = Player(1, "Alice", 1000)

        assert not player.is_sitting_out

        player.sit_out()
        assert player.is_sitting_out

        player.sit_in()
        assert not player.is_sitting_out

    def test_str_representation(self) -> None:
        player = Player(1, "Alice", 1000)

        assert str(player) == "Alice (1000)"

        player.fold()
        assert "FOLDED" in str(player)

        player.reset()
        player.bet(1000)
        assert "ALL-IN" in str(player)

        player.reset()
        player.add_chips(100)
        player.sit_out()
        assert "SITTING OUT" in str(player)

    def test_repr_representation(self) -> None:
        """Test repr representation."""
        player = Player(1, "Alice", 1000)

        assert repr(player) == "Player(id=1, name='Alice', chips=1000)"

    def test_multiple_bets_same_hand(self) -> None:
        """Test multiple betting actions in same hand."""
        player = Player(1, "Alice", 1000)

        player.bet(100)
        assert player.current_bet == 100
        assert player.total_bet_this_hand == 100

        player.bet(50)  # Additional bet
        assert player.current_bet == 150
        assert player.total_bet_this_hand == 150
        assert player.chips == 850
