"""CLI entry point: flags, review, eval."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from contractreview.config import load_config
from contractreview.data.contracts import CONTRACT_TEXTS, LABELED_EXTRACTIONS
from contractreview.llm import DailyQuotaExhausted, OllamaUnavailable, build_llm_client
from contractreview.pipeline import run_review
from contractreview.playbook.definitions import DEFAULT_PLAYBOOK
from contractreview.playbook.rules import evaluate_playbook
from contractreview.report.render import save_run

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
console = Console()


@app.command()
def flags() -> None:
    """Deterministic playbook comparison over the hand-labeled contract set (zero LLM cost)."""
    table = Table(title=f"Playbook Flags ({DEFAULT_PLAYBOOK.contract_type}, v{DEFAULT_PLAYBOOK.version})")
    table.add_column("Contract")
    table.add_column("Flagged Clauses")
    table.add_column("Count", justify="right")
    for contract_id, labeled in LABELED_EXTRACTIONS.items():
        result = evaluate_playbook(labeled, DEFAULT_PLAYBOOK)
        clause_list = ", ".join(f.clause_type.value for f in result) or "[green]none[/]"
        table.add_row(contract_id, clause_list, str(len(result)))
    console.print(table)


@app.command()
def review(contract: str = typer.Option(..., help="Contract ID, e.g. 'globex_risky'.")) -> None:
    """Run the full review pipeline (extract -> compare -> explain) for one contract."""
    if contract not in CONTRACT_TEXTS:
        console.print(f"[bold red]Unknown contract '{contract}'.[/] Known: {list(CONTRACT_TEXTS)}")
        raise typer.Exit(code=1)

    config = load_config()
    console.print(f"[bold]Reviewing '{contract}' (LLM provider: {config.llm_provider})...[/]")
    client = build_llm_client(config)
    try:
        run = run_review(client, config, contract, CONTRACT_TEXTS[contract])
    except (DailyQuotaExhausted, OllamaUnavailable) as exc:
        console.print(f"[bold red]Stopped: {exc}[/]")
        raise typer.Exit(code=1)

    table = Table(title=f"Flagged Items — {contract}")
    table.add_column("Clause")
    table.add_column("Severity")
    table.add_column("Materiality")
    for explanation in run.review.flags:
        flag = next((f for f in run.flags if f.clause_type.value == explanation.clause_type), None)
        table.add_row(explanation.clause_type, flag.severity.value if flag else "?", explanation.materiality)
    console.print(table)

    if run.grounding_violations:
        console.print(f"\n[bold red]Grounding: FAILED[/] — {run.grounding_violations}")
    else:
        console.print("\n[bold green]Grounding: passed[/]")
    console.print(f"LLM calls: {run.llm_call_count}")

    run_dir = save_run(run, config.runs_dir)
    console.print(f"Saved to: {run_dir}")


@app.command(name="eval")
def eval_cmd() -> None:
    """Run the full pipeline against all 5 labeled contracts; report flag recall, extraction accuracy, and grounding."""
    from contractreview.eval.harness import run_eval

    config = load_config()
    console.print(f"[bold]Running eval over {len(CONTRACT_TEXTS)} labeled contracts (LLM provider: {config.llm_provider})...[/]\n")
    client = build_llm_client(config)
    try:
        summary = run_eval(client, config)
    except (DailyQuotaExhausted, OllamaUnavailable) as exc:
        console.print(f"[bold red]Stopped: {exc}[/]")
        raise typer.Exit(code=1)

    table = Table(title="Eval: Per-Contract Results")
    table.add_column("Contract")
    table.add_column("Expected Flags")
    table.add_column("Actual Flags")
    table.add_column("Recall", justify="right")
    table.add_column("Field Acc.", justify="right")
    table.add_column("Grounded")
    for r in summary.results:
        table.add_row(
            r.contract_id,
            str(sorted(r.expected_flag_types)) or "none",
            str(sorted(r.actual_flag_types)) or "none",
            f"{r.flag_recall:.0%}",
            f"{r.field_accuracy:.0%}",
            "[green]yes[/]" if r.grounded else "[red]no[/]",
        )
    console.print(table)

    console.print(f"\n[bold]Avg flag recall:[/] {summary.avg_flag_recall:.0%} (Section 14: most important quality metric)")
    console.print(f"[bold]Avg extraction field accuracy:[/] {summary.avg_field_accuracy:.0%}")
    console.print(f"[bold]Grounding pass rate:[/] {summary.grounding_pass_rate:.0%}")
    console.print(f"[bold]Total LLM calls:[/] {summary.total_llm_calls}")


if __name__ == "__main__":
    app()
