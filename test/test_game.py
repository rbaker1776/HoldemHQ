import pytest
from src.core.cards import Card
from src.core.player import Player
from src.core.game import Game, GamePhase, GameAction


class TestGame:
    def create_players(self, count: int = 3) -> list[Player]:
        return [Player(i, f"Player{i}", 1000) for i in range(count)]

    def test_game_creation(self) -> None:
        players = self.create_players(3)
        game = Game(players, small_blind=5, big_blind=10)

        assert len(game.players) == 3
        assert game.small_blind == 5
        assert game.big_blind == 10
        assert game.phase == GamePhase.PREFLOP
        assert game.pot == 0
        assert game.current_bet == 0
        assert game.dealer_position == 0
        assert len(game.board) == 0

    def test_game_creation_invalid_player_count(self) -> None:
        with pytest.raises(AssertionError, match="Invalid player count"):
            Game([Player(0, "Alice")], 1, 2)

        players = self.create_players(11)
        with pytest.raises(AssertionError, match="Invalid player count"):
            Game(players, 1, 2)

    def test_game_creation_invalid_blinds(self) -> None:
        players = self.create_players(3)

        with pytest.raises(AssertionError, match="Invalid blinds"):
            Game(players, -1, 2)

        with pytest.raises(AssertionError, match="Invalid blinds"):
            Game(players, 5, 0)

        with pytest.raises(AssertionError, match="Invalid blinds"):
            Game(players, 10, 5)

    def test_start_new_hand(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        # Simulate some previous state
        game.board = [Card("A", "s")]
        game.phase = GamePhase.FLOP
        game.pot = 100

        game.start_new_hand()

        assert game.phase == GamePhase.PREFLOP
        assert len(game.board) == 0
        assert game.pot == 15  # Should have blinds posted
        assert game.current_bet == 10  # Big blind amount
        assert game.dealer_position == 1  # Moved from 0

    def test_blinds_posting_three_players(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.dealer_position = 0

        game.start_new_hand()

        # With 3 players: dealer=1, small=2, big=0
        assert players[2].current_bet == 5  # Small blind
        assert players[0].current_bet == 10  # Big blind
        assert players[1].current_bet == 0  # No blind
        assert game.pot == 15

    def test_blinds_posting_heads_up(self) -> None:
        players = self.create_players(2)
        game = Game(players, 5, 10)
        game.dealer_position = 0

        game.start_new_hand()

        # Heads up: dealer posts small blind
        assert players[1].current_bet == 5  # Dealer = small blind
        assert players[0].current_bet == 10  # Other = big blind
        assert game.pot == 15

    def test_deal_hole_cards(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        game.deal_hole_cards()

        for player in players:
            assert len(player.hole_cards) == 2

        # Should have dealt 6 cards total
        assert len(game.deck) == 46  # 52 - 6 dealt

    def test_deal_hole_cards_wrong_phase(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.phase = GamePhase.FLOP

        with pytest.raises(AssertionError, match="Can only deal hole cards preflop"):
            game.deal_hole_cards()

    def test_advance_phase_preflop_to_flop(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        game.advance_phase()

        assert game.phase == GamePhase.FLOP
        assert len(game.board) == 3
        assert game.current_bet == 0  # Reset for new betting round

    def test_advance_phase_flop_to_turn(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.phase = GamePhase.FLOP
        game.board = [Card("A", "s"), Card("K", "h"), Card("Q", "d")]

        game.advance_phase()

        assert game.phase == GamePhase.TURN
        assert len(game.board) == 4

    def test_advance_phase_turn_to_river(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.phase = GamePhase.TURN
        game.board = [Card("A", "s"), Card("K", "h"), Card("Q", "d"), Card("J", "c")]

        game.advance_phase()

        assert game.phase == GamePhase.RIVER
        assert len(game.board) == 5

    def test_advance_phase_river_to_showdown(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.phase = GamePhase.RIVER

        game.advance_phase()

        assert game.phase == GamePhase.SHOWDOWN

    def test_advance_phase_showdown_to_finished(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.phase = GamePhase.SHOWDOWN

        game.advance_phase()

        assert game.phase == GamePhase.FINISHED

    def test_get_active_players(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        active = game.get_active_players()
        assert active == [0, 1, 2]

        players[1].fold()
        active = game.get_active_players()
        assert active == [0, 2]

        players[0].sit_out()
        active = game.get_active_players()
        assert active == [2]

    def test_can_check(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 0

        assert game.can_check(0)

        game.current_bet = 10
        assert not game.can_check(0)  # Cannot check with bet to call

        players[0].fold()
        game.current_bet = 0
        assert not game.can_check(0)  # Folded player cannot check

    def test_can_call(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        game.current_bet = 10
        assert game.can_call(0)

        game.current_bet = 0
        assert not game.can_call(0)  # No bet to call

        players[0].fold()
        game.current_bet = 10
        assert not game.can_call(0)  # Folded player cannot call

    def test_can_bet(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 0

        assert game.can_bet(0)

        game.current_bet = 10
        assert not game.can_bet(0)  # Cannot bet when there's a bet to call

        players[0].chips = 0
        game.current_bet = 0
        assert not game.can_bet(0)  # No chips to bet

    def test_can_raise(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        game.current_bet = 10
        assert game.can_raise(0)

        game.current_bet = 0
        assert not game.can_raise(0)  # No bet to raise

        players[0].chips = 0
        game.current_bet = 10
        assert not game.can_raise(0)  # No chips to raise

    def test_process_action_fold(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.start_new_hand()
        game.current_player = 0

        success = game.process_action(0, GameAction.FOLD)

        assert success
        assert players[0].is_folded

    def test_process_action_check(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 0
        game.current_player = 0

        success = game.process_action(0, GameAction.CHECK)

        assert success
        assert not players[0].is_folded

    def test_process_action_call(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 50
        game.current_player = 0
        initial_pot = game.pot

        success = game.process_action(0, GameAction.CALL)

        assert success
        assert players[0].current_bet == 50
        assert players[0].chips == 950
        assert game.pot == initial_pot + 50

    def test_process_action_bet(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 0
        game.current_player = 0
        initial_pot = game.pot

        success = game.process_action(0, GameAction.BET, 100)

        assert success
        assert players[0].current_bet == 100
        assert players[0].chips == 900
        assert game.current_bet == 100
        assert game.pot == initial_pot + 100
        assert game.last_raiser == 0

    def test_process_action_raise(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_bet = 50
        game.current_player = 0
        initial_pot = game.pot

        success = game.process_action(0, GameAction.RAISE, 100)

        assert success
        assert players[0].current_bet == 100
        assert players[0].chips == 900
        assert game.current_bet == 100
        assert game.pot == initial_pot + 100
        assert game.last_raiser == 0

    def test_process_action_all_in(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_player = 0
        initial_pot = game.pot

        success = game.process_action(0, GameAction.ALL_IN)

        assert success
        assert players[0].is_all_in
        assert players[0].chips == 0
        assert game.pot == initial_pot + 1000

    def test_process_action_wrong_player(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_player = 0

        with pytest.raises(AssertionError, match="Not player 1's turn"):
            game.process_action(1, GameAction.CHECK)

    def test_process_action_inactive_player(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.current_player = 0
        players[0].fold()

        with pytest.raises(AssertionError, match="Player 0 not active"):
            game.process_action(0, GameAction.CHECK)

    def test_evaluate_hands(self) -> None:
        players = self.create_players(2)
        game = Game(players, 5, 10)

        # Give players hole cards
        players[0].deal_hole_cards([Card("A", "s"), Card("A", "h")])  # Pocket aces
        players[1].deal_hole_cards([Card("K", "s"), Card("K", "h")])  # Pocket kings

        # Set community cards
        game.board = [
            Card("A", "d"),
            Card("K", "d"),
            Card("Q", "c"),
            Card("J", "s"),
            Card("9", "h"),
        ]

        results = game.evaluate_hands()

        assert len(results) == 2
        player0_score = next(score for player_idx, score in results if player_idx == 0)
        player1_score = next(score for player_idx, score in results if player_idx == 1)

        assert player0_score < player1_score

    def test_determine_winner(self) -> None:
        players = self.create_players(2)
        game = Game(players, 5, 10)

        # Give players hole cards
        players[0].deal_hole_cards([Card("A", "s"), Card("A", "h")])
        players[1].deal_hole_cards([Card("K", "s"), Card("K", "h")])

        # Set community cards for straight
        game.board = [
            Card("7", "d"),
            Card("J", "d"),
            Card("T", "c"),
            Card("9", "s"),
            Card("8", "h"),
        ]

        winners = game.determine_winner()

        assert len(winners) == 2  # Both have same straight

    def test_distribute_pot_single_winner(self) -> None:
        players = self.create_players(2)
        game = Game(players, 5, 10)
        game.pot = 200

        game.distribute_pot([0])

        assert players[0].chips == 1200  # 1000 + 200
        assert players[1].chips == 1000  # Unchanged
        assert game.pot == 0

    def test_distribute_pot_multiple_winners(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.pot = 200

        game.distribute_pot([0, 1])

        assert players[0].chips == 1100  # 1000 + 100
        assert players[1].chips == 1100  # 1000 + 100
        assert players[2].chips == 1000  # Unchanged
        assert game.pot == 0

    def test_distribute_pot_with_remainder(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.pot = 101  # Odd amount

        game.distribute_pot([0, 1, 2])

        # 101 / 3 = 33 each, remainder 2 goes to first winners
        assert players[0].chips == 1034  # 1000 + 33 + 1
        assert players[1].chips == 1034  # 1000 + 33 + 1
        assert players[2].chips == 1033  # 1000 + 33
        assert game.pot == 0

    def test_is_betting_round_complete_all_folded_but_one(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        players[0].fold()
        players[1].fold()

        assert game.is_betting_round_complete()

    def test_is_betting_round_complete_everyone_acted(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.players_acted = {0, 1, 2}

        assert game.is_betting_round_complete()

    def test_is_betting_round_complete_not_everyone_acted(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.players_acted = {0, 1}  # Player 2 hasn't acted

        assert not game.is_betting_round_complete()

    def test_is_betting_round_complete_return_to_raiser(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.players_acted = {0, 1, 2}
        game.last_raiser = 1
        game.current_player = 1

        assert game.is_betting_round_complete()

    def test_is_betting_round_complete_not_returned_to_raiser(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.players_acted = {0, 1, 2}
        game.last_raiser = 1
        game.current_player = 2  # Action hasn't returned to raiser

        assert not game.is_betting_round_complete()

    def test_betting_round_integration(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.start_new_hand()

        initial_pot = game.pot
        assert game.current_bet == 10

        game.process_action(game.current_player, GameAction.CALL, 10)
        game.process_action(game.current_player, GameAction.CALL, 5)
        game.process_action(game.current_player, GameAction.CHECK, is_bb=True)

        assert game.pot == initial_pot + 15

    def test_all_in_affects_current_bet(self) -> None:
        players = self.create_players(2)
        players[0].chips = 150  # Less than others
        game = Game(players, 5, 10)
        game.current_bet = 100
        game.current_player = 0

        game.process_action(0, GameAction.ALL_IN)

        assert game.current_bet == 150  # All-in amount becomes new bet
        assert game.last_raiser == 0

    def test_all_in_doesnt_affect_current_bet(self) -> None:
        players = self.create_players(2)
        players[0].chips = 50  # Less than current bet
        game = Game(players, 5, 10)
        game.current_bet = 100
        game.current_player = 0

        game.process_action(0, GameAction.ALL_IN)

        assert game.current_bet == 100  # Unchanged
        assert game.last_raiser is None  # No raise

    def test_player_sitting_out_not_active(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        players[1].sit_out()
        active = game.get_active_players()

        assert active == [0, 2]

    def test_advance_to_next_active_player(self) -> None:
        players = self.create_players(4)
        game = Game(players, 5, 10)
        game.current_player = 0

        # Fold players 1 and 2
        players[1].fold()
        players[2].fold()

        game._advance_to_next_active_player()

        assert game.current_player == 3  # Skipped folded players

    def test_game_repr(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)
        game.pot = 100

        repr_str = repr(game)

        assert "Game" in repr_str
        assert "PREFLOP" in repr_str
        assert "players=3" in repr_str
        assert "pot=100" in repr_str

    def test_dealer_button_movement(self) -> None:
        players = self.create_players(3)
        game = Game(players, 5, 10)

        assert game.dealer_position == 0

        game.start_new_hand()
        assert game.dealer_position == 1

        game.start_new_hand()
        assert game.dealer_position == 2

        game.start_new_hand()
        assert game.dealer_position == 0  # Wraps around

    def test_deck_burn_cards(self) -> None:
        players = self.create_players(2)
        game = Game(players, 5, 10)

        initial_deck_size = len(game.deck)

        # Deal hole cards (4 cards)
        game.deal_hole_cards()
        assert len(game.deck) == initial_deck_size - 4

        # Advance to flop (1 burn + 3 flop = 4 cards)
        game.advance_phase()
        assert len(game.deck) == initial_deck_size - 8

        # Advance to turn (1 burn + 1 turn = 2 cards)
        game.advance_phase()
        assert len(game.deck) == initial_deck_size - 10

        # Advance to river (1 burn + 1 river = 2 cards)
        game.advance_phase()
        assert len(game.deck) == initial_deck_size - 12
