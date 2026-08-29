"""Deterministic grounding validation (PROJECT.md Section 17: "does every
risk explanation cite the actual clause language"). Two checks, each
independent of model cooperation:

1. Every explanation's clause_type must correspond to a clause the
   deterministic rules engine actually flagged -- the agent cannot invent
   a new flag.
2. Every explanation's cited excerpt must be a real substring of that
   flagged clause's raw text -- the agent cannot fabricate a quote.
"""

from __future__ import annotations

import re

from contractreview.agent.schemas import RiskReviewOutput
from contractreview.playbook.rules import PolicyFlag


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def validate_grounding(review: RiskReviewOutput, flags: list[PolicyFlag]) -> list[str]:
    violations: list[str] = []
    flags_by_type = {f.clause_type.value: f for f in flags}

    for explanation in review.flags:
        flag = flags_by_type.get(explanation.clause_type)
        if flag is None:
            violations.append(
                f"Explanation cites clause_type '{explanation.clause_type}', which was never "
                "flagged by the policy rules engine for this contract."
            )
            continue

        cited = _normalize(explanation.cites_raw_text)
        source = _normalize(flag.raw_text)
        if not cited or cited not in source:
            violations.append(
                f"Explanation for '{explanation.clause_type}' cites text not found verbatim in "
                f"the flagged clause's raw text: {explanation.cites_raw_text!r}"
            )

    explained_types = {e.clause_type for e in review.flags}
    for flag in flags:
        if flag.clause_type.value not in explained_types:
            violations.append(
                f"Flagged clause '{flag.clause_type.value}' has no corresponding explanation in the review output."
            )

    return violations
