"""Runs the full live pipeline (real extraction LLM call, real rules
engine, real review LLM call) against the 5-contract labeled set and
reports the metrics PROJECT.md Section 14/17 call out as most important:
flag recall (did we catch the clauses that should have been flagged) above
extraction field accuracy above raw explanation-agreement, since a missed
risk is the failure that actually costs a legal team (Section 25).
"""

from __future__ import annotations

from dataclasses import dataclass

from contractreview.config import Config
from contractreview.data.contracts import CONTRACT_TEXTS, LABELED_EXTRACTIONS
from contractreview.eval.accuracy import compare_to_labeled, raw_text_is_grounded
from contractreview.llm import LLMClient
from contractreview.pipeline import run_review
from contractreview.playbook.definitions import DEFAULT_PLAYBOOK
from contractreview.playbook.rules import evaluate_playbook
from contractreview.report.render import ContractReviewRun, save_run


@dataclass
class ContractEvalResult:
    contract_id: str
    run: ContractReviewRun
    expected_flag_types: set[str]
    actual_flag_types: set[str]
    field_accuracy: float
    raw_text_grounded: bool

    @property
    def flag_recall(self) -> float:
        if not self.expected_flag_types:
            return 1.0
        return len(self.expected_flag_types & self.actual_flag_types) / len(self.expected_flag_types)

    @property
    def flag_set_exact_match(self) -> bool:
        return self.expected_flag_types == self.actual_flag_types

    @property
    def grounded(self) -> bool:
        return not self.run.grounding_violations


@dataclass
class EvalSummary:
    results: list[ContractEvalResult]

    @property
    def avg_flag_recall(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.flag_recall for r in self.results) / len(self.results)

    @property
    def grounding_pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.grounded) / len(self.results)

    @property
    def avg_field_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.field_accuracy for r in self.results) / len(self.results)

    @property
    def total_llm_calls(self) -> int:
        return sum(r.run.llm_call_count for r in self.results)


def run_eval(llm: LLMClient, config: Config, save_runs: bool = True) -> EvalSummary:
    results: list[ContractEvalResult] = []
    for contract_id, contract_text in CONTRACT_TEXTS.items():
        labeled = LABELED_EXTRACTIONS[contract_id]
        expected_flags = {f.clause_type.value for f in evaluate_playbook(labeled, DEFAULT_PLAYBOOK)}

        run = run_review(llm, config, contract_id, contract_text)
        actual_flags = {f.clause_type.value for f in run.flags}

        results.append(ContractEvalResult(
            contract_id=contract_id,
            run=run,
            expected_flag_types=expected_flags,
            actual_flag_types=actual_flags,
            field_accuracy=compare_to_labeled(run.extraction, labeled).accuracy,
            raw_text_grounded=all(raw_text_is_grounded(run.extraction, contract_text).values()),
        ))
        if save_runs:
            save_run(run, config.runs_dir)

    return EvalSummary(results=results)
