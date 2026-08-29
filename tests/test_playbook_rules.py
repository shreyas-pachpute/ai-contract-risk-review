"""The primary test suite (PROJECT.md Section 17: "Policy rule-comparison
correctness: tested as rules-engine logic -- deterministic input/output
pairs, not LLM-judged"). Runs entirely against the hand-labeled contract
set, zero LLM cost.
"""

from contractreview.data.contracts import LABELED_EXTRACTIONS
from contractreview.playbook.definitions import DEFAULT_PLAYBOOK
from contractreview.playbook.rules import ClauseType, Severity, evaluate_playbook


def _flag_types(contract_id: str) -> set[ClauseType]:
    flags = evaluate_playbook(LABELED_EXTRACTIONS[contract_id], DEFAULT_PLAYBOOK)
    return {f.clause_type for f in flags}


def test_acme_standard_fully_compliant_no_flags():
    assert _flag_types("acme_standard") == set()


def test_globex_risky_flagged_on_every_clause():
    # Worst-case contract: a real violation on all six checked clauses.
    assert _flag_types("globex_risky") == {
        ClauseType.CONFIDENTIALITY_TERM, ClauseType.GOVERNING_LAW, ClauseType.AUTO_RENEWAL,
        ClauseType.LIABILITY_CAP, ClauseType.INDEMNIFICATION, ClauseType.ASSIGNMENT,
    }


def test_globex_confidentiality_flag_reports_perpetual():
    flags = evaluate_playbook(LABELED_EXTRACTIONS["globex_risky"], DEFAULT_PLAYBOOK)
    conf_flag = next(f for f in flags if f.clause_type == ClauseType.CONFIDENTIALITY_TERM)
    assert conf_flag.actual_value == "perpetual/indefinite"
    assert conf_flag.severity == Severity.HIGH


def test_initech_borderline_flags_only_law_and_assignment():
    # 2-year confidentiality, capped liability, standard indemnification, and
    # no auto-renewal are all compliant -- only governing law (Texas, not
    # approved) and assignment (no consent required) should be flagged.
    assert _flag_types("initech_borderline") == {ClauseType.GOVERNING_LAW, ClauseType.ASSIGNMENT}


def test_umbrella_corp_flags_only_confidentiality_and_renewal():
    # 4-year term exceeds the 3-year cap; 15-day renewal notice is below the
    # 30-day minimum. New York governing law, capped liability, standard
    # indemnification, and consent-gated assignment are all compliant.
    assert _flag_types("umbrella_corp") == {ClauseType.CONFIDENTIALITY_TERM, ClauseType.AUTO_RENEWAL}


def test_wonka_industries_compliant_despite_verbose_drafting():
    # Verbose/unusual drafting style should not itself trigger a flag --
    # a false-positive-avoidance check (PROJECT.md Section 14 "Flag
    # precision"). The exact 3-year boundary is compliant (<=, not <).
    assert _flag_types("wonka_industries") == set()


def test_confidentiality_boundary_exactly_at_max_years_is_compliant():
    from contractreview.extraction.schemas import ConfidentialityTermClause

    labeled = LABELED_EXTRACTIONS["wonka_industries"]
    assert labeled.confidentiality_term.years == DEFAULT_PLAYBOOK.max_confidentiality_years
    boundary = LABELED_EXTRACTIONS["wonka_industries"].model_copy(
        update={"confidentiality_term": ConfidentialityTermClause(
            raw_text="x", years=DEFAULT_PLAYBOOK.max_confidentiality_years, is_perpetual=False,
        )}
    )
    flags = evaluate_playbook(boundary, DEFAULT_PLAYBOOK)
    assert ClauseType.CONFIDENTIALITY_TERM not in {f.clause_type for f in flags}


def test_auto_renewal_notice_boundary_exactly_at_minimum_is_compliant():
    from contractreview.extraction.schemas import AutoRenewalClause

    contract = LABELED_EXTRACTIONS["acme_standard"].model_copy(
        update={"auto_renewal": AutoRenewalClause(
            raw_text="x", has_auto_renewal=True, notice_days=DEFAULT_PLAYBOOK.min_auto_renewal_notice_days,
        )}
    )
    flags = evaluate_playbook(contract, DEFAULT_PLAYBOOK)
    assert ClauseType.AUTO_RENEWAL not in {f.clause_type for f in flags}


def test_no_auto_renewal_clause_never_flagged_regardless_of_notice():
    from contractreview.extraction.schemas import AutoRenewalClause

    contract = LABELED_EXTRACTIONS["acme_standard"].model_copy(
        update={"auto_renewal": AutoRenewalClause(raw_text="x", has_auto_renewal=False, notice_days=None)}
    )
    flags = evaluate_playbook(contract, DEFAULT_PLAYBOOK)
    assert ClauseType.AUTO_RENEWAL not in {f.clause_type for f in flags}


def test_governing_law_matches_despite_state_of_prefix():
    # Live run caught this: extraction returned "State of Delaware" for a
    # contract whose governing law is Delaware (approved) -- a naive
    # exact-string check would wrongly flag a fully compliant contract.
    contract = LABELED_EXTRACTIONS["acme_standard"].model_copy(
        update={"governing_law": LABELED_EXTRACTIONS["acme_standard"].governing_law.model_copy(
            update={"jurisdiction": "State of Delaware"}
        )}
    )
    flags = evaluate_playbook(contract, DEFAULT_PLAYBOOK)
    assert ClauseType.GOVERNING_LAW not in {f.clause_type for f in flags}


def test_governing_law_prefix_normalization_is_case_insensitive():
    from contractreview.playbook.rules import _normalize_jurisdiction

    assert _normalize_jurisdiction("state of new york") == "new york"
    assert _normalize_jurisdiction("The Commonwealth of Massachusetts") == "Massachusetts"
    assert _normalize_jurisdiction("Delaware") == "Delaware"


def test_every_flag_carries_the_raw_text_it_was_derived_from():
    for contract_id, labeled in LABELED_EXTRACTIONS.items():
        for flag in evaluate_playbook(labeled, DEFAULT_PLAYBOOK):
            assert flag.raw_text, f"{contract_id}: {flag.clause_type} flag has empty raw_text"
