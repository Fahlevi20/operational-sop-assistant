import pytest

from sop_assistant.qa import Answer, Statement, validate_answer

EVIDENCE = [{"id": "a", "source": "policy.pdf", "page": 1, "text": "Initial response 15 minutes."}]


def test_answer_resolves_trusted_citation():
    result = validate_answer(
        Answer(status="answered", statements=[Statement(text="15 minutes.", evidence_ids=["a"])]),
        EVIDENCE,
    )
    assert result["citations"][0]["source"] == "policy.pdf"
    assert result["citations"][0]["page"] == 1


@pytest.mark.parametrize("ids", [[], ["invented"]])
def test_answer_rejects_missing_or_unknown_evidence(ids):
    with pytest.raises(ValueError, match="citation"):
        validate_answer(
            Answer(status="answered", statements=[Statement(text="A claim.", evidence_ids=ids)]),
            EVIDENCE,
        )


def test_unsupported_requires_no_fabricated_claims():
    result = validate_answer(
        Answer(status="unsupported", message="Tidak disebutkan dalam SOP."), EVIDENCE
    )
    assert result["status"] == "unsupported"
    assert result["citations"] == []


def test_empty_answer_rejected():
    with pytest.raises(ValueError):
        validate_answer(Answer(status="answered"), EVIDENCE)


def test_answer_rejects_uncited_message():
    with pytest.raises(ValueError, match="message"):
        validate_answer(
            Answer(
                status="answered",
                message="Invented compensation.",
                statements=[Statement(text="15 minutes.", evidence_ids=["a"])],
            ),
            EVIDENCE,
        )


def test_clarification_requires_message():
    with pytest.raises(ValueError):
        validate_answer(Answer(status="needs_clarification"), EVIDENCE)
