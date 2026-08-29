"""Structured clause-extraction schema for a single contract type: the
mutual vendor NDA (PROJECT.md Section 21 MVP scope -- one well-defined
contract type, not general-purpose extraction).

Every clause field carries `raw_text`, the verbatim excerpt the value was
read from. This is the grounding anchor for the whole pipeline: nothing
downstream may assert a value without a quote it traces back to, and the
Risk Review Agent (agent/review.py) is later required to cite these
excerpts, not paraphrase them.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConfidentialityTermClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt describing the confidentiality term/duration.")
    years: int | None = Field(description="Term length in years, if a finite term is stated. Null if perpetual/indefinite or not found.")
    is_perpetual: bool = Field(description="True if the confidentiality obligation has no end date (perpetual/indefinite).")


class GoverningLawClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt naming the governing law/jurisdiction.")
    jurisdiction: str = Field(description="The named governing-law jurisdiction, e.g. 'Delaware', 'New York'. 'unknown' if not found.")


class AutoRenewalClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt describing renewal terms.")
    has_auto_renewal: bool = Field(description="True if the contract automatically renews unless action is taken.")
    notice_days: int | None = Field(description="Days of advance notice required to prevent auto-renewal. Null if no notice requirement is stated.")


class LiabilityClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt describing liability limitation, if any.")
    has_cap: bool = Field(description="True if liability is capped at a stated amount or formula.")
    cap_description: str | None = Field(description="Plain description of the cap, e.g. '$500,000' or 'fees paid in prior 12 months'. Null if uncapped.")


class IndemnificationClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt describing indemnification obligations.")
    scope: Literal["standard", "broad"] = Field(
        description=(
            "'standard' if indemnification is limited to direct damages from a breach of "
            "confidentiality. 'broad' if it extends to indirect/consequential/punitive damages, "
            "third-party claims generally, or is otherwise uncapped in scope."
        )
    )


class AssignmentClause(BaseModel):
    raw_text: str = Field(description="Verbatim excerpt describing assignment rights.")
    requires_consent: bool = Field(description="True if assignment to a third party requires the other party's prior written consent.")


class ExtractedContract(BaseModel):
    contract_id: str
    contract_type_confidence: float = Field(ge=0.0, le=1.0, description="Confidence this document is a mutual vendor NDA.")
    confidentiality_term: ConfidentialityTermClause
    governing_law: GoverningLawClause
    auto_renewal: AutoRenewalClause
    liability: LiabilityClause
    indemnification: IndemnificationClause
    assignment: AssignmentClause
