import pytest

from sop_assistant.retrieval_report import measure_ranking


def test_ranking_deduplicates_pages_and_uses_all_required_sources():
    relevant = {("a.pdf", 1), ("b.pdf", 1)}
    ranked = [("x.pdf", 1), ("a.pdf", 1), ("a.pdf", 1), ("b.pdf", 1)]
    result = measure_ranking(relevant, ranked)
    assert result["mrr"] == 0.5
    assert result["recall@1"] == 0
    assert result["recall@2"] == 0.5
    assert result["recall@4"] == 1


def test_missing_relevant_page_is_not_full_recall():
    result = measure_ranking({("a.pdf", 1)}, [("x.pdf", 1)])
    assert result["mrr"] == 0
    assert result["recall@4"] == 0


def test_no_reference_pages_is_not_a_perfect_score():
    with pytest.raises(ValueError):
        measure_ranking(set(), [])
