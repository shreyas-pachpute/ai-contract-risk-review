"""Renders a contract review run to JSON (full audit trail, PROJECT.md
Section 18) and Markdown (the reviewer-facing flagged-item list).
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from contractreview.agent.schemas import RiskReviewOutput
from contractreview.extraction.schemas import ExtractedContract
from contractreview.playbook.rules import PolicyFlag


@dataclasses.dataclass
class ContractReviewRun:
    run_id: str
    contract_id: str
    extraction: ExtractedContract
    flags: list[PolicyFlag]
    review: RiskReviewOutput
    grounding_violations: list[str]
    llm_call_count: int
    prompt_tokens: int
    output_tokens: int


def trace_to_dict(trace: ContractReviewRun) -> dict:
    return {
        "run_id": trace.run_id,
        "contract_id": trace.contract_id,
        "extraction": trace.extraction.model_dump(mode="json"),
        "flags": [f.model_dump(mode="json") for f in trace.flags],
        "review": trace.review.model_dump(mode="json"),
        "grounding_violations": trace.grounding_violations,
        "llm_call_count": trace.llm_call_count,
        "prompt_tokens": trace.prompt_tokens,
        "output_tokens": trace.output_tokens,
    }


def render_markdown(trace: ContractReviewRun) -> str:
    lines = [
        f"# Contract Risk Review — {trace.contract_id}",
        "",
        f"**Run ID:** {trace.run_id}",
        f"**Clauses flagged:** {len(trace.flags)}",
        f"**Grounding:** {'PASSED' if not trace.grounding_violations else 'FAILED — ' + '; '.join(trace.grounding_violations)}",
        "",
        f"**Overall summary:** {trace.review.overall_summary}",
        "",
    ]
    if not trace.flags:
        lines.append("No playbook deviations detected. This contract matches standard terms.")
    for explanation in trace.review.flags:
        flag = next((f for f in trace.flags if f.clause_type.value == explanation.clause_type), None)
        lines.append(f"## {explanation.clause_type}")
        if flag:
            lines.append(
                f"- **Rule:** {flag.rule_description}\n"
                f"- **Actual:** {flag.actual_value}  |  **Required:** {flag.required_value}  |  **Severity:** {flag.severity.value}"
            )
        lines.append(f"- **Risk explanation:** {explanation.risk_explanation}")
        lines.append(f"- **Negotiation checklist item:** {explanation.negotiation_checklist_item}")
        lines.append(f"- **Materiality:** {explanation.materiality}")
        lines.append(f"- **Cited text:** \"{explanation.cites_raw_text}\"")
        lines.append("")

    lines += [
        "## Observability",
        f"- LLM calls: {trace.llm_call_count}",
        f"- Prompt tokens: {trace.prompt_tokens}, Output tokens: {trace.output_tokens}",
    ]
    return "\n".join(lines)


def save_run(trace: ContractReviewRun, runs_dir: Path) -> Path:
    run_dir = runs_dir / trace.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trace.json").write_text(json.dumps(trace_to_dict(trace), indent=2), encoding="utf-8")
    (run_dir / "report.md").write_text(render_markdown(trace), encoding="utf-8")
    return run_dir
