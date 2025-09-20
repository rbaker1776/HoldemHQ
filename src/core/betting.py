from typing import Optional, Any
from dataclasses import dataclass
from src.core.player import Player


@dataclass
class SidePot:
    amount: int
    player_indices: list[int]

    def __repr__(self) -> str:
        return f"SidePot(amount={self.amount}, players={len(self.player_indices)})"


@dataclass
class BettingAction:
    player_id: int
    action_type: str  # "fold", "check", "call", "bet", "raise", "all_in"
    amount: int
    total_investment: int

    def __repr__(self) -> str:
        return f"{self.action_type.upper()}({self.amount}) by Player {self.player_id}"


class BettingManager:
    def __init__(self) -> None:
        self.main_pot: int = 0
        self.side_pots: list[SidePot] = []
        self.current_bet: int = 0
        self.betting_history: list[BettingAction] = []
        self.player_investments: dict[
            int, int
        ] = {}  # player_id -> total invested this hand

    def start_new_hand(self) -> None:
        self.main_pot = 0
        self.side_pots.clear()
        self.current_bet = 0
        self.betting_history.clear()
        self.player_investments.clear()

    def start_new_betting_round(self) -> None:
        self.current_bet = 0

    def post_blind(
        self, player: Player, amount: int, is_big_blind: bool = False
    ) -> int:
        actual_amount = player.bet(amount)
        self.main_pot += actual_amount
        self.current_bet = max(self.current_bet, actual_amount)
        self.player_investments[player.player_id] = actual_amount

        action_type = "big_blind" if is_big_blind else "small_blind"
        self._record_action(player.player_id, action_type, actual_amount, actual_amount)

        return actual_amount

    def process_fold(self, player: Player) -> None:
        player.fold()
        self._record_action(
            player.player_id, "fold", 0, self._get_total_investment(player.player_id)
        )

    def process_check(self, player: Player) -> bool:
        if self.current_bet > 0:
            return False

        player.check()
        self._record_action(
            player.player_id, "check", 0, self._get_total_investment(player.player_id)
        )
        return True

    def process_call(self, player: Player) -> int:
        if self.current_bet == 0:
            return 0

        call_amount = self.current_bet - player.current_bet
        actual_call = player.call(self.current_bet)

        self.main_pot += actual_call
        self._add_investment(player.player_id, actual_call)

        self._record_action(
            player.player_id,
            "call",
            actual_call,
            self._get_total_investment(player.player_id),
        )

        return actual_call

    def process_bet(self, player: Player, amount: int) -> int:
        if self.current_bet > 0:
            return 0

        actual_bet = player.bet(amount)
        self.main_pot += actual_bet
        self.current_bet = actual_bet
        self._add_investment(player.player_id, actual_bet)

        self._record_action(
            player.player_id,
            "bet",
            actual_bet,
            self._get_total_investment(player.player_id),
        )

        return actual_bet

    def process_raise(self, player: Player, raise_to_amount: int) -> int:
        if self.current_bet == 0:
            return 0

        if raise_to_amount <= self.current_bet:
            return 0

        call_amount = self.current_bet - player.current_bet
        additional_raise = raise_to_amount - self.current_bet

        actual_call = player.call(self.current_bet)
        actual_raise = player.bet(additional_raise)

        total_action = actual_call + actual_raise
        self.main_pot += total_action
        self.current_bet = player.current_bet
        self._add_investment(player.player_id, total_action)

        self._record_action(
            player.player_id,
            "raise",
            total_action,
            self._get_total_investment(player.player_id),
        )

        return total_action

    def process_all_in(self, player: Player) -> int:
        if player.chips == 0:
            return 0

        all_in_amount = player.go_all_in()
        self.main_pot += all_in_amount

        if player.current_bet > self.current_bet:
            self.current_bet = player.current_bet

        self._add_investment(player.player_id, all_in_amount)
        self._record_action(
            player.player_id,
            "all_in",
            all_in_amount,
            self._get_total_investment(player.player_id),
        )

        return all_in_amount

    def calculate_side_pots(self, players: list[Player]) -> list[SidePot]:
        """Calculate side pots for all-in scenarios."""
        if not any(p.is_all_in for p in players):
            eligible = [p.player_id for p in players if p.is_active()]
            if eligible:
                return [SidePot(self.get_total_pot(), eligible)]
            return []

        investment_levels = set()
        for player in players:
            if player.is_active() or player.is_all_in:
                total_investment = self._get_total_investment(player.player_id)
                investment_levels.add(total_investment)

        sorted_levels = sorted(investment_levels)
        side_pots = []

        previous_level = 0
        for level in sorted_levels:
            player_indices = []
            for player in players:
                if player.is_active() or player.is_all_in:
                    player_investment = self._get_total_investment(player.player_id)
                    if player_investment >= level:
                        player_indices.append(player.player_id)

            if player_indices:
                pot_amount = (level - previous_level) * len(player_indices)
                if pot_amount > 0:
                    side_pots.append(SidePot(pot_amount, player_indices.copy()))

            previous_level = level

        return side_pots

    def distribute_winnings(
        self, winners_by_pot: list[list[int]], side_pots: list[SidePot]
    ) -> dict[int, int]:
        winnings: dict[int, int] = {}

        for i, (winners, pot) in enumerate(zip(winners_by_pot, side_pots)):
            if not winners:
                continue

            winnings_per_winner = pot.amount // len(winners)
            remainder = pot.amount % len(winners)

            for j, winner_id in enumerate(winners):
                amount = winnings_per_winner
                if j < remainder:
                    amount += 1

                winnings[winner_id] = winnings.get(winner_id, 0) + amount

        return winnings

    def get_total_pot(self) -> int:
        return self.main_pot + sum(pot.amount for pot in self.side_pots)

    def get_pot_info(self) -> dict[str, Any]:
        return {
            "main_pot": self.main_pot,
            "side_pots": len(self.side_pots),
            "total_pot": self.get_total_pot(),
            "current_bet": self.current_bet,
            "side_pot_details": [
                {"amount": pot.amount, "player_indices": pot.player_indices}
                for pot in self.side_pots
            ],
        }

    def get_player_investment(self, player_id: int) -> int:
        return self._get_total_investment(player_id)

    def get_betting_history(self) -> list[BettingAction]:
        return self.betting_history.copy()

    def get_action_summary(self) -> dict[str, Any]:
        actions_by_type: dict[str, Any] = {}
        total_invested = 0

        for action in self.betting_history:
            action_type = action.action_type
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
            total_invested += action.amount

        return {
            "total_actions": len(self.betting_history),
            "actions_by_type": actions_by_type,
            "total_invested": total_invested,
            "average_action": total_invested / len(self.betting_history)
            if self.betting_history
            else 0,
        }

    def can_player_check(self, player: Player) -> bool:
        return self.current_bet == 0 and player.can_act()

    def can_player_call(self, player: Player) -> bool:
        return (
            self.current_bet > 0
            and player.can_act()
            and player.current_bet < self.current_bet
        )

    def can_player_bet(self, player: Player) -> bool:
        return self.current_bet == 0 and player.can_act() and player.has_chips()

    def can_player_raise(self, player: Player) -> bool:
        return (
            self.current_bet > 0
            and player.can_act()
            and player.has_chips()
            and player.current_bet < self.current_bet
        )

    def get_minimum_raise(self) -> int:
        if self.current_bet == 0:
            return 0

        return self.current_bet * 2

    def get_call_amount(self, player: Player) -> int:
        return max(0, self.current_bet - player.current_bet)

    def is_betting_capped(self, players: list[Player]) -> bool:
        active_players = [p for p in players if p.is_active()]
        players_with_chips = [
            p for p in active_players if p.has_chips() and not p.is_all_in
        ]

        return len(players_with_chips) <= 1

    def _get_total_investment(self, player_id: int) -> int:
        return self.player_investments.get(player_id, 0)

    def _add_investment(self, player_id: int, amount: int) -> None:
        self.player_investments[player_id] = (
            self._get_total_investment(player_id) + amount
        )

    def _record_action(
        self, player_id: int, action_type: str, amount: int, total_investment: int
    ) -> None:
        action = BettingAction(player_id, action_type, amount, total_investment)
        self.betting_history.append(action)

    def __repr__(self) -> str:
        return f"BettingManager(pot={self.get_total_pot()}, current_bet={self.current_bet}, actions={len(self.betting_history)})"
