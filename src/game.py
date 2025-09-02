from src.player import Player
from src.cards import Deck
from typing import List

class Game:
    states: List[str] = ["RESET", "PREFLOP", "POSTFLOP", "TURN", "RIVER"]

    def __init__(self, players: List[Player]) -> None:
        self.players: List[Player] = players
        self.deck: Deck = Deck()
        self.state: str = Game.states[0]
        self.board: List[Card] = []

    def deal_hole_cards(self) -> None:
        assert self.state == "RESET"
        for player in self.players:
            player.deal_cards(self.deck.draw_cards(2))
        self.state = "PREFLOP"

    def deal_flop(self) -> None:
        assert self.state == "PREFLOP"
        flop: List[Card] = self.deck.draw_cards(3)
        self.board += flop
        assert len(self.board) == 3
        self.state = "POSTFLOP"

    def deal_turn(self) -> None:
        assert self.state == "POSTFLOP"
        turn: List[Card] = self.deck.draw_cards(1)
        self.board += turn
        assert len(self.board) == 4
        self.state = "TURN"

    def deal_river(self) -> None:
        assert self.state == "TURN"
        river: List[Card] = self.deck.draw_cards(1)
        self.board += river
        assert len(self.board) == 5
        self.state = "RIVER"

    def reset(self) -> None:
        for player in self.players:
            player.reset()
        self.deck.shuffle()
        self.state = "RESET"

if __name__ == "__main__":
    players: List[Player] = [Player(name) for name in ["A", "B"]]
    game: Game = Game(players)
