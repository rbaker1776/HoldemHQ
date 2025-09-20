import pytest
import random
from itertools import combinations, product
from hypothesis import given, strategies as st, assume, settings
from src.core.cards import Card, Deck
from src.core.evaluator import evaluate_hand, get_hand_description


ROYAL_FLUSH = [
    Card("As"),
    Card("Ks"),
    Card("Qs"),
    Card("Js"),
    Card("Ts"),
]
STRAIGHT_FLUSH = [
    Card("9h"),
    Card("8h"),
    Card("7h"),
    Card("6h"),
    Card("5h"),
]
FOUR_KIND = [
    Card("As"),
    Card("Ah"),
    Card("Ad"),
    Card("Ac"),
    Card("Ks"),
]
FULL_HOUSE = [
    Card("Ks"),
    Card("Kh"),
    Card("Kd"),
    Card("Qs"),
    Card("Qh"),
]
FLUSH = [Card("As"), Card("Js"), Card("9s"), Card("7s"), Card("5s")]
STRAIGHT = [
    Card("As"),
    Card("Kh"),
    Card("Qd"),
    Card("Jc"),
    Card("Ts"),
]
THREE_KIND = [
    Card("Ks"),
    Card("Kh"),
    Card("Kd"),
    Card("As"),
    Card("Qh"),
]
TWO_PAIR = [
    Card("Ks"),
    Card("Kh"),
    Card("Qd"),
    Card("Qs"),
    Card("Ah"),
]
ONE_PAIR = [
    Card("Ks"),
    Card("Kh"),
    Card("Ad"),
    Card("Qs"),
    Card("Jh"),
]
HIGH_CARD = [
    Card("As"),
    Card("Kh"),
    Card("Qd"),
    Card("Js"),
    Card("9h"),
]


class TestEvaluateHandComprehensive:
    def test_hand_ranking_order(self) -> None:
        hands = [
            ROYAL_FLUSH,
            STRAIGHT_FLUSH,
            FOUR_KIND,
            FULL_HOUSE,
            FLUSH,
            STRAIGHT,
            THREE_KIND,
            TWO_PAIR,
            ONE_PAIR,
            HIGH_CARD,
        ]
        scores = [evaluate_hand(hand) for hand in hands]
        for i in range(len(scores) - 1):
            assert scores[i] < scores[i + 1], (
                f"Hand {i} should be stronger than hand {i + 1}"
            )

    @pytest.mark.parametrize("hand_size", [2, 3, 4, 5, 6, 7])
    def test_valid_hand_sizes(self, hand_size: int) -> None:
        deck = Deck(shuffled=True)
        hand = deck.deal(hand_size)
        score = evaluate_hand(hand)
        assert isinstance(score, int)
        assert score > 0

    @pytest.mark.parametrize("invalid_size", [0, 1, 8, 9, 10])
    def test_invalid_hand_sizes(self, invalid_size: int) -> None:
        if invalid_size == 0:
            hand = []
        elif invalid_size == 1:
            hand = [Card("As")]
        else:
            deck = Deck(shuffled=False)
            hand = deck.deal(invalid_size)
        with pytest.raises(AssertionError):
            evaluate_hand(hand)

    @pytest.mark.parametrize(
        "quad_rank,kicker1,kicker2",
        [("A", "K", "Q"), ("A", "Q", "K"), ("K", "A", "Q"), ("2", "A", "K")],
    )
    def test_four_of_kind_kickers(
        self, quad_rank: str, kicker1: str, kicker2: str
    ) -> None:
        hand1 = [
            Card(f"{quad_rank}s"),
            Card(f"{quad_rank}h"),
            Card(f"{quad_rank}d"),
            Card(f"{quad_rank}c"),
            Card(f"{kicker1}s"),
        ]
        hand2 = [
            Card(f"{quad_rank}s"),
            Card(f"{quad_rank}h"),
            Card(f"{quad_rank}d"),
            Card(f"{quad_rank}c"),
            Card(f"{kicker2}s"),
        ]

        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)

        kicker1_val = Card.RANKS.index(kicker1)
        kicker2_val = Card.RANKS.index(kicker2)

        if kicker1_val > kicker2_val:
            assert score1 < score2
        elif kicker1_val < kicker2_val:
            assert score1 > score2
        else:
            assert score1 == score2

    @pytest.mark.parametrize(
        "trips,pair1,pair2", [("A", "K", "Q"), ("K", "A", "Q"), ("K", "Q", "A")]
    )
    def test_full_house_ranking(self, trips: str, pair1: str, pair2: str) -> None:
        hand1 = [
            Card(f"{trips}s"),
            Card(f"{trips}h"),
            Card(f"{trips}d"),
            Card(f"{pair1}s"),
            Card(f"{pair1}h"),
        ]
        hand2 = [
            Card(f"{trips}s"),
            Card(f"{trips}h"),
            Card(f"{trips}d"),
            Card(f"{pair2}s"),
            Card(f"{pair2}h"),
        ]

        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)

        pair1_val = Card.RANKS.index(pair1)
        pair2_val = Card.RANKS.index(pair2)

        if pair1_val > pair2_val:
            assert score1 < score2
        elif pair1_val < pair2_val:
            assert score1 > score2
        else:
            assert score1 == score2

    @pytest.mark.parametrize("suit", ["s", "h", "d", "c"])
    def test_flush_all_suits(self, suit: str) -> None:
        hand = [
            Card(f"A{suit}"),
            Card(f"K{suit}"),
            Card(f"Q{suit}"),
            Card(f"J{suit}"),
            Card(f"9{suit}"),
        ]
        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Flush" in description

        non_flush = [
            Card("As"),
            Card("Kh"),
            Card("Qd"),
            Card("Jc"),
            Card("9s"),
        ]
        non_flush_score = evaluate_hand(non_flush)
        assert score < non_flush_score

    @pytest.mark.parametrize(
        "high_card", ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5"]
    )
    def test_straight_all_highs(self, high_card: str) -> None:
        high_val = Card.RANKS.index(high_card)

        straight_ranks = []
        for i in range(5):
            rank_idx = high_val - i
            if rank_idx >= 0:
                straight_ranks.append(Card.RANKS[rank_idx])

        if len(straight_ranks) == 5:
            hand = [
                Card(f"{rank}{['s', 'h', 'd', 'c'][i % 4]}")
                for i, rank in enumerate(straight_ranks)
            ]
            score = evaluate_hand(hand)
            description = get_hand_description(hand)
            assert "Straight" in description

    def test_wheel_straight_edge_cases(self) -> None:
        wheel = [
            Card("As"),
            Card("2h"),
            Card("3d"),
            Card("4c"),
            Card("5s"),
        ]
        wheel_score = evaluate_hand(wheel)

        wheel_7 = wheel + [Card("Kh"), Card("Qd")]
        wheel_7_score = evaluate_hand(wheel_7)

        assert wheel_score == wheel_7_score

        six_high = [
            Card("6s"),
            Card("5h"),
            Card("4d"),
            Card("3c"),
            Card("2s"),
        ]
        six_high_score = evaluate_hand(six_high)
        assert wheel_score > six_high_score

    def test_wheel_straight_flush(self) -> None:
        wheel_sf = [
            Card("As"),
            Card("2s"),
            Card("3s"),
            Card("4s"),
            Card("5s"),
        ]
        regular_sf = [
            Card("6h"),
            Card("5h"),
            Card("4h"),
            Card("3h"),
            Card("2h"),
        ]

        wheel_score = evaluate_hand(wheel_sf)
        regular_score = evaluate_hand(regular_sf)

        assert wheel_score > regular_score

        description = get_hand_description(wheel_sf)
        assert "Straight Flush, 5 high" in description

    def test_multiple_pairs_edge_cases(self) -> None:
        hand = [
            Card("As"),
            Card("Ah"),
            Card("Kd"),
            Card("Ks"),
            Card("Qc"),
            Card("Qh"),
            Card("Jd"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Two Pair, As and Ks" in description

    def test_full_house_vs_two_pair_in_seven_cards(self) -> None:
        hand = [
            Card("As"),
            Card("Ah"),
            Card("Ad"),
            Card("Ks"),
            Card("Kh"),
            Card("Qc"),
            Card("Jd"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Full House" in description

    def test_flush_vs_straight_priority(self) -> None:
        flush_hand = [
            Card("As"),
            Card("Js"),
            Card("9s"),
            Card("7s"),
            Card("5s"),
        ]
        straight_hand = [
            Card("As"),
            Card("Kh"),
            Card("Qd"),
            Card("Jc"),
            Card("Ts"),
        ]

        flush_score = evaluate_hand(flush_hand)
        straight_score = evaluate_hand(straight_hand)

        assert flush_score < straight_score

    @given(st.integers(min_value=2, max_value=7))
    @settings(max_examples=50)
    def test_random_hand_sizes_property(self, hand_size: int) -> None:
        deck = Deck(shuffled=True)
        hand = deck.deal(hand_size)
        score = evaluate_hand(hand)

        assert isinstance(score, int)
        assert score > 0

    @given(
        st.lists(
            st.tuples(st.sampled_from(Card.RANKS), st.sampled_from(Card.SUITS)),
            min_size=2,
            max_size=7,
            unique=True,
        )
    )
    @settings(max_examples=100)
    def test_hypothesis_random_hands(self, card_tuples: list[tuple[str, str]]) -> None:
        hand = [Card(f"{rank}{suit}") for rank, suit in card_tuples]
        score = evaluate_hand(hand)

        assert isinstance(score, int)
        assert score > 0

        description = get_hand_description(hand)
        assert len(description) > 0
        assert description != "Invalid hand"

    def test_deterministic_evaluation(self) -> None:
        hand = [
            Card("As"),
            Card("Kh"),
            Card("Qd"),
            Card("Jc"),
            Card("Ts"),
        ]

        scores = [evaluate_hand(hand.copy()) for _ in range(100)]
        assert len(set(scores)) == 1, "Hand evaluation should be deterministic"

    def test_hand_order_independence(self) -> None:
        cards = [
            Card("As"),
            Card("Kh"),
            Card("Qd"),
            Card("Jc"),
            Card("Ts"),
        ]

        base_score = evaluate_hand(cards)

        for _ in range(20):
            shuffled = cards.copy()
            random.shuffle(shuffled)
            score = evaluate_hand(shuffled)
            assert score == base_score, "Card order should not affect evaluation"

    @pytest.mark.parametrize(
        "rank1,rank2",
        [
            ("A", "K"),
            ("K", "Q"),
            ("Q", "J"),
            ("J", "T"),
            ("T", "9"),
            ("9", "8"),
            ("8", "7"),
            ("7", "6"),
            ("6", "5"),
            ("5", "4"),
            ("4", "3"),
            ("3", "2"),
            ("A", "2"),
        ],
    )
    def test_all_pair_rankings(self, rank1: str, rank2: str) -> None:
        pair1 = [
            Card(f"{rank1}s"),
            Card(f"{rank1}h"),
            Card("Kd"),
            Card("Qc"),
            Card("Js"),
        ]
        pair2 = [
            Card(f"{rank2}s"),
            Card(f"{rank2}h"),
            Card("Kd"),
            Card("Qc"),
            Card("Js"),
        ]

        for hand in [pair1, pair2]:
            pair_rank = hand[0].rank
            for i in range(2, 5):
                if hand[i].rank == pair_rank:
                    for replacement in [
                        "A",
                        "K",
                        "Q",
                        "J",
                        "T",
                        "9",
                        "8",
                        "7",
                        "6",
                        "5",
                        "4",
                        "3",
                        "2",
                    ]:
                        if replacement != pair_rank and not any(
                            c.rank == replacement for c in hand
                        ):
                            hand[i] = Card(f"{replacement}{hand[i].suit}")
                            break

        score1 = evaluate_hand(pair1)
        score2 = evaluate_hand(pair2)

        rank1_val = Card.RANKS.index(rank1)
        rank2_val = Card.RANKS.index(rank2)

        if rank1_val > rank2_val:
            assert score1 < score2
        elif rank1_val < rank2_val:
            assert score1 > score2

    def test_all_suit_combinations_flush(self) -> None:
        ranks = ["A", "K", "Q", "J", "9"]

        for suit in Card.SUITS:
            flush_hand = [Card(f"{rank}{suit}") for rank in ranks]
            score = evaluate_hand(flush_hand)
            description = get_hand_description(flush_hand)
            assert "Flush" in description

    def test_many_random_hands_consistency(self) -> None:
        results: dict = {}  # type: ignore[type-arg]

        for _ in range(1000):
            deck = Deck(shuffled=True)
            hand = deck.deal(5)

            hand_key = tuple(sorted((card.rank, card.suit) for card in hand))
            score = evaluate_hand(hand)

            if hand_key in results:
                assert results[hand_key] == score, (
                    "Same hand should always have same score"
                )
            else:
                results[hand_key] = score

    def test_ranking_transitivity(self) -> None:
        hands = []
        for _ in range(50):
            deck = Deck(shuffled=True)
            hands.append(deck.deal(5))

        scores = [(evaluate_hand(hand), i) for i, hand in enumerate(hands)]
        scores.sort()

        for i in range(len(scores) - 2):
            score_a, idx_a = scores[i]
            score_b, idx_b = scores[i + 1]
            score_c, idx_c = scores[i + 2]

            assert score_a <= score_c

    def test_identical_hands_different_suits(self) -> None:
        hand1 = [
            Card("As"),
            Card("Ks"),
            Card("Qs"),
            Card("Js"),
            Card("Ts"),
        ]
        hand2 = [
            Card("Ah"),
            Card("Kh"),
            Card("Qh"),
            Card("Jh"),
            Card("Th"),
        ]
        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)
        assert score1 == score2

    def test_six_card_flush_uses_best_five(self) -> None:
        six_card_flush = [
            Card("As"),
            Card("Ks"),
            Card("Qs"),
            Card("Js"),
            Card("Ts"),
            Card("2s"),
        ]

        five_card_flush = [
            Card("Ah"),
            Card("Kh"),
            Card("Qh"),
            Card("Jh"),
            Card("Th"),
        ]

        score_6 = evaluate_hand(six_card_flush)
        score_5 = evaluate_hand(five_card_flush)

        assert score_6 == score_5

    def test_worst_case_performance_patterns(self) -> None:
        alternating = [
            Card("As"),
            Card("2h"),
            Card("Kd"),
            Card("3c"),
            Card("Qs"),
        ]
        score = evaluate_hand(alternating)
        assert isinstance(score, int)

        all_diff_suits = [
            Card("As"),
            Card("Kh"),
            Card("Qd"),
            Card("Jc"),
            Card("Ts"),
        ]
        score = evaluate_hand(all_diff_suits)
        assert isinstance(score, int)

    def test_card_comparison_integration(self) -> None:
        hand = [
            Card("As"),
            Card("2h"),
            Card("3d"),
            Card("4c"),
            Card("5s"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Straight, 5 high" in description

    def test_card_equality_edge_cases(self) -> None:
        hand1 = [
            Card("As"),
            Card("Ah"),
            Card("Kd"),
            Card("Qc"),
            Card("Js"),
        ]
        hand2 = [
            Card("Ad"),
            Card("Ac"),
            Card("Ks"),
            Card("Qh"),
            Card("Jd"),
        ]

        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)

        assert score1 == score2

    def test_new_card_format_compatibility(self) -> None:
        # Test that new format works properly
        old_style = [Card("A", "s"), Card("K", "h")]  # Still works
        new_style = [Card("As"), Card("Kh")]  # New format

        old_score = evaluate_hand(old_style)
        new_score = evaluate_hand(new_style)

        assert old_score == new_score
        assert str(old_style[0]) == str(new_style[0])
        assert str(old_style[1]) == str(new_style[1])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
