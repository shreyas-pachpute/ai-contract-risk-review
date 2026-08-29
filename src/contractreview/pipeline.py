"""Orchestrates a single contract review: extract -> compare (deterministic)
-> review flagged items -> validate grounding -> render.

Matches PROJECT.md Section 20's architecture: extraction and the review
agent are the only two LLM calls; policy comparison in between is pure
rules-engine logic with zero LLM cost.
"""

from __future__ import annotations

import uuid

from contractreview.agent.grounding import validate_grounding
from contractreview.agent.review import review_flags
from contractreview.config import Config
from contractreview.extraction.extract import extract_contract
from contractreview.llm import LLMClient
from contractreview.playbook.definitions import DEFAULT_PLAYBOOK, Playbook
from contractreview.playbook.rules import evaluate_playbook
from contractreview.report.render import ContractReviewRun


def run_review(
    llm: LLMClient,
    config: Config,
    contract_id: str,
    contract_text: str,
    playbook: Playbook = DEFAULT_PLAYBOOK,
) -> ContractReviewRun:
    extraction = extract_contract(llm, contract_id, contract_text)
    flags = evaluate_playbook(extraction, playbook)
    review = review_flags(llm, contract_id, flags)
    violations = validate_grounding(review, flags)

    return ContractReviewRun(
        run_id=uuid.uuid4().hex[:12],
        contract_id=contract_id,
        extraction=extraction,
        flags=flags,
        review=review,
        grounding_violations=violations,
        llm_call_count=llm.call_count,
        prompt_tokens=llm.prompt_tokens,
        output_tokens=llm.output_tokens,
    )
