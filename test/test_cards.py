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

    def test_card_value(self) -> None:
        assert Card("2s").value() == 0
        assert Card("3s").value() == 1
        assert Card("Ts").value() == 8
        assert Card("Js").value() == 9
        assert Card("Qs").value() == 10
        assert Card("Ks").value() == 11
        assert Card("As").value() == 12

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
    def test_hand_creation_empty(self) -> None:
        hand = Hand()
        assert len(hand) == 0
        assert bool(hand) is False
        assert hand.cards == []
    
    def test_hand_creation_with_cards(self) -> None:
        cards = [Card("As"), Card("Kh")]
        hand = Hand(cards)
        assert len(hand) == 2
        assert bool(hand) is True
        assert hand[0].rank == "A"
        assert hand[1].rank == "K"

    def test_hand_append_card(self) -> None:
        hand = Hand()
        card1 = Card("As")
        card2 = Card("Kh")

        hand.append(card1)
        assert len(hand) == 1
        assert bool(hand) is True
        assert hand[0] is card1

        hand.append(card2)
        assert len(hand) == 2
        assert hand[1] is card2
    
    def test_hand_extend(self) -> None:
        hand = Hand([Card("As")])
        new_cards = [Card("Kh"), Card("Qd")]
        
        hand.extend(new_cards)
        assert len(hand) == 3
        assert str(hand[1]) == "Kh"
        assert str(hand[2]) == "Qd"
    
    def test_hand_copy(self) -> None:
        original = Hand([Card("As"), Card("Kh")])
        copy_hand = original.copy()
        
        assert len(copy_hand) == len(original)
        assert copy_hand is not original
        assert copy_hand.cards is not original.cards
        assert str(copy_hand) == str(original)
    
    def test_hand_sort(self) -> None:
        hand = Hand([Card("2s"), Card("As"), Card("Kh")])
        
        hand.sort(reverse=True)
        assert str(hand[0]) == "As"
        assert str(hand[1]) == "Kh" 
        assert str(hand[2]) == "2s"
    
    def test_hand_sorted(self) -> None:
        original = Hand([Card("2s"), Card("As"), Card("Kh")])
        sorted_hand = original.sorted(reverse=True)
        
        # Original unchanged
        assert str(original[0]) == "2s"
        
        # Sorted version correct
        assert str(sorted_hand[0]) == "As"
        assert str(sorted_hand[1]) == "Kh"
        assert str(sorted_hand[2]) == "2s"
    
    def test_hand_iteration(self) -> None:
        cards = [Card("As"), Card("Kh"), Card("Qd")]
        hand = Hand(cards)
        
        result = []
        for card in hand:
            result.append(str(card))
        
        assert result == ["As", "Kh", "Qd"]
    
    def test_hand_contains(self) -> None:
        ace_spades = Card("As")
        hand = Hand([ace_spades, Card("Kh")])
        
        assert ace_spades in hand
        assert Card("Qd") not in hand
    
    def test_hand_value(self) -> None:
        # Test with a known hand (pair of aces)
        hand = Hand([Card("As"), Card("Ah"), Card("Kd"), Card("Qc"), Card("Js")])
        value = hand.value()
        
        assert isinstance(value, int)
        assert value > 0
    
    def test_hand_description(self) -> None:
        # Test with a known hand
        hand = Hand([Card("As"), Card("Ah"), Card("Kd"), Card("Qc"), Card("Js")])
        description = hand.description()
        
        assert "Pair of As" in description
    
    def test_hand_best_five_cards(self) -> None:
        # Test with 7-card hand
        seven_cards = Hand([
            Card("As"), Card("Ah"), Card("Kd"), 
            Card("Qc"), Card("Js"), Card("2h"), Card("3d")
        ])
        
        best_five = seven_cards.best_five_cards()
        assert len(best_five) == 5
        
        # Should exclude the 2 and 3
        best_five_str = str(best_five)
        assert "2h" not in best_five_str
        assert "3d" not in best_five_str
    
    def test_hand_str_representation(self) -> None:
        hand = Hand([Card("As"), Card("Kh"), Card("Qd")])
        assert str(hand) == "As Kh Qd"

    def test_hand_reset(self) -> None:
        hand = Hand([Card("As"), Card("Kh")])
        assert len(hand) == 2

        hand.reset()
        assert len(hand) == 0
        assert bool(hand) is False
        assert hand.cards == []

    def test_hand_repr_representation(self) -> None:
        hand = Hand([Card("As"), Card("Kh")])
        repr_str = repr(hand)
        assert "Hand(2 cards: As Kh)" == repr_str


class TestIntegration:
    def test_dealing_cards_to_hand(self) -> None:
        deck = Deck()
        hand = Hand()

        deck.deal_to_hand(hand, 2)

        assert len(deck) == 50
        assert len(hand) == 2
        assert all(isinstance(card, Card) for card in hand)
    
    def test_deal_hand_method(self) -> None:
        deck = Deck()
        
        hand = deck.deal_hand(5)
        
        assert len(deck) == 47
        assert len(hand) == 5
        assert isinstance(hand, Hand)

    def test_multiple_hands_from_deck(self) -> None:
        deck = Deck()
        hand1 = deck.deal_hand(2)
        hand2 = deck.deal_hand(2)

        assert len(deck) == 48
        assert len(hand1) == 2
        assert len(hand2) == 2

        hand1_cards = set(str(card) for card in hand1)
        hand2_cards = set(str(card) for card in hand2)
        assert hand1_cards.isdisjoint(hand2_cards)

    def test_poker_hand_simulation(self) -> None:
        deck = Deck()
        players_hands = []
        
        for _ in range(4):
            hand = deck.deal_hand(2)
            players_hands.append(hand)

        assert len(deck) == 44
        assert all(len(hand) == 2 for hand in players_hands)

        all_dealt_cards = []
        for hand in players_hands:
            all_dealt_cards.extend(str(card) for card in hand)
        assert len(all_dealt_cards) == len(set(all_dealt_cards))
    
    def test_hand_evaluation_integration(self) -> None:
        # Test that Hand.value() works correctly
        royal_flush = Hand([
            Card("As"), Card("Ks"), Card("Qs"), Card("Js"), Card("Ts")
        ])
        
        high_card = Hand([
            Card("Ah"), Card("Kd"), Card("Qc"), Card("Jh"), Card("9s")
        ])
        
        # Royal flush should have a lower score (better) than high card
        assert royal_flush.value() < high_card.value()
        
        # Test descriptions
        assert "Royal Flush" in royal_flush.description()
        assert "high" in high_card.description()
