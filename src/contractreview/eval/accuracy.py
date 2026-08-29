"""Pure, zero-LLM-cost comparison functions: how close did a live
extraction come to the hand-labeled ground truth (PROJECT.md Section 14
"Clause extraction accuracy against a labeled contract set")? These take
already-produced `ExtractedContract` objects, so they're fully unit
testable without ever calling a model.
"""

from __future__ import annotations

from dataclasses import dataclass

from contractreview.extraction.schemas import ExtractedContract

# (field label, extractor function) -- the value-bearing fields, excluding
# free-text raw_text (compared separately, since wording legitimately
# varies even when the extracted meaning is correct).
_FIELDS: list[tuple[str, callable]] = [
    ("confidentiality_term.years", lambda c: c.confidentiality_term.years),
    ("confidentiality_term.is_perpetual", lambda c: c.confidentiality_term.is_perpetual),
    ("governing_law.jurisdiction", lambda c: c.governing_law.jurisdiction),
    ("auto_renewal.has_auto_renewal", lambda c: c.auto_renewal.has_auto_renewal),
    ("auto_renewal.notice_days", lambda c: c.auto_renewal.notice_days),
    ("liability.has_cap", lambda c: c.liability.has_cap),
    ("indemnification.scope", lambda c: c.indemnification.scope),
    ("assignment.requires_consent", lambda c: c.assignment.requires_consent),
]


@dataclass
class FieldAccuracyResult:
    contract_id: str
    field_matches: dict[str, bool]

    @property
    def accuracy(self) -> float:
        if not self.field_matches:
            return 0.0
        return sum(self.field_matches.values()) / len(self.field_matches)

    @property
    def mismatched_fields(self) -> list[str]:
        return [f for f, matched in self.field_matches.items() if not matched]


def compare_to_labeled(extracted: ExtractedContract, labeled: ExtractedContract) -> FieldAccuracyResult:
    matches = {name: getter(extracted) == getter(labeled) for name, getter in _FIELDS}
    return FieldAccuracyResult(contract_id=labeled.contract_id, field_matches=matches)


def raw_text_is_grounded(extracted: ExtractedContract, contract_text: str) -> dict[str, bool]:
    """Every raw_text excerpt should appear verbatim (whitespace-insensitive)
    in the source contract text -- catches an extraction fabricating a
    quote rather than reading it from the document.
    """
    normalized_source = " ".join(contract_text.split()).lower()
    clauses = {
        "confidentiality_term": extracted.confidentiality_term.raw_text,
        "governing_law": extracted.governing_law.raw_text,
        "auto_renewal": extracted.auto_renewal.raw_text,
        "liability": extracted.liability.raw_text,
        "indemnification": extracted.indemnification.raw_text,
        "assignment": extracted.assignment.raw_text,
    }
    return {
        name: " ".join(raw.split()).lower() in normalized_source
        for name, raw in clauses.items()
    }
