from typing import Optional
from enum import Enum, auto
from src.core.player import Player


class TableStatus(Enum):
    PAUSED = auto()
    ACTIVE = auto()
    CLOSED = auto()


class PokerTable:
    def __init__(
        self,
        table_id: str,
        max_players: int = 10,
        small_blind: int = 1,
        big_blind: int = 2,
    ) -> None:
        assert len(table_id.strip()) > 0, "Table ID cannot be empty"
        assert 2 <= max_players <= 10, f"Invalid max players: {max_players}"
        assert small_blind > 0, "Small blind must be positive"
        assert big_blind > small_blind, "Big blind must be > small blind"

        self.table_id = table_id.strip()
        self.max_players = max_players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.status = TableStatus.PAUSED

        self.seats: list[Optional[Player]] = [None] * max_players
        self.dealer_seat = 0
        self.hand_number = 0

        self.hands_played = 0
        self.total_pot_awarded = 0
        self.biggest_pot = 0

    def add_player(self, player: Player, seat: Optional[int] = None) -> Optional[int]:
        assert isinstance(player, Player), "Must provide Player instance"
        assert player.chips > 0, "Player must have chips to join"

        if self.find_player_seat(player.player_id) is not None:
            return None

        if seat is not None:
            if self.is_seat_available(seat):
                self.seats[seat] = player
                return seat
            return None
        else:
            for i in range(self.max_players):
                if self.is_seat_available(i):
                    self.seats[i] = player
                    return i
            return None

    def remove_player(self, seat: int) -> Optional[Player]:
        assert 0 <= seat < self.max_players, f"Invalid seat: {seat}"

        player = self.seats[seat]
        if player is not None:
            self.seats[seat] = None

        return player

    def remove_player_by_id(self, player_id: int) -> Optional[Player]:
        seat = self.find_player_seat(player_id)
        if seat is not None:
            return self.remove_player(seat)
        return None

    def get_player(self, seat: int) -> Optional[Player]:
        assert 0 <= seat < self.max_players, f"Invalid seat: {seat}"
        return self.seats[seat]

    def find_player_seat(self, player_id: int) -> Optional[int]:
        for i, player in enumerate(self.seats):
            if player is not None and player.player_id == player_id:
                return i
        return None

    def get_active_players(self) -> list[tuple[int, Player]]:
        return [
            (i, p)
            for i, p in enumerate(self.seats)
            if p is not None and not p.is_sitting_out and p.chips > 0
        ]

    def get_players_in_hand(self) -> list[tuple[int, Player]]:
        return [(i, p) for i, p in self.get_active_players() if p.is_active()]

    def is_seat_available(self, seat: int) -> bool:
        return 0 <= seat < self.max_players and self.seats[seat] is None

    def get_available_seats(self) -> list[int]:
        return [i for i in range(self.max_players) if self.is_seat_available(i)]

    def get_occupied_seats(self) -> list[int]:
        return [i for i in range(self.max_players) if self.seats[i] is not None]

    def get_seat_count(self) -> int:
        return len(self.get_occupied_seats())

    def can_start_game(self, min_players: int = 2) -> bool:
        if self.status != TableStatus.PAUSED:
            return False

        active_count = len(self.get_active_players())
        return active_count >= min_players

    def start_game(self) -> bool:
        if not self.can_start_game():
            return False

        self.status = TableStatus.ACTIVE
        self.hand_number += 1
        self._advance_dealer_button()
        return True

    def pause_game(self) -> None:
        if self.status == TableStatus.ACTIVE:
            self.status = TableStatus.PAUSED

    def resume_game(self) -> bool:
        if self.status == TableStatus.PAUSED and self.can_start_game():
            self.status = TableStatus.ACTIVE
            return True
        return False

    def end_game(self) -> None:
        self.status = TableStatus.PAUSED

    def close_table(self) -> None:
        self.status = TableStatus.CLOSED

    def get_blind_seats(self) -> tuple[int, int]:
        active_players = self.get_active_players()
        if len(active_players) < 2:
            raise ValueError("Need at least 2 players for blinds")

        if len(active_players) == 2:
            small_blind_seat = self.dealer_seat
            big_blind_seat: Optional[int] = self._get_next_active_seat(self.dealer_seat)
        else:
            small_blind_seat = self._get_next_active_seat(self.dealer_seat)  # type: ignore[assignment]
            big_blind_seat: Optional[int] = self._get_next_active_seat(small_blind_seat)  # type: ignore

        if small_blind_seat is None or big_blind_seat is None:
            raise ValueError("Could not determine blind positions")

        return small_blind_seat, big_blind_seat

    def get_action_seat(self) -> Optional[int]:
        try:
            _, big_blind_seat = self.get_blind_seats()
            return self._get_next_active_seat(big_blind_seat)
        except ValueError:
            return None

    def prepare_new_hand(self) -> None:
        for player in self.seats:
            if player is not None:
                player.reset()

    def update_stats(self, pot_size: int) -> None:
        self.hands_played += 1
        self.total_pot_awarded += pot_size
        if pot_size > self.biggest_pot:
            self.biggest_pot = pot_size

    def get_table_info(self) -> dict:  # type: ignore[type-arg]
        active_players = self.get_active_players()

        return {
            "table_id": self.table_id,
            "status": self.status.name,
            "players": len(active_players),
            "max_players": self.max_players,
            "dealer_seat": self.dealer_seat,
            "small_blind": self.small_blind,
            "big_blind": self.big_blind,
            "hand_number": self.hand_number,
            "available_seats": self.get_available_seats(),
            "occupied_seats": self.get_occupied_seats(),
            "hands_played": self.hands_played,
            "biggest_pot": self.biggest_pot,
        }

    def get_seat_info(self, seat: int) -> Optional[dict]:  # type: ignore[type-arg]
        player = self.get_player(seat)
        if player is None:
            return None

        return {
            "seat": seat,
            "player_id": player.player_id,
            "name": player.name,
            "chips": player.chips,
            "is_dealer": seat == self.dealer_seat,
            "is_folded": player.is_folded,
            "is_all_in": player.is_all_in,
            "is_sitting_out": player.is_sitting_out,
            "current_bet": player.current_bet,
            "hole_cards_count": len(player.hole_cards),
        }

    def get_all_seat_info(self) -> list[Optional[dict]]:  # type: ignore[type-arg]
        return [self.get_seat_info(i) for i in range(self.max_players)]

    def move_player(self, from_seat: int, to_seat: int) -> bool:
        if not self.is_seat_available(to_seat):
            return False

        player = self.get_player(from_seat)
        if player is None:
            return False

        self.seats[to_seat] = player
        self.seats[from_seat] = None
        return True

    def _advance_dealer_button(self) -> None:
        active_players = self.get_active_players()
        if not active_players:
            return

        next_dealer = self._get_next_active_seat(self.dealer_seat)
        if next_dealer is not None:
            self.dealer_seat = next_dealer

    def _get_next_active_seat(self, current_seat: int) -> Optional[int]:
        active_players = self.get_active_players()
        if not active_players:
            return None

        active_seats = [seat for seat, _ in active_players]

        try:
            current_idx = active_seats.index(current_seat)
            next_idx = (current_idx + 1) % len(active_seats)
            return active_seats[next_idx]
        except ValueError:
            return active_seats[0] if active_seats else None

    def __str__(self) -> str:
        occupied = self.get_seat_count()
        return f"Table {self.table_id}: {occupied}/{self.max_players} players, ${self.small_blind}/${self.big_blind}"

    def __repr__(self) -> str:
        return f"PokerTable(id='{self.table_id}', players={self.get_seat_count()}, status={self.status.name})"
