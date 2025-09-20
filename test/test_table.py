import pytest
from src.core.player import Player
from src.core.table import PokerTable, TableStatus
from src.core.cards import Card


class TestPokerTable:
    def create_players(self, count: int = 3) -> list[Player]:
        return [Player(i, f"Player{i}", 1000) for i in range(count)]

    def test_table_creation(self) -> None:
        table = PokerTable("TEST_TABLE", max_players=6, small_blind=5, big_blind=10)

        assert table.table_id == "TEST_TABLE"
        assert table.max_players == 6
        assert table.small_blind == 5
        assert table.big_blind == 10
        assert table.status == TableStatus.PAUSED
        assert table.dealer_seat == 0
        assert table.hand_number == 0
        assert len(table.seats) == 6
        assert all(seat is None for seat in table.seats)

    def test_table_creation_default_values(self) -> None:
        table = PokerTable("DEFAULT")

        assert table.max_players == 10
        assert table.small_blind == 1
        assert table.big_blind == 2

    def test_table_creation_invalid_id(self) -> None:
        with pytest.raises(AssertionError, match="Table ID cannot be empty"):
            PokerTable("")

        with pytest.raises(AssertionError, match="Table ID cannot be empty"):
            PokerTable("   ")

    def test_table_creation_invalid_max_players(self) -> None:
        with pytest.raises(AssertionError, match="Invalid max players"):
            PokerTable("TEST", max_players=1)

        with pytest.raises(AssertionError, match="Invalid max players"):
            PokerTable("TEST", max_players=11)

    def test_table_creation_invalid_blinds(self) -> None:
        with pytest.raises(AssertionError, match="Small blind must be positive"):
            PokerTable("TEST", small_blind=0)

        with pytest.raises(AssertionError, match="Big blind must be > small blind"):
            PokerTable("TEST", small_blind=10, big_blind=10)

        with pytest.raises(AssertionError, match="Big blind must be > small blind"):
            PokerTable("TEST", small_blind=20, big_blind=10)

    def test_add_player_to_any_seat(self) -> None:
        table = PokerTable("TEST", max_players=4)
        player = Player(1, "Alice", 1000)

        seat = table.add_player(player)

        assert seat == 0
        assert table.seats[0] is player
        assert table.get_seat_count() == 1

    def test_add_player_to_specific_seat(self) -> None:
        table = PokerTable("TEST", max_players=4)
        player = Player(1, "Alice", 1000)

        seat = table.add_player(player, seat=2)

        assert seat == 2
        assert table.seats[2] is player
        assert table.seats[0] is None
        assert table.seats[1] is None

    def test_add_player_to_occupied_seat(self) -> None:
        table = PokerTable("TEST", max_players=4)
        player1 = Player(1, "Alice", 1000)
        player2 = Player(2, "Bob", 1000)

        table.add_player(player1, seat=2)
        seat = table.add_player(player2, seat=2)

        assert seat is None
        assert table.seats[2] is player1

    def test_add_player_table_full(self) -> None:
        table = PokerTable("TEST", max_players=2)
        players = self.create_players(3)

        assert table.add_player(players[0]) == 0
        assert table.add_player(players[1]) == 1
        assert table.add_player(players[2]) is None

    def test_add_duplicate_player(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        seat1 = table.add_player(player)
        seat2 = table.add_player(player)

        assert seat1 == 0
        assert seat2 is None

    def test_add_player_no_chips(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 0)

        with pytest.raises(AssertionError, match="Player must have chips"):
            table.add_player(player)

    def test_add_player_invalid_type(self) -> None:
        table = PokerTable("TEST")

        with pytest.raises(AssertionError, match="Must provide Player instance"):
            table.add_player("not_a_player")  # type: ignore

    def test_remove_player(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        table.add_player(player, seat=3)
        removed_player = table.remove_player(3)

        assert removed_player is player
        assert table.seats[3] is None
        assert table.get_seat_count() == 0

    def test_remove_player_empty_seat(self) -> None:
        table = PokerTable("TEST")

        removed_player = table.remove_player(3)

        assert removed_player is None

    def test_remove_player_invalid_seat(self) -> None:
        table = PokerTable("TEST", max_players=5)

        with pytest.raises(AssertionError, match="Invalid seat"):
            table.remove_player(-1)

        with pytest.raises(AssertionError, match="Invalid seat"):
            table.remove_player(5)

    def test_remove_player_by_id(self) -> None:
        table = PokerTable("TEST")
        player = Player(42, "Alice", 1000)

        table.add_player(player, seat=5)
        removed_player = table.remove_player_by_id(42)

        assert removed_player is player
        assert table.seats[5] is None

    def test_remove_player_by_id_not_found(self) -> None:
        table = PokerTable("TEST")

        removed_player = table.remove_player_by_id(999)

        assert removed_player is None

    def test_get_player(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        table.add_player(player, seat=7)

        assert table.get_player(7) is player
        assert table.get_player(6) is None

    def test_get_player_invalid_seat(self) -> None:
        table = PokerTable("TEST", max_players=5)

        with pytest.raises(AssertionError, match="Invalid seat"):
            table.get_player(-1)

        with pytest.raises(AssertionError, match="Invalid seat"):
            table.get_player(5)

    def test_find_player_seat(self) -> None:
        table = PokerTable("TEST")
        player = Player(123, "Alice", 1000)

        table.add_player(player, seat=4)

        assert table.find_player_seat(123) == 4
        assert table.find_player_seat(999) is None

    def test_get_active_players(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(4)

        table.add_player(players[0], seat=1)
        table.add_player(players[1], seat=3)
        table.add_player(players[2], seat=7)
        table.add_player(players[3], seat=9)

        players[1].sit_out()

        active = table.get_active_players()
        active_seats = [seat for seat, _ in active]

        assert active_seats == [1, 7, 9]

    def test_get_active_players_no_chips(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        table.add_player(players[0], seat=0)
        table.add_player(players[1], seat=1)

        players[0].chips = 0

        active = table.get_active_players()
        active_seats = [seat for seat, _ in active]

        assert active_seats == [1]

    def test_get_players_in_hand(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(3)

        for i, player in enumerate(players):
            table.add_player(player, seat=i)

        players[1].fold()

        in_hand = table.get_players_in_hand()
        in_hand_seats = [seat for seat, _ in in_hand]

        assert in_hand_seats == [0, 2]

    def test_is_seat_available(self) -> None:
        table = PokerTable("TEST", max_players=5)
        player = Player(1, "Alice", 1000)

        assert table.is_seat_available(2)
        assert table.is_seat_available(4)
        assert not table.is_seat_available(-1)
        assert not table.is_seat_available(5)

        table.add_player(player, seat=2)
        assert not table.is_seat_available(2)

    def test_get_available_seats(self) -> None:
        table = PokerTable("TEST", max_players=4)
        player = Player(1, "Alice", 1000)

        assert table.get_available_seats() == [0, 1, 2, 3]

        table.add_player(player, seat=1)
        assert table.get_available_seats() == [0, 2, 3]

    def test_get_occupied_seats(self) -> None:
        table = PokerTable("TEST", max_players=4)
        players = self.create_players(2)

        assert table.get_occupied_seats() == []

        table.add_player(players[0], seat=0)
        table.add_player(players[1], seat=3)
        assert table.get_occupied_seats() == [0, 3]

    def test_get_seat_count(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(3)

        assert table.get_seat_count() == 0

        table.add_player(players[0])
        assert table.get_seat_count() == 1

        table.add_player(players[1])
        table.add_player(players[2])
        assert table.get_seat_count() == 3

    def test_can_start_game(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(3)

        assert not table.can_start_game()

        table.add_player(players[0])
        assert not table.can_start_game()

        table.add_player(players[1])
        assert table.can_start_game()

        table.status = TableStatus.ACTIVE
        assert not table.can_start_game()

    def test_can_start_game_custom_minimum(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(4)

        table.add_player(players[0])
        table.add_player(players[1])

        assert table.can_start_game(min_players=2)
        assert not table.can_start_game(min_players=3)

        table.add_player(players[2])
        assert table.can_start_game(min_players=3)

    def test_start_game(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        table.add_player(players[0])
        table.add_player(players[1])

        success = table.start_game()

        assert success
        assert table.status == TableStatus.ACTIVE
        assert table.hand_number == 1

    def test_start_game_insufficient_players(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        table.add_player(player)
        success = table.start_game()

        assert not success
        assert table.status == TableStatus.PAUSED

    def test_pause_resume_game(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        for player in players:
            table.add_player(player)

        table.start_game()
        table.pause_game()

        assert table.status == TableStatus.PAUSED

        success = table.resume_game()
        assert success
        assert table.status == TableStatus.ACTIVE  # type: ignore

    def test_pause_game_wrong_status(self) -> None:
        table = PokerTable("TEST")

        table.pause_game()
        assert table.status == TableStatus.PAUSED

    def test_resume_game_insufficient_players(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        for player in players:
            table.add_player(player)

        table.start_game()
        table.pause_game()

        table.remove_player(0)

        success = table.resume_game()
        assert not success
        assert table.status == TableStatus.PAUSED

    def test_end_game(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        for player in players:
            table.add_player(player)

        table.start_game()
        table.end_game()

        assert table.status == TableStatus.PAUSED

    def test_close_table(self) -> None:
        table = PokerTable("TEST")

        table.close_table()

        assert table.status == TableStatus.CLOSED

    def test_get_blind_seats_multiway(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(4)

        for i, player in enumerate(players):
            table.add_player(player, seat=i)

        table.dealer_seat = 1
        small_seat, big_seat = table.get_blind_seats()

        assert small_seat == 2
        assert big_seat == 3

    def test_get_blind_seats_heads_up(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        table.add_player(players[0], seat=2)
        table.add_player(players[1], seat=5)

        table.dealer_seat = 2
        small_seat, big_seat = table.get_blind_seats()

        assert small_seat == 2
        assert big_seat == 5

    def test_get_blind_seats_insufficient_players(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        table.add_player(player)

        with pytest.raises(ValueError, match="Need at least 2 players"):
            table.get_blind_seats()

    def test_get_action_seat(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(3)

        for i, player in enumerate(players):
            table.add_player(player, seat=i)

        table.dealer_seat = 0
        action_seat = table.get_action_seat()

        assert action_seat == 0

    def test_prepare_new_hand(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        for player in players:
            table.add_player(player)
            player.fold()

        table.prepare_new_hand()

        for player in players:
            assert not player.is_folded

    def test_update_stats(self) -> None:
        table = PokerTable("TEST")

        table.update_stats(100)
        table.update_stats(250)
        table.update_stats(150)

        assert table.hands_played == 3
        assert table.total_pot_awarded == 500
        assert table.biggest_pot == 250

    def test_get_table_info(self) -> None:
        table = PokerTable("TEST", max_players=6, small_blind=5, big_blind=10)
        players = self.create_players(3)

        for player in players:
            table.add_player(player)

        table.hand_number = 42
        table.hands_played = 100
        table.biggest_pot = 500

        info = table.get_table_info()

        assert info["table_id"] == "TEST"
        assert info["status"] == "PAUSED"
        assert info["players"] == 3
        assert info["max_players"] == 6
        assert info["small_blind"] == 5
        assert info["big_blind"] == 10
        assert info["hand_number"] == 42
        assert info["hands_played"] == 100
        assert info["biggest_pot"] == 500
        assert len(info["available_seats"]) == 3
        assert len(info["occupied_seats"]) == 3

    def test_get_seat_info(self) -> None:
        table = PokerTable("TEST")
        player = Player(99, "Alice", 1500)
        player.current_bet = 50
        player.deal_hole_cards([Card("As"), Card("Kh")])

        table.add_player(player, seat=3)
        table.dealer_seat = 3

        info = table.get_seat_info(3)

        assert info is not None
        assert info["seat"] == 3
        assert info["player_id"] == 99
        assert info["name"] == "Alice"
        assert info["chips"] == 1500
        assert info["is_dealer"] == True
        assert info["current_bet"] == 50
        assert info["hole_cards_count"] == 2

    def test_get_seat_info_empty_seat(self) -> None:
        table = PokerTable("TEST")

        info = table.get_seat_info(5)

        assert info is None

    def test_get_all_seat_info(self) -> None:
        table = PokerTable("TEST", max_players=3)
        player = Player(1, "Alice", 1000)

        table.add_player(player, seat=1)

        all_info = table.get_all_seat_info()

        assert len(all_info) == 3
        assert all_info[0] is None
        assert all_info[1] is not None
        assert all_info[2] is None

    def test_move_player(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)

        table.add_player(player, seat=2)
        success = table.move_player(from_seat=2, to_seat=7)

        assert success
        assert table.seats[2] is None
        assert table.seats[7] is player

    def test_move_player_to_occupied_seat(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(2)

        table.add_player(players[0], seat=1)
        table.add_player(players[1], seat=3)

        success = table.move_player(from_seat=1, to_seat=3)

        assert not success
        assert table.seats[1] is players[0]
        assert table.seats[3] is players[1]

    def test_move_player_from_empty_seat(self) -> None:
        table = PokerTable("TEST")

        success = table.move_player(from_seat=2, to_seat=5)

        assert not success

    def test_dealer_button_advancement(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(4)

        table.add_player(players[0], seat=1)
        table.add_player(players[1], seat=3)
        table.add_player(players[2], seat=5)
        table.add_player(players[3], seat=8)

        table.dealer_seat = 3
        table._advance_dealer_button()

        assert table.dealer_seat == 5

    def test_dealer_button_wraps_around(self) -> None:
        table = PokerTable("TEST")
        players = self.create_players(3)

        table.add_player(players[0], seat=2)
        table.add_player(players[1], seat=5)
        table.add_player(players[2], seat=7)

        table.dealer_seat = 7
        table._advance_dealer_button()

        assert table.dealer_seat == 2

    def test_str_representation(self) -> None:
        table = PokerTable("MAIN_GAME", max_players=8, small_blind=2, big_blind=4)
        players = self.create_players(3)

        for player in players:
            table.add_player(player)

        table_str = str(table)

        assert "MAIN_GAME" in table_str
        assert "3/8" in table_str
        assert "$2/$4" in table_str

    def test_repr_representation(self) -> None:
        table = PokerTable("TEST")
        player = Player(1, "Alice", 1000)
        table.add_player(player)

        repr_str = repr(table)

        assert "PokerTable" in repr_str
        assert "TEST" in repr_str
        assert "players=1" in repr_str
        assert "PAUSED" in repr_str
