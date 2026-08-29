"""The deterministic policy rules engine (PROJECT.md Section 8 & 19): does
this extracted clause match, deviate from, or omit a required playbook
term? This is fixed rules-comparison logic, not agent judgment, once
clauses are in structured form -- zero LLM calls, fully unit-testable.
"""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel

from contractreview.extraction.schemas import ExtractedContract
from contractreview.playbook.definitions import Playbook

_JURISDICTION_PREFIX_RE = re.compile(r"^(the\s+)?(state|commonwealth)\s+of\s+", re.IGNORECASE)


def _normalize_jurisdiction(name: str) -> str:
    """Extraction wording varies ("Delaware" vs "State of Delaware") even
    when the jurisdiction is the same -- strip the common prefix so the
    playbook comparison isn't fooled by phrasing. Caught live: an
    extraction on a fully-compliant Delaware NDA returned "State of
    Delaware", which failed a naive exact-string membership check against
    the approved-jurisdictions set.
    """
    return _JURISDICTION_PREFIX_RE.sub("", name.strip()).strip()


class ClauseType(StrEnum):
    CONFIDENTIALITY_TERM = "confidentiality_term"
    GOVERNING_LAW = "governing_law"
    AUTO_RENEWAL = "auto_renewal"
    LIABILITY_CAP = "liability_cap"
    INDEMNIFICATION = "indemnification"
    ASSIGNMENT = "assignment"


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PolicyFlag(BaseModel):
    clause_type: ClauseType
    raw_text: str
    rule_description: str
    actual_value: str
    required_value: str
    severity: Severity


def evaluate_playbook(contract: ExtractedContract, playbook: Playbook) -> list[PolicyFlag]:
    flags: list[PolicyFlag] = []

    ct = contract.confidentiality_term
    if ct.is_perpetual or (ct.years is not None and ct.years > playbook.max_confidentiality_years):
        actual = "perpetual/indefinite" if ct.is_perpetual else f"{ct.years} years"
        flags.append(PolicyFlag(
            clause_type=ClauseType.CONFIDENTIALITY_TERM,
            raw_text=ct.raw_text,
            rule_description=f"Confidentiality term must not exceed {playbook.max_confidentiality_years} years.",
            actual_value=actual,
            required_value=f"<= {playbook.max_confidentiality_years} years",
            severity=Severity.HIGH,
        ))

    gl = contract.governing_law
    if _normalize_jurisdiction(gl.jurisdiction) not in playbook.approved_jurisdictions:
        flags.append(PolicyFlag(
            clause_type=ClauseType.GOVERNING_LAW,
            raw_text=gl.raw_text,
            rule_description="Governing law must be an approved jurisdiction.",
            actual_value=gl.jurisdiction,
            required_value=" or ".join(sorted(playbook.approved_jurisdictions)),
            severity=Severity.MEDIUM,
        ))

    ar = contract.auto_renewal
    if ar.has_auto_renewal and (ar.notice_days is None or ar.notice_days < playbook.min_auto_renewal_notice_days):
        actual = "no notice requirement stated" if ar.notice_days is None else f"{ar.notice_days} days"
        flags.append(PolicyFlag(
            clause_type=ClauseType.AUTO_RENEWAL,
            raw_text=ar.raw_text,
            rule_description=f"Auto-renewal requires at least {playbook.min_auto_renewal_notice_days} days' notice to prevent renewal.",
            actual_value=actual,
            required_value=f">= {playbook.min_auto_renewal_notice_days} days",
            severity=Severity.MEDIUM,
        ))

    liab = contract.liability
    if playbook.require_liability_cap and not liab.has_cap:
        flags.append(PolicyFlag(
            clause_type=ClauseType.LIABILITY_CAP,
            raw_text=liab.raw_text,
            rule_description="Liability must be capped at a stated amount or formula.",
            actual_value="uncapped",
            required_value="capped",
            severity=Severity.HIGH,
        ))

    indem = contract.indemnification
    if indem.scope != playbook.max_approved_indemnification_scope:
        flags.append(PolicyFlag(
            clause_type=ClauseType.INDEMNIFICATION,
            raw_text=indem.raw_text,
            rule_description="Indemnification scope must not exceed standard (direct-damages-only) scope.",
            actual_value=indem.scope,
            required_value=playbook.max_approved_indemnification_scope,
            severity=Severity.HIGH,
        ))

    assign = contract.assignment
    if playbook.require_assignment_consent and not assign.requires_consent:
        flags.append(PolicyFlag(
            clause_type=ClauseType.ASSIGNMENT,
            raw_text=assign.raw_text,
            rule_description="Assignment to a third party must require the other party's prior written consent.",
            actual_value="assignable without consent",
            required_value="requires consent",
            severity=Severity.MEDIUM,
        ))

    return flags
