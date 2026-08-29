"""Tests eval/accuracy.py's pure comparison functions, and separately
sanity-checks the hand-labeled fixture data itself: every labeled
raw_text excerpt must actually appear in its contract's full text, or the
"ground truth" used for extraction-accuracy scoring would itself be wrong
(the same class of self-caught fixture bug as project 07's seed data).
"""

from contractreview.data.contracts import CONTRACT_TEXTS, LABELED_EXTRACTIONS
from contractreview.eval.accuracy import compare_to_labeled, raw_text_is_grounded


def test_identical_extraction_scores_perfect_accuracy():
    labeled = LABELED_EXTRACTIONS["acme_standard"]
    result = compare_to_labeled(labeled, labeled)
    assert result.accuracy == 1.0
    assert result.mismatched_fields == []


def test_mismatched_field_is_detected():
    labeled = LABELED_EXTRACTIONS["acme_standard"]
    wrong = labeled.model_copy(update={
        "governing_law": labeled.governing_law.model_copy(update={"jurisdiction": "Nevada"})
    })
    result = compare_to_labeled(wrong, labeled)
    assert result.accuracy < 1.0
    assert "governing_law.jurisdiction" in result.mismatched_fields


def test_all_labeled_fixtures_are_internally_consistent_with_playbook_flags():
    # Every contract_id in LABELED_EXTRACTIONS must have matching contract text.
    assert set(LABELED_EXTRACTIONS) == set(CONTRACT_TEXTS)


def test_every_labeled_raw_text_excerpt_is_grounded_in_its_contract_text():
    for contract_id, labeled in LABELED_EXTRACTIONS.items():
        grounded = raw_text_is_grounded(labeled, CONTRACT_TEXTS[contract_id])
        ungrounded = [clause for clause, ok in grounded.items() if not ok]
        assert not ungrounded, f"{contract_id}: labeled raw_text not found in source for {ungrounded}"
