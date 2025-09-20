import pytest
from src.core.cards import Card, Deck, Hand


class TestCard:
    def test_card_creation_valid_old_format(self) -> None:
        card = Card("A", "s")
        assert card.rank == "A"
        assert card.suit == "s"

    def test_card_creation_valid_new_format(self) -> None:
        card = Card("As")
        assert card.rank == "A"
        assert card.suit == "s"

    def test_card_creation_invalid_rank(self) -> None:
        with pytest.raises(AssertionError, match="Invalid rank: X"):
            Card("X", "s")
        with pytest.raises(AssertionError, match="Invalid rank: X"):
            Card("Xs")

    def test_card_creation_invalid_suit(self) -> None:
        with pytest.raises(AssertionError, match="Invalid suit: x"):
            Card("A", "x")
        with pytest.raises(AssertionError, match="Invalid suit: x"):
            Card("Ax")

    def test_card_str_representation(self) -> None:
        card = Card("Kh")
        assert str(card) == "Kh"

    def test_card_repr_representation(self) -> None:
        card = Card("Qd")
        assert repr(card) == "Card('Qd')"

    def test_card_abs_rank_value(self) -> None:
        assert abs(Card("2s")) == 0
        assert abs(Card("3s")) == 1
        assert abs(Card("Ts")) == 8
        assert abs(Card("Js")) == 9
        assert abs(Card("Qs")) == 10
        assert abs(Card("Ks")) == 11
        assert abs(Card("As")) == 12

    def test_card_equality(self) -> None:
        assert Card("As") == Card("Ah")
        assert Card("Kd") == Card("Kc")
        assert Card("As") != Card("Ks")

    def test_card_equality_with_non_card(self) -> None:
        card = Card("As")
        assert card != "As"
        assert card != 12
        assert card != None

    def test_card_less_than(self) -> None:
        assert Card("2s") < Card("3h")
        assert Card("Td") < Card("Jc")
        assert Card("Qs") < Card("Kh")
        assert Card("Kd") < Card("Ac")
        assert not Card("As") < Card("Kh")

    def test_card_less_than_with_non_card(self) -> None:
        card = Card("As")
        with pytest.raises(TypeError):
            card < "As"  # type: ignore[operator]

    def test_card_hash(self) -> None:
        assert hash(Card("As")) == hash(Card("Ah"))
        assert hash(Card("Kd")) == hash(Card("Kc"))
        for rank1 in Card.RANKS:
            for rank2 in Card.RANKS:
                assert (hash(Card(f"{rank1}s")) == hash(Card(f"{rank2}h"))) == (
                    rank1 == rank2
                )

    def test_card_sorting(self) -> None:
        cards = [Card("Ks"), Card("2h"), Card("Ad"), Card("Tc")]
        sorted_cards = sorted(cards)
        expected_ranks = ["2", "T", "K", "A"]
        assert [card.rank for card in sorted_cards] == expected_ranks

    def test_both_formats_equivalent(self) -> None:
        # Test that both formats create equivalent cards
        old_format = Card("A", "s")
        new_format = Card("As")
        assert old_format.rank == new_format.rank
        assert old_format.suit == new_format.suit
        assert str(old_format) == str(new_format)
        assert old_format == new_format


class TestDeck:
    def test_deck_creation_shuffled(self) -> None:
        deck = Deck(shuffled=True)
        assert len(deck) == 52
        assert bool(deck) is True

    def test_deck_creation_unshuffled(self) -> None:
        deck = Deck(shuffled=False)
        assert len(deck) == 52
        first_card = deck.deal_one()
        assert str(first_card) == "2s"

    def test_deck_shuffle(self) -> None:
        deck1 = Deck(shuffled=False)
        deck2 = Deck(shuffled=False)

        original_order = [str(card) for card in deck1.cards]
        assert [str(card) for card in deck2.cards] == original_order

        deck2.shuffle()
        shuffled_order = [str(card) for card in deck2.cards]
        assert shuffled_order != original_order

    def test_deck_deal_single_card(self) -> None:
        deck = Deck(shuffled=False)
        initial_count = len(deck)
        cards = deck.deal(1)

        assert len(cards) == 1
        assert isinstance(cards[0], Card)
        assert len(deck) == initial_count - 1

    def test_deck_deal_multiple_cards(self) -> None:
        deck = Deck()
        initial_count = len(deck)
        cards = deck.deal(5)

        assert len(cards) == 5
        assert all(isinstance(card, Card) for card in cards)
        assert len(deck) == initial_count - 5

    def test_deck_deal_one(self) -> None:
        deck = Deck()
        initial_count = len(deck)
        card = deck.deal_one()

        assert isinstance(card, Card)
        assert len(deck) == initial_count - 1

    def test_deck_deal_too_many_cards(self) -> None:
        deck = Deck()
        with pytest.raises(AssertionError, match="Cannot deal 53 card"):
            deck.deal(53)

    def test_deck_deal_empty_deck(self) -> None:
        deck = Deck()
        deck.deal(52)
        assert len(deck) == 0
        assert bool(deck) is False

        with pytest.raises(AssertionError, match="Cannot deal 1 card"):
            deck.deal_one()

    def test_deck_reset_shuffled(self) -> None:
        deck = Deck()
        deck.deal(10)
        assert len(deck) == 42

        deck.reset(shuffled=True)
        assert len(deck) == 52

    def test_deck_reset_unshuffled(self) -> None:
        deck = Deck()
        deck.deal(10)
        assert len(deck) == 42

        deck.reset(shuffled=False)
        assert len(deck) == 52
        first_card = deck.deal_one()
        assert str(first_card) == "2s"

    def test_deck_contains_all_cards(self) -> None:
        deck = Deck(shuffled=False)
        card_strings = [str(card) for card in deck.cards]
        assert len(card_strings) == 52
        assert len(set(card_strings)) == 52

        expected_cards = [f"{rank}{suit}" for rank in Card.RANKS for suit in Card.SUITS]
        assert set(card_strings) == set(expected_cards)

    def test_deck_repr(self) -> None:
        deck = Deck()
        assert repr(deck) == "Deck(52 cards)"

        deck.deal(10)
        assert repr(deck) == "Deck(42 cards)"


class TestHand:
    def test_hand_creation(self) -> None:
        hand = Hand()
        assert len(hand) == 0
        assert bool(hand) is False
        assert hand.cards == []

    def test_hand_append_card(self) -> None:
        hand = Hand()
        card1 = Card("As")
        card2 = Card("Kh")

        hand.append(card1)
        assert len(hand) == 1
        assert bool(hand) is True
        assert hand.cards[0] is card1

        hand.append(card2)
        assert len(hand) == 2
        assert hand.cards[1] is card2

    def test_hand_reset(self) -> None:
        hand = Hand()
        hand.append(Card("As"))
        hand.append(Card("Kh"))
        assert len(hand) == 2

        hand.reset()
        assert len(hand) == 0
        assert bool(hand) is False
        assert hand.cards == []

    def test_hand_repr(self) -> None:
        hand = Hand()
        assert repr(hand) == "Hand(0 cards)"

        hand.append(Card("As"))
        assert repr(hand) == "Hand(1 cards)"

        hand.append(Card("Kh"))
        assert repr(hand) == "Hand(2 cards)"


class TestIntegration:
    def test_dealing_cards_to_hand(self) -> None:
        deck = Deck()
        hand = Hand()

        cards = deck.deal(2)
        for card in cards:
            hand.append(card)

        assert len(deck) == 50
        assert len(hand) == 2
        assert all(isinstance(card, Card) for card in hand.cards)

    def test_multiple_hands_from_deck(self) -> None:
        deck = Deck()
        hand1 = Hand()
        hand2 = Hand()

        for card in deck.deal(2):
            hand1.append(card)
        for card in deck.deal(2):
            hand2.append(card)

        assert len(deck) == 48
        assert len(hand1) == 2
        assert len(hand2) == 2

        hand1_cards = set(str(card) for card in hand1.cards)
        hand2_cards = set(str(card) for card in hand2.cards)
        assert hand1_cards.isdisjoint(hand2_cards)

    def test_poker_hand_simulation(self) -> None:
        deck = Deck()
        players = [Hand() for _ in range(4)]
        for _ in range(2):
            for player in players:
                player.append(deck.deal_one())

        assert len(deck) == 44
        assert all(len(player) == 2 for player in players)

        all_dealt_cards: list[str] = []
        for player in players:
            all_dealt_cards.extend(str(card) for card in player.cards)
        assert len(all_dealt_cards) == len(set(all_dealt_cards))
