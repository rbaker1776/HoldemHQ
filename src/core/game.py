from enum import Enum, auto
from typing import Optional
from src.core.cards import Card, Deck
from src.core.player import Player
from src.core.evaluator import evaluate_hand


class GamePhase(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()
    FINISHED = auto()


class GameAction(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    RAISE = auto()
    ALL_IN = auto()


class Game:
    def __init__(self, players: list[Player], small_blind: int, big_blind: int) -> None:
        assert 2 <= len(players) <= 10, f"Invalid player count: {len(players)}"
        assert 0 <= small_blind <= big_blind, "Invalid blinds"

        self.players: list[Player] = players
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

        self.deck: Deck = Deck()
        self.board: list[Card] = []
        self.phase: GamePhase = GamePhase.PREFLOP
        self.pot: int = 0
        self.current_bet: int = 0
        self.dealer_position: int = 0

        self.current_player: int = 0
        self.last_raiser: Optional[int] = None
        self.players_acted: set[int] = set()

    def start_new_hand(self) -> None:
        self.deck.reset()
        self.board.clear()
        self.phase = GamePhase.PREFLOP

        for player in self.players:
            player.reset()

        self.pot = 0
        self.current_bet = 0
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

        self._post_blinds()

        self.current_player = (self.dealer_position + 3) % len(self.players)
        self.last_raiser = None
        self.players_acted.clear()

    def deal_hole_cards(self) -> None:
        assert self.phase == GamePhase.PREFLOP, "Can only deal hole cards preflop"

        for player in self.players:
            if not player.is_sitting_out:
                cards = self.deck.deal(2)
                player.deal_hole_cards(cards)

    def advance_phase(self) -> None:
        if self.phase == GamePhase.PREFLOP:
            self.deck.deal(1)
            self.board.extend(self.deck.deal(3))
            self.phase = GamePhase.FLOP

        elif self.phase == GamePhase.FLOP:
            self.deck.deal(1)
            self.board.extend(self.deck.deal(1))
            self.phase = GamePhase.TURN

        elif self.phase == GamePhase.TURN:
            self.deck.deal(1)
            self.board.extend(self.deck.deal(1))
            self.phase = GamePhase.RIVER

        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN

        elif self.phase == GamePhase.SHOWDOWN:
            self.phase = GamePhase.FINISHED

        if self.phase in [GamePhase.FLOP, GamePhase.TURN, GamePhase.RIVER]:
            self.current_bet = 0
            self.current_player = (self.dealer_position + 1) % len(self.players)
            self._advance_to_next_active_player()
            self.last_raiser = None
            self.players_acted.clear()

    def get_active_players(self) -> list[int]:
        return [i for i, p in enumerate(self.players) if p.is_active()]

    def is_betting_round_complete(self) -> bool:
        active = self.get_active_players()

        # If all but one player folded, round is over
        if len(active) < 2:
            return True

        # All active players must have acted
        if not all(i in self.players_acted for i in active):
            return False

        # If there was a raiser, action must return to them
        if self.last_raiser is not None:
            return self.current_player == self.last_raiser

        return True

    def can_check(self, player_idx: int) -> bool:
        return (
            player_idx in self.get_active_players()
            and self.current_bet == 0
            and self.players[player_idx].can_act()
        )

    def can_call(self, player_idx: int) -> bool:
        return (
            player_idx in self.get_active_players()
            and self.current_bet > 0
            and self.players[player_idx].can_act()
        )

    def can_bet(self, player_idx: int) -> bool:
        return (
            player_idx in self.get_active_players()
            and self.current_bet == 0
            and self.players[player_idx].can_act()
            and self.players[player_idx].has_chips()
        )

    def can_raise(self, player_idx: int) -> bool:
        return (
            player_idx in self.get_active_players()
            and self.current_bet > 0
            and self.players[player_idx].can_act()
            and self.players[player_idx].has_chips()
        )

    def process_action(
        self, player_idx: int, action: GameAction, amount: int = 0, is_bb: bool = False
    ) -> bool:
        assert player_idx == self.current_player, f"Not player {player_idx}'s turn"
        assert player_idx in self.get_active_players(), (
            f"Player {player_idx} not active"
        )

        player: Player = self.players[player_idx]

        if action == GameAction.FOLD:
            player.fold()

        elif action == GameAction.CHECK:
            assert self.can_check(player_idx) or is_bb, f"Cannot check: {player}"
            player.check()

        elif action == GameAction.CALL:
            assert self.can_call(player_idx), "Cannot call"
            actual_call = player.call(self.current_bet)
            self.pot += actual_call

        elif action == GameAction.BET:
            assert self.can_bet(player_idx), "Cannot bet"
            assert amount > 0, "Bet amount must be positive"
            actual_bet = player.bet(amount)
            self.current_bet = player.current_bet
            self.pot += actual_bet
            self.last_raiser = player_idx

        elif action == GameAction.RAISE:
            assert self.can_raise(player_idx), "Cannot raise"
            assert amount > self.current_bet, "Raise must be larger than current bet"

            call_amount = player.call(self.current_bet)
            raise_amount = player.bet(amount - self.current_bet)
            total_action = call_amount + raise_amount

            self.current_bet = amount
            self.pot += total_action
            self.last_raiser = player_idx

        elif action == GameAction.ALL_IN:
            all_in_amount = player.go_all_in()
            self.pot += all_in_amount

            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
                self.last_raiser = player_idx

        self.players_acted.add(player_idx)
        self._advance_to_next_active_player()

        return True

    def evaluate_hands(self) -> list[tuple[int, int]]:
        assert len(self.board) == 5, "Need all 5 community cards"

        results = []
        for i, player in enumerate(self.players):
            if player.is_active() and len(player.hole_cards) == 2:
                full_hand = player.hole_cards + self.board
                score = evaluate_hand(full_hand)
                results.append((i, score))

        return results

    def determine_winner(self) -> list[int]:
        hand_scores = self.evaluate_hands()

        if not hand_scores:
            return []

        best_score = min(score for _, score in hand_scores)
        winners = [
            player_idx for player_idx, score in hand_scores if score == best_score
        ]

        return winners

    def distribute_pot(self, winners: list[int]) -> None:
        if not winners:
            return

        winnings_per_player = self.pot // len(winners)
        remainder = self.pot % len(winners)

        for i, winner_idx in enumerate(winners):
            amount = winnings_per_player
            if i < remainder:
                amount += 1

            self.players[winner_idx].add_chips(amount)

        self.pot = 0

    def _post_blinds(self) -> None:
        num_players = len(self.players)

        if num_players == 2:
            small_blind_idx = self.dealer_position
            big_blind_idx = (self.dealer_position + 1) % num_players
        else:
            small_blind_idx = (self.dealer_position + 1) % num_players
            big_blind_idx = (self.dealer_position + 2) % num_players

        small_actual = self.players[small_blind_idx].bet(self.small_blind)
        big_actual = self.players[big_blind_idx].bet(self.big_blind)

        self.pot += small_actual + big_actual
        self.current_bet = big_actual

    def _advance_to_next_active_player(self) -> None:
        active_players = self.get_active_players()
        if len(active_players) <= 1:
            return

        original_player = self.current_player
        while True:
            self.current_player = (self.current_player + 1) % len(self.players)
            if self.current_player in active_players:
                break
            if self.current_player == original_player:
                break

    def __repr__(self) -> str:
        active = len(self.get_active_players())
        return f"Game(phase={self.phase.name}, players={active}, pot={self.pot})"
