import pytest
from src.core.player import Player
from src.core.betting import BettingManager, SidePot, BettingAction


class TestBettingManager:
    def create_players(self, count: int = 3) -> list[Player]:
        return [Player(i, f"Player{i}", 1000) for i in range(count)]

    def test_betting_manager_creation(self) -> None:
        manager = BettingManager()

        assert manager.main_pot == 0
        assert len(manager.side_pots) == 0
        assert manager.current_bet == 0
        assert len(manager.betting_history) == 0
        assert len(manager.player_investments) == 0

    def test_start_new_hand(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # Add some state
        manager.post_blind(player, 10)
        assert manager.main_pot > 0

        manager.start_new_hand()

        assert manager.main_pot == 0
        assert len(manager.side_pots) == 0
        assert manager.current_bet == 0
        assert len(manager.betting_history) == 0
        assert len(manager.player_investments) == 0

    def test_start_new_betting_round(self) -> None:
        manager = BettingManager()
        manager.main_pot = 100

        manager.start_new_betting_round()

        assert manager.current_bet == 0
        assert manager.main_pot == 100  # Pot preserved

    def test_post_blind_small(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.post_blind(player, 5, is_big_blind=False)

        assert actual == 5
        assert manager.main_pot == 5
        assert manager.current_bet == 5
        assert manager.player_investments[1] == 5
        assert len(manager.betting_history) == 1
        assert manager.betting_history[0].action_type == "small_blind"

    def test_post_blind_big(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.post_blind(player, 10, is_big_blind=True)

        assert actual == 10
        assert manager.main_pot == 10
        assert manager.current_bet == 10
        assert manager.player_investments[1] == 10
        assert manager.betting_history[0].action_type == "big_blind"

    def test_post_blind_insufficient_chips(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 5)  # Only 5 chips

        actual = manager.post_blind(player, 10, is_big_blind=True)

        assert actual == 5  # Only what player had
        assert manager.main_pot == 5
        assert manager.current_bet == 5
        assert player.chips == 0
        assert player.is_all_in

    def test_process_fold(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        manager.process_fold(player)

        assert player.is_folded
        assert len(manager.betting_history) == 1
        assert manager.betting_history[0].action_type == "fold"
        assert manager.betting_history[0].amount == 0

    def test_process_check_valid(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        result = manager.process_check(player)

        assert result is True
        assert len(manager.betting_history) == 1
        assert manager.betting_history[0].action_type == "check"

    def test_process_check_invalid(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)
        manager.current_bet = 1

        result = manager.process_check(player)

        assert result is False
        assert len(manager.betting_history) == 0

    def test_process_call_valid(self) -> None:
        manager = BettingManager()
        manager.current_bet = 50
        player = Player(1, "Alice", 1000)

        actual = manager.process_call(player)

        assert actual == 50
        assert manager.main_pot == 50
        assert player.current_bet == 50
        assert player.chips == 950
        assert manager.player_investments[1] == 50

    def test_process_call_no_bet(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.process_call(player)

        assert actual == 0
        assert manager.main_pot == 0

    def test_process_call_partial_bet(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)
        player.bet(20)  # Player already bet 20

        manager.current_bet = 50
        actual = manager.process_call(player)

        assert actual == 30  # Only need 30 more to call 50
        assert player.current_bet == 50

    def test_process_bet_valid(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.process_bet(player, 100)

        assert actual == 100
        assert manager.main_pot == 100
        assert manager.current_bet == 100
        assert player.current_bet == 100
        assert player.chips == 900

    def test_process_bet_invalid(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)
        manager.current_bet = 1

        actual = manager.process_bet(player, 100)

        assert actual == 0
        assert manager.main_pot == 0

    def test_process_raise_valid(self) -> None:
        manager = BettingManager()
        manager.current_bet = 50
        player = Player(1, "Alice", 1000)

        actual = manager.process_raise(player, 100)

        assert actual == 100
        assert manager.main_pot == 100
        assert manager.current_bet == 100
        assert player.current_bet == 100

    def test_process_raise_no_bet(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.process_raise(player, 100)

        assert actual == 0

    def test_process_raise_too_small(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        actual = manager.process_raise(player, 90)

        assert actual == 0

    def test_process_all_in(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 250)

        actual = manager.process_all_in(player)

        assert actual == 250
        assert manager.main_pot == 250
        assert manager.current_bet == 250  # All-in raised the bet
        assert player.chips == 0
        assert player.is_all_in

    def test_process_all_in_no_chips(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 0)

        actual = manager.process_all_in(player)

        assert actual == 0

    def test_process_all_in_not_raise(self) -> None:
        manager = BettingManager()
        manager.current_bet = 100
        player = Player(1, "Alice", 50)

        actual = manager.process_all_in(player)

        assert actual == 50
        assert manager.current_bet == 100

    def test_calculate_side_pots_no_all_ins(self) -> None:
        manager = BettingManager()
        players = self.create_players(3)
        manager.main_pot = 150

        side_pots = manager.calculate_side_pots(players)

        assert len(side_pots) == 1
        assert side_pots[0].amount == 150
        assert side_pots[0].player_indices == [0, 1, 2]

    def test_calculate_side_pots_with_all_ins(self) -> None:
        manager = BettingManager()
        players = self.create_players(3)

        # Player 0 goes all-in for 100
        players[0].chips = 100
        manager.process_all_in(players[0])
        manager.player_investments[0] = 100

        # Player 1 calls 200
        manager.player_investments[1] = 200

        # Player 2 calls 200
        manager.player_investments[2] = 200

        side_pots = manager.calculate_side_pots(players)

        # Should have 2 side pots:
        # Main pot: 100 * 3 = 300 (all 3 eligible)
        # Side pot: 100 * 2 = 200 (only players 1,2 eligible)
        assert len(side_pots) == 2
        assert side_pots[0].amount == 300
        assert set(side_pots[0].player_indices) == {0, 1, 2}
        assert side_pots[1].amount == 200
        assert set(side_pots[1].player_indices) == {1, 2}

    def test_distribute_winnings_single_pot(self) -> None:
        manager = BettingManager()
        side_pots = [SidePot(300, [1, 2, 3])]
        winners_by_pot = [[2]]  # Player 2 wins

        winnings = manager.distribute_winnings(winners_by_pot, side_pots)

        assert winnings == {2: 300}

    def test_distribute_winnings_multiple_winners(self) -> None:
        manager = BettingManager()
        side_pots = [SidePot(300, [1, 2, 3])]
        winners_by_pot = [[1, 2]]  # Players 1 and 2 tie

        winnings = manager.distribute_winnings(winners_by_pot, side_pots)

        assert winnings == {1: 150, 2: 150}

    def test_distribute_winnings_with_remainder(self) -> None:
        manager = BettingManager()
        side_pots = [SidePot(301, [1, 2, 3])]
        winners_by_pot = [[1, 2, 3]]  # Three-way tie

        winnings = manager.distribute_winnings(winners_by_pot, side_pots)

        # 301 / 3 = 100 each, remainder 1 goes to first winner
        assert winnings == {1: 101, 2: 100, 3: 100}

    def test_distribute_winnings_multiple_pots(self) -> None:
        manager = BettingManager()
        side_pots = [
            SidePot(300, [1, 2, 3]),  # Main pot
            SidePot(200, [2, 3]),  # Side pot
        ]
        winners_by_pot = [
            [2],  # Player 2 wins main pot
            [3],  # Player 3 wins side pot
        ]

        winnings = manager.distribute_winnings(winners_by_pot, side_pots)

        assert winnings == {2: 300, 3: 200}

    def test_get_total_pot(self) -> None:
        manager = BettingManager()
        manager.main_pot = 100
        manager.side_pots = [SidePot(50, [1, 2]), SidePot(30, [1])]

        total = manager.get_total_pot()

        assert total == 180

    def test_get_pot_info(self) -> None:
        manager = BettingManager()
        manager.main_pot = 100
        manager.side_pots = [SidePot(75, [1, 2])]

        info = manager.get_pot_info()

        assert info["main_pot"] == 100
        assert info["side_pots"] == 1
        assert info["total_pot"] == 175
        assert info["current_bet"] == 0
        assert len(info["side_pot_details"]) == 1

    def test_get_player_investment(self) -> None:
        manager = BettingManager()
        manager.player_investments[1] = 150

        investment = manager.get_player_investment(1)

        assert investment == 150

    def test_get_player_investment_none(self) -> None:
        manager = BettingManager()

        investment = manager.get_player_investment(999)

        assert investment == 0

    def test_get_betting_history(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        manager.process_fold(player)

        history = manager.get_betting_history()

        assert len(history) == 1
        assert isinstance(history[0], BettingAction)
        assert history[0].action_type == "fold"

    def test_get_action_summary(self) -> None:
        manager = BettingManager()
        players = self.create_players(2)

        manager.process_bet(players[0], 50)
        manager.process_call(players[1])

        summary = manager.get_action_summary()

        assert summary["total_actions"] == 2
        assert summary["actions_by_type"]["bet"] == 1
        assert summary["actions_by_type"]["call"] == 1
        assert summary["total_invested"] == 100

    def test_can_player_check(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # Can check when no bet
        assert manager.can_player_check(player) is True

        # Cannot check when bet exists
        manager.current_bet = 1
        assert manager.can_player_check(player) is False

        # Cannot check when folded
        player.fold()
        assert manager.can_player_check(player) is False

    def test_can_player_call(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # Cannot call when no bet
        assert manager.can_player_call(player) is False

        # Can call when bet exists
        manager.current_bet = 1
        assert manager.can_player_call(player) is True

        # Cannot call if already called full amount
        player.bet(50)
        assert manager.can_player_call(player) is False

    def test_can_player_bet(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # Can bet when no current bet
        assert manager.can_player_bet(player) is True

        # Cannot bet when bet already exists
        manager.current_bet = 1
        assert manager.can_player_bet(player) is False

        # Cannot bet with no chips
        player.chips = 0
        assert manager.can_player_bet(player) is False

    def test_can_player_raise(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # Cannot raise when no bet
        assert manager.can_player_raise(player) is False

        # Can raise when bet exists
        manager.current_bet = 1
        assert manager.can_player_raise(player) is True

        # Cannot raise with no chips
        player.chips = 0
        assert manager.can_player_raise(player) is False

    def test_get_minimum_raise(self) -> None:
        manager = BettingManager()

        # No minimum when no bet
        assert manager.get_minimum_raise() == 0

        # Minimum is double current bet
        manager.current_bet = 50
        assert manager.get_minimum_raise() == 100

    def test_get_call_amount(self) -> None:
        manager = BettingManager()
        player = Player(1, "Alice", 1000)

        # No call needed when no bet
        assert manager.get_call_amount(player) == 0

        # Full amount when no partial bet
        manager.current_bet = 50
        assert manager.get_call_amount(player) == 50

        # Partial amount when player has partial bet
        player.bet(20)
        assert manager.get_call_amount(player) == 30

    def test_is_betting_capped(self) -> None:
        manager = BettingManager()
        players = self.create_players(3)

        # Not capped with multiple players with chips
        assert manager.is_betting_capped(players) is False

        # Capped when only one player has chips
        players[0].chips = 0
        players[1].chips = 0
        assert manager.is_betting_capped(players) is True

        # Capped when all but one are all-in
        players[1].chips = 100
        players[1].is_all_in = True
        assert manager.is_betting_capped(players) is True

    def test_betting_manager_repr(self) -> None:
        manager = BettingManager()
        manager.main_pot = 150
        player = Player(1, "Alice", 1000)
        manager.process_bet(player, 50)

        repr_str = repr(manager)

        assert "BettingManager" in repr_str
        assert "pot=200" in repr_str  # 150 + 50
        assert "current_bet=50" in repr_str
        assert "actions=1" in repr_str

    def test_side_pot_repr(self) -> None:
        pot = SidePot(300, [1, 2, 3])

        repr_str = repr(pot)

        assert "SidePot" in repr_str
        assert "amount=300" in repr_str
        assert "players=3" in repr_str

    def test_betting_action_repr(self) -> None:
        action = BettingAction(1, "bet", 50, 50)

        repr_str = repr(action)

        assert "BET(50)" in repr_str
        assert "Player 1" in repr_str

    def test_complex_betting_scenario(self) -> None:
        manager = BettingManager()
        players = self.create_players(3)

        # Post blinds
        manager.post_blind(players[0], 5, is_big_blind=False)
        manager.post_blind(players[1], 10, is_big_blind=True)

        # Player 2 calls
        manager.process_call(players[2])

        # Player 0 raises
        manager.process_raise(players[0], 30)

        # Player 1 folds
        manager.process_fold(players[1])

        # Player 2 calls
        manager.process_call(players[2])

        assert manager.main_pot == 70  # 5 + 10 + 10 + 25 + 20
        assert manager.current_bet == 30
        assert len(manager.betting_history) == 6
        assert players[1].is_folded
