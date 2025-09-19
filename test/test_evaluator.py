import pytest
import random
from itertools import combinations, product
from hypothesis import given, strategies as st, assume, settings
from src.core.cards import Card, Deck
from src.core.evaluator import evaluate_hand, get_hand_description


ROYAL_FLUSH = [
    Card("A", "s"),
    Card("K", "s"),
    Card("Q", "s"),
    Card("J", "s"),
    Card("T", "s"),
]
STRAIGHT_FLUSH = [
    Card("9", "h"),
    Card("8", "h"),
    Card("7", "h"),
    Card("6", "h"),
    Card("5", "h"),
]
FOUR_KIND = [
    Card("A", "s"),
    Card("A", "h"),
    Card("A", "d"),
    Card("A", "c"),
    Card("K", "s"),
]
FULL_HOUSE = [
    Card("K", "s"),
    Card("K", "h"),
    Card("K", "d"),
    Card("Q", "s"),
    Card("Q", "h"),
]
FLUSH = [Card("A", "s"), Card("J", "s"), Card("9", "s"), Card("7", "s"), Card("5", "s")]
STRAIGHT = [
    Card("A", "s"),
    Card("K", "h"),
    Card("Q", "d"),
    Card("J", "c"),
    Card("T", "s"),
]
THREE_KIND = [
    Card("K", "s"),
    Card("K", "h"),
    Card("K", "d"),
    Card("A", "s"),
    Card("Q", "h"),
]
TWO_PAIR = [
    Card("K", "s"),
    Card("K", "h"),
    Card("Q", "d"),
    Card("Q", "s"),
    Card("A", "h"),
]
ONE_PAIR = [
    Card("K", "s"),
    Card("K", "h"),
    Card("A", "d"),
    Card("Q", "s"),
    Card("J", "h"),
]
HIGH_CARD = [
    Card("A", "s"),
    Card("K", "h"),
    Card("Q", "d"),
    Card("J", "s"),
    Card("9", "h"),
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
            hand = [Card("A", "s")]
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
            Card(quad_rank, "s"),
            Card(quad_rank, "h"),
            Card(quad_rank, "d"),
            Card(quad_rank, "c"),
            Card(kicker1, "s"),
        ]
        hand2 = [
            Card(quad_rank, "s"),
            Card(quad_rank, "h"),
            Card(quad_rank, "d"),
            Card(quad_rank, "c"),
            Card(kicker2, "s"),
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
            Card(trips, "s"),
            Card(trips, "h"),
            Card(trips, "d"),
            Card(pair1, "s"),
            Card(pair1, "h"),
        ]
        hand2 = [
            Card(trips, "s"),
            Card(trips, "h"),
            Card(trips, "d"),
            Card(pair2, "s"),
            Card(pair2, "h"),
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
            Card("A", suit),
            Card("K", suit),
            Card("Q", suit),
            Card("J", suit),
            Card("9", suit),
        ]
        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Flush" in description

        non_flush = [
            Card("A", "s"),
            Card("K", "h"),
            Card("Q", "d"),
            Card("J", "c"),
            Card("9", "s"),
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
                Card(rank, ["s", "h", "d", "c"][i % 4])
                for i, rank in enumerate(straight_ranks)
            ]
            score = evaluate_hand(hand)
            description = get_hand_description(hand)
            assert "Straight" in description

    def test_wheel_straight_edge_cases(self) -> None:
        wheel = [
            Card("A", "s"),
            Card("2", "h"),
            Card("3", "d"),
            Card("4", "c"),
            Card("5", "s"),
        ]
        wheel_score = evaluate_hand(wheel)

        wheel_7 = wheel + [Card("K", "h"), Card("Q", "d")]
        wheel_7_score = evaluate_hand(wheel_7)

        assert wheel_score == wheel_7_score

        six_high = [
            Card("6", "s"),
            Card("5", "h"),
            Card("4", "d"),
            Card("3", "c"),
            Card("2", "s"),
        ]
        six_high_score = evaluate_hand(six_high)
        assert wheel_score > six_high_score

    def test_wheel_straight_flush(self) -> None:
        wheel_sf = [
            Card("A", "s"),
            Card("2", "s"),
            Card("3", "s"),
            Card("4", "s"),
            Card("5", "s"),
        ]
        regular_sf = [
            Card("6", "h"),
            Card("5", "h"),
            Card("4", "h"),
            Card("3", "h"),
            Card("2", "h"),
        ]

        wheel_score = evaluate_hand(wheel_sf)
        regular_score = evaluate_hand(regular_sf)

        assert wheel_score > regular_score

        description = get_hand_description(wheel_sf)
        assert "Straight Flush, 5 high" in description

    def test_multiple_pairs_edge_cases(self) -> None:
        hand = [
            Card("A", "s"),
            Card("A", "h"),
            Card("K", "d"),
            Card("K", "s"),
            Card("Q", "c"),
            Card("Q", "h"),
            Card("J", "d"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Two Pair, As and Ks" in description

    def test_full_house_vs_two_pair_in_seven_cards(self) -> None:
        hand = [
            Card("A", "s"),
            Card("A", "h"),
            Card("A", "d"),
            Card("K", "s"),
            Card("K", "h"),
            Card("Q", "c"),
            Card("J", "d"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Full House" in description

    def test_flush_vs_straight_priority(self) -> None:
        flush_hand = [
            Card("A", "s"),
            Card("J", "s"),
            Card("9", "s"),
            Card("7", "s"),
            Card("5", "s"),
        ]
        straight_hand = [
            Card("A", "s"),
            Card("K", "h"),
            Card("Q", "d"),
            Card("J", "c"),
            Card("T", "s"),
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
        hand = [Card(rank, suit) for rank, suit in card_tuples]
        score = evaluate_hand(hand)

        assert isinstance(score, int)
        assert score > 0

        description = get_hand_description(hand)
        assert len(description) > 0
        assert description != "Invalid hand"

    def test_deterministic_evaluation(self) -> None:
        hand = [
            Card("A", "s"),
            Card("K", "h"),
            Card("Q", "d"),
            Card("J", "c"),
            Card("T", "s"),
        ]

        scores = [evaluate_hand(hand.copy()) for _ in range(100)]
        assert len(set(scores)) == 1, "Hand evaluation should be deterministic"

    def test_hand_order_independence(self) -> None:
        cards = [
            Card("A", "s"),
            Card("K", "h"),
            Card("Q", "d"),
            Card("J", "c"),
            Card("T", "s"),
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
            Card(rank1, "s"),
            Card(rank1, "h"),
            Card("K", "d"),
            Card("Q", "c"),
            Card("J", "s"),
        ]
        pair2 = [
            Card(rank2, "s"),
            Card(rank2, "h"),
            Card("K", "d"),
            Card("Q", "c"),
            Card("J", "s"),
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
                            hand[i] = Card(replacement, hand[i].suit)
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
            flush_hand = [Card(rank, suit) for rank in ranks]
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
            Card("A", "s"),
            Card("K", "s"),
            Card("Q", "s"),
            Card("J", "s"),
            Card("T", "s"),
        ]
        hand2 = [
            Card("A", "h"),
            Card("K", "h"),
            Card("Q", "h"),
            Card("J", "h"),
            Card("T", "h"),
        ]
        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)
        assert score1 == score2

    def test_six_card_flush_uses_best_five(self) -> None:
        six_card_flush = [
            Card("A", "s"),
            Card("K", "s"),
            Card("Q", "s"),
            Card("J", "s"),
            Card("T", "s"),
            Card("2", "s"),
        ]

        five_card_flush = [
            Card("A", "h"),
            Card("K", "h"),
            Card("Q", "h"),
            Card("J", "h"),
            Card("T", "h"),
        ]

        score_6 = evaluate_hand(six_card_flush)
        score_5 = evaluate_hand(five_card_flush)

        assert score_6 == score_5

    def test_worst_case_performance_patterns(self) -> None:
        alternating = [
            Card("A", "s"),
            Card("2", "h"),
            Card("K", "d"),
            Card("3", "c"),
            Card("Q", "s"),
        ]
        score = evaluate_hand(alternating)
        assert isinstance(score, int)

        all_diff_suits = [
            Card("A", "s"),
            Card("K", "h"),
            Card("Q", "d"),
            Card("J", "c"),
            Card("T", "s"),
        ]
        score = evaluate_hand(all_diff_suits)
        assert isinstance(score, int)

    def test_card_comparison_integration(self) -> None:
        hand = [
            Card("A", "s"),
            Card("2", "h"),
            Card("3", "d"),
            Card("4", "c"),
            Card("5", "s"),
        ]

        score = evaluate_hand(hand)
        description = get_hand_description(hand)
        assert "Straight, 5 high" in description

    def test_card_equality_edge_cases(self) -> None:
        hand1 = [
            Card("A", "s"),
            Card("A", "h"),
            Card("K", "d"),
            Card("Q", "c"),
            Card("J", "s"),
        ]
        hand2 = [
            Card("A", "d"),
            Card("A", "c"),
            Card("K", "s"),
            Card("Q", "h"),
            Card("J", "d"),
        ]

        score1 = evaluate_hand(hand1)
        score2 = evaluate_hand(hand2)

        assert score1 == score2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
