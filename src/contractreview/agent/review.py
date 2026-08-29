"""Risk Review Agent: a single LLM call that explains an already-flagged
list of policy deviations (PROJECT.md Section 9). If there are zero flags,
no call is made at all -- there is nothing to explain.
"""

from __future__ import annotations

from contractreview.agent.prompts import SYSTEM_INSTRUCTION, build_review_prompt
from contractreview.agent.schemas import RiskReviewOutput
from contractreview.llm import LLMClient
from contractreview.playbook.rules import PolicyFlag


def review_flags(llm: LLMClient, contract_id: str, flags: list[PolicyFlag]) -> RiskReviewOutput:
    if not flags:
        return RiskReviewOutput(
            contract_id=contract_id,
            overall_summary="No playbook deviations detected. This contract matches standard terms.",
            flags=[],
        )
    prompt = build_review_prompt(contract_id, flags)
    result = llm.generate_structured(SYSTEM_INSTRUCTION, prompt, RiskReviewOutput)
    if result.contract_id != contract_id:
        result = result.model_copy(update={"contract_id": contract_id})
    return result
