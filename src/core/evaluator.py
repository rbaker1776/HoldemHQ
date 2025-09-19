from src.core.cards import Card
from collections import Counter
from typing import Optional


def evaluate_hand(hand: list[Card]) -> int:
    assert 2 <= len(hand) <= 7, (
        f"Hand must contain between [2, 7] cards, not {len(hand)}"
    )

    sorted_cards = sorted(hand, reverse=True)
    ranks = [abs(card) for card in sorted_cards]
    suits = [card.suit for card in sorted_cards]

    rank_counts = Counter(ranks)
    count_frequencies = Counter(rank_counts.values())

    is_flush = len(set(suits)) == 1 and len(hand) >= 5

    straight_high = _get_straight_high(ranks)
    is_straight = straight_high is not None

    if is_straight and is_flush:
        return _build_score(1, [12 - straight_high])  # type: ignore[operator]

    if 4 in count_frequencies:
        quad_rank = _get_rank_with_count(rank_counts, 4)
        kickers = _get_kickers(ranks, [quad_rank], 1)
        return _build_score(2, [12 - quad_rank] + [12 - k for k in kickers])

    if 3 in count_frequencies and 2 in count_frequencies:
        trips_rank = _get_rank_with_count(rank_counts, 3)
        pair_rank = _get_rank_with_count(rank_counts, 2)
        return _build_score(3, [12 - trips_rank, 12 - pair_rank])

    if is_flush:
        flush_cards = ranks[:5]
        return _build_score(4, [12 - r for r in flush_cards])

    if is_straight:
        return _build_score(5, [12 - straight_high])  # type: ignore[operator]

    if 3 in count_frequencies:
        trips_rank = _get_rank_with_count(rank_counts, 3)
        kickers = _get_kickers(ranks, [trips_rank], 2)
        return _build_score(6, [12 - trips_rank] + [12 - k for k in kickers])

    if count_frequencies[2] >= 2:
        pairs = _get_ranks_with_count(rank_counts, 2)
        pairs.sort(reverse=True)
        high_pair, low_pair = pairs[0], pairs[1]
        kickers = _get_kickers(ranks, pairs, 1)
        return _build_score(
            7, [12 - high_pair, 12 - low_pair] + [12 - k for k in kickers]
        )

    if 2 in count_frequencies:
        pair_rank = _get_rank_with_count(rank_counts, 2)
        kickers = _get_kickers(ranks, [pair_rank], 3)
        return _build_score(8, [12 - pair_rank] + [12 - k for k in kickers])

    high_cards = ranks[:5]
    return _build_score(9, [12 - r for r in high_cards])


def _build_score(hand_type: int, components: list[int]) -> int:
    score = hand_type * 100000000000  # Ensure hand types don't overlap

    for i, component in enumerate(components):
        score += component * (100 ** (5 - i))

    return score


def _get_straight_high(ranks: list[int]) -> Optional[int]:
    unique_ranks = sorted(set(ranks), reverse=True)

    # Check for regular straight
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i + 4] == 4:
            return unique_ranks[i]

    # Check for wheel (A-2-3-4-5)
    if set([12, 0, 1, 2, 3]).issubset(set(unique_ranks)):
        return 3  # 5-high straight

    return None


def _get_rank_with_count(rank_counts: Counter[int], count: int) -> int:
    for rank, freq in rank_counts.items():
        if freq == count:
            return rank
    raise ValueError(f"No rank found with count {count}")


def _get_ranks_with_count(rank_counts: Counter[int], count: int) -> list[int]:
    return [rank for rank, freq in rank_counts.items() if freq == count]


def _get_kickers(
    ranks: list[int], exclude_ranks: list[int], num_kickers: int
) -> list[int]:
    kickers = []
    exclude_set = set(exclude_ranks)

    for rank in ranks:
        if rank not in exclude_set and rank not in kickers:
            kickers.append(rank)
            if len(kickers) >= num_kickers:
                break

    return kickers


def get_hand_description(hand: list[Card]) -> str:
    if len(hand) < 2:
        return "Invalid hand"

    sorted_cards = sorted(hand, reverse=True)
    ranks = [abs(card) for card in sorted_cards]
    suits = [card.suit for card in sorted_cards]

    rank_counts = Counter(ranks)
    count_frequencies = Counter(rank_counts.values())

    is_flush = len(set(suits)) == 1 and len(hand) >= 5
    straight_high = _get_straight_high(ranks)
    is_straight = straight_high is not None

    def rank_name(rank: int) -> str:
        return ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"][rank]

    if is_straight and is_flush:
        if straight_high == 12:
            return "Royal Flush"
        else:
            return f"Straight Flush, {rank_name(straight_high)} high"  # type: ignore[arg-type]

    if 4 in count_frequencies:
        quad_rank = _get_rank_with_count(rank_counts, 4)
        return f"Four of a Kind, {rank_name(quad_rank)}s"

    if 3 in count_frequencies and 2 in count_frequencies:
        trips_rank = _get_rank_with_count(rank_counts, 3)
        pair_rank = _get_rank_with_count(rank_counts, 2)
        return f"Full House, {rank_name(trips_rank)}s over {rank_name(pair_rank)}s"

    if is_flush:
        high_card = max(ranks)
        return f"Flush, {rank_name(high_card)} high"

    if is_straight:
        return f"Straight, {rank_name(straight_high)} high"  # type: ignore[arg-type]

    if 3 in count_frequencies:
        trips_rank = _get_rank_with_count(rank_counts, 3)
        return f"Three of a Kind, {rank_name(trips_rank)}s"

    if count_frequencies[2] >= 2:
        pairs = _get_ranks_with_count(rank_counts, 2)
        pairs.sort(reverse=True)
        return f"Two Pair, {rank_name(pairs[0])}s and {rank_name(pairs[1])}s"

    if 2 in count_frequencies:
        pair_rank = _get_rank_with_count(rank_counts, 2)
        return f"Pair of {rank_name(pair_rank)}s"

    high_card = max(ranks)
    return f"{rank_name(high_card)} high"
