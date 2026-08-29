"""Risk Review Agent output schema. PROJECT.md Section 9: the agent's only
job is to explain flagged deviations and assess practical risk -- it never
decides whether something is flagged (that's playbook/rules.py) and it
carries no field where it could assert a source that isn't a quote from the
contract itself.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FlagExplanation(BaseModel):
    clause_type: str = Field(description="Which flagged clause this explains, e.g. 'confidentiality_term'.")
    risk_explanation: str = Field(description="Plain-language explanation of why this deviation matters and its practical risk implication.")
    negotiation_checklist_item: str = Field(description="A concrete, actionable item for the reviewer's negotiation checklist.")
    cites_raw_text: str = Field(description="The exact clause excerpt (verbatim, copied from the input) this explanation is based on.")
    materiality: Literal["high", "medium", "low"] = Field(description="How materially this deviation matters in this specific contract's context.")


class RiskReviewOutput(BaseModel):
    contract_id: str
    overall_summary: str = Field(description="A 1-3 sentence summary of the contract's overall risk posture for the reviewer.")
    flags: list[FlagExplanation]
