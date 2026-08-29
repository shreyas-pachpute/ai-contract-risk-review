from contractreview.agent.grounding import validate_grounding
from contractreview.agent.schemas import FlagExplanation, RiskReviewOutput
from contractreview.playbook.rules import ClauseType, PolicyFlag, Severity


def _flag(clause_type=ClauseType.LIABILITY_CAP, raw_text="There shall be no limitation on liability.") -> PolicyFlag:
    return PolicyFlag(
        clause_type=clause_type, raw_text=raw_text, rule_description="must be capped",
        actual_value="uncapped", required_value="capped", severity=Severity.HIGH,
    )


def _explanation(clause_type=ClauseType.LIABILITY_CAP.value, cites="no limitation on liability") -> FlagExplanation:
    return FlagExplanation(
        clause_type=clause_type, risk_explanation="r", negotiation_checklist_item="n",
        cites_raw_text=cites, materiality="high",
    )


def test_grounded_explanation_passes():
    review = RiskReviewOutput(contract_id="c1", overall_summary="s", flags=[_explanation()])
    assert validate_grounding(review, [_flag()]) == []


def test_citation_not_present_in_source_flagged():
    review = RiskReviewOutput(contract_id="c1", overall_summary="s", flags=[
        _explanation(cites="a completely fabricated quote that never appeared")
    ])
    violations = validate_grounding(review, [_flag()])
    assert len(violations) == 1
    assert "not found verbatim" in violations[0]


def test_explanation_for_never_flagged_clause_type_rejected():
    review = RiskReviewOutput(contract_id="c1", overall_summary="s", flags=[
        _explanation(clause_type=ClauseType.GOVERNING_LAW.value, cites="Cayman Islands")
    ])
    violations = validate_grounding(review, [_flag()])  # only LIABILITY_CAP was actually flagged
    assert any("never flagged" in v for v in violations)


def test_missing_explanation_for_a_flagged_clause_is_reported():
    review = RiskReviewOutput(contract_id="c1", overall_summary="s", flags=[])
    violations = validate_grounding(review, [_flag()])
    assert any("no corresponding explanation" in v for v in violations)


def test_citation_matching_is_whitespace_insensitive():
    flag = _flag(raw_text="There   shall be\nno limitation  on liability.")
    review = RiskReviewOutput(contract_id="c1", overall_summary="s", flags=[
        _explanation(cites="There shall be no limitation on liability.")
    ])
    assert validate_grounding(review, [flag]) == []
