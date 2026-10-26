import pytest

from sop_assistant.report import render_report


def test_report_summarizes_scores_without_treating_unscored_as_zero():
    report = render_report(
        {
            "scores": [
                {"id": "answer", "status_matches": True, "faithfulness": 1.0},
                {
                    "id": "missing",
                    "status_matches": True,
                    "faithfulness": None,
                    "note": "Manual review required.",
                },
                {"id": "partial", "status_matches": False, "faithfulness": 0.5},
            ]
        }
    )
    assert "0.750" in report
    assert "2/3" in report
    assert "Not scored" in report
    assert "Manual review required." in report
    assert "not a correctness" in report


def test_empty_scores_have_no_invented_average():
    report = render_report({"scores": []})
    assert "N/A" in report
    assert "0/0" in report


def test_report_escapes_table_cells():
    report = render_report(
        {
            "scores": [
                {"id": "a|b\nc", "status_matches": True, "faithfulness": None},
            ]
        }
    )
    assert "a\\|b c" in report


def test_comprehensive_report_explains_failures_and_denominators():
    report = render_report(
        {
            "schema_version": 2,
            "complete": False,
            "expected_cases": 2,
            "processed_cases": 1,
            "provenance": {},
            "scores": [
                {
                    "id": "refund",
                    "status_matches": True,
                    "sample": {
                        "user_input": "Amount?",
                        "response": "Not specified.",
                        "reference": "Unknown",
                        "statements": [],
                        "evidence": [],
                    },
                    "metrics": {
                        "citation_support": {
                            "status": "scored",
                            "value": 0.0,
                            "reason": "Wrong passage",
                        },
                        "context_recall": {
                            "status": "skipped",
                            "value": None,
                            "reason": "Unsupported question",
                        },
                    },
                }
            ],
        }
    )
    assert "Incomplete" in report
    assert "Wrong passage" in report
    assert "Amount?" in report
    assert "citation_support" in report
    assert "not a production" in report


def test_rounding_noise_is_not_reported_as_a_review_finding():
    report = render_report(
        {
            "schema_version": 2,
            "complete": True,
            "expected_cases": 1,
            "processed_cases": 1,
            "scores": [
                {
                    "id": "a",
                    "status_matches": True,
                    "metrics": {
                        "context_precision": {
                            "status": "scored",
                            "value": 0.9999999999,
                            "reason": "",
                        }
                    },
                }
            ],
        }
    )
    assert "**a / context_precision**" not in report


def test_report_does_not_assume_four_pages_or_ten_cases():
    report = render_report(
        {
            "schema_version": 2,
            "scores": [],
            "expected_cases": 0,
            "processed_cases": 0,
            "complete": True,
        }
    )
    assert "All four SOP pages are retrieved" not in report
    assert "Ten development cases" not in report


def test_report_rejects_missing_scores():
    with pytest.raises(ValueError, match="scores"):
        render_report({"results": []})
