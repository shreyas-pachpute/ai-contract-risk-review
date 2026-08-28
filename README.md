# AI Contract & Commercial Risk Review System

## 1. One-Sentence Explanation

This is an AI system that gives a company's legal and commercial teams a fast first-pass review of a contract — what's unusual, what's risky, and what to check — before a qualified human makes any actual legal judgment.

## 2. The Business Problem

Companies of any real size review a constant stream of commercial documents: vendor contracts, customer agreements, NDAs, amendments, and renewals. Every one of these needs to be checked against company policy (approved clause language, required protections, prohibited terms) and compared for unusual or risky terms — an indemnification clause broader than standard, a liability cap missing, an auto-renewal with a short notice window, a jurisdiction clause that creates unexpected exposure. Legal and commercial teams do this today largely by reading contracts manually, often under time pressure from a deal that needs to close, which means review depth is inconsistent — a contract reviewed by a rushed junior associate on a Friday afternoon gets different scrutiny than the same contract reviewed by a senior counsel with time to spare.

Companies address this today with contract templates and playbooks (reducing but not eliminating variation, since counterparties routinely propose their own paper), contract-lifecycle-management (CLM) software that tracks metadata (dates, parties, status) but typically does little substantive clause-level risk analysis, and manual legal review that scales linearly with headcount and contract volume. The pain concentrates in mid-tier contracts that don't warrant a senior lawyer's full attention but are too consequential to skip review entirely — exactly where inconsistent review quality does the most damage, since the highest-value contracts already get careful scrutiny by default.

The cost is legal team hours spent on repetitive first-pass review (the same handful of risk categories, checked over and over across many contracts), inconsistent risk-flagging depending on reviewer bandwidth, and the risk that actually matters most: unfavorable terms that make it through review because nobody had time to catch them, only surfacing as a real problem later (an uncapped liability exposure, an unfavorable auto-renewal triggering unexpectedly). If nothing changes, contract volume typically grows with company size and deal velocity, while legal headcount usually does not grow proportionally.

**This is explicitly a decision-support system that accelerates first-pass review, not a system that provides autonomous legal advice or makes legal judgments.** Every flagged risk is a "check this" signal for a qualified human, not a legal conclusion.

## 3. Who Would Use This?

- **Legal Counsel / Contract Reviewer:** Wants a fast, consistent first-pass identification of unusual or risky clauses, so their time goes to actual legal judgment on flagged items, not re-reading routine, standard-language sections.
- **General Counsel / Legal Ops Lead:** Wants consistent review quality and depth across the team regardless of individual reviewer bandwidth, plus visibility into aggregate risk patterns across the contract portfolio.
- **Commercial/Sales/Procurement Team (contract requester):** Wants faster turnaround on routine contracts without waiting in a legal review queue behind higher-priority work.
- **Compliance function:** Wants an auditable record of what was reviewed, what was flagged, and how it was resolved, especially for contracts with regulatory relevance.

## 4. Current Process Without AI

```
Contract received (new deal, renewal, or amendment)
 → Assigned to a legal reviewer, queued behind other work
 → Reviewer reads the contract, often against a mental checklist or an informal playbook
 → Reviewer manually compares unusual clauses against company standard language
     (often relying on memory of past contracts rather than systematic comparison)
 → Reviewer flags concerns, may negotiate directly or send back to the business team
 → Review depth and turnaround time vary significantly based on reviewer bandwidth and contract complexity
 → Resolution and final terms recorded, often informally, in the CLM system or not at all
```

The mechanical part — reading a long document and comparing its clauses against a known playbook — consumes time that could go to the actual judgment calls (is this risk acceptable given the deal's context, how hard should we push back).

## 5. Proposed AI-Powered Process

```
Contract uploaded/received
 ↓
Document classification and clause extraction: identify contract type and extract
   structured clauses (liability, indemnification, termination, renewal, governing law, etc.)
 ↓
Deterministic policy comparison: check extracted clauses against the company's
   defined playbook rules (a rules engine, not the LLM's judgment)
 ↓
Agent investigation: for flagged deviations, explain why the clause is unusual/risky,
   compare against similar past contracts, assess materiality in plain language
 ↓
Agent produces a structured risk review: flagged clauses, explanation, comparison to standard,
   suggested negotiation checklist items
 ↓
Legal reviewer reviews the flagged items against the actual contract text (never just the AI summary),
   applies judgment, and makes the actual legal decision
 ↓
High-risk items route to senior legal/commercial leadership per existing escalation policy
 ↓
Outcome recorded; resolved contract and its review feed back into the historical comparison set
```

## 6. What the AI Actually Does

**Reasoning:** Explains *why* a flagged clause deviates from standard and what the practical risk implication is — this is interpretive synthesis a reviewer can quickly evaluate, not a legal conclusion.

**Retrieval:** Pulls the company's playbook/policy rules and comparable historical contract clauses relevant to a flagged item.

**Analysis (document intelligence):** Classifies contract type and extracts structured clause data from documents that vary widely in format and drafting style across counterparties.

**Decision support:** Prioritizes which flagged clauses most warrant reviewer attention based on materiality (informed by deterministic rules, not solely the agent's own judgment).

**Tool usage:** Queries the playbook/policy rules engine and the historical contract archive for comparison.

**Communication:** Produces a structured review document for the legal team — it does not communicate with a counterparty, and it does not communicate a legal position externally under any circumstance.

**Validation:** Every flag traces to a specific extracted clause and a specific policy rule or comparable precedent — no flag is presented without its supporting evidence.

**What the AI does NOT do:** It does not provide legal advice or make a legal determination about whether a clause is acceptable. It does not negotiate or communicate with a counterparty. It does not approve or reject a contract. It does not replace qualified legal review — every flagged item and, in fact, the full contract, remains subject to human legal judgment before any decision is made.

## 7. Where AI Is Used

AI is good at reading contract language that varies enormously in drafting style and structure across counterparties and correctly extracting the substance of a clause into a comparable structured form — a real document-intelligence problem. It's good at explaining, in plain language, why a specific clause deviates from the company's standard position and what that practically means, work that currently depends on a reviewer's memory of the playbook and past contracts. It's good at surfacing an unusual clause that a time-pressured reviewer might otherwise skim past, precisely because it doesn't get tired or rushed the way a human reviewer under deadline pressure does.

Deterministic software must handle the actual policy-comparison logic (does this clause match, deviate from, or omit a required playbook term) — this is a rules-engine problem, not a judgment call, once clauses are extracted into structured form. Legal conclusions, negotiation strategy, and final contract approval must remain with qualified human counsel — this is both a quality and a professional-responsibility boundary, not merely a risk-management preference.

## 8. Agent vs Workflow vs Normal Software

- **Normal software:** Contract storage/CLM integration, the playbook/policy rules engine, the legal-review-facing UI and escalation-routing workflow.
- **Deterministic workflow:** Comparing extracted clauses against playbook rules (does this liability cap meet the minimum required, is this governing-law clause on the approved list) is a fixed rules-comparison problem — once clauses are extracted into structured form, this should be ordinary rules-engine logic, not agent reasoning.
- **AI agent:** Explaining *why* a flagged deviation matters and how it compares to similar past contracts requires synthesis that genuinely benefits from investigation — checking historical precedent, assessing materiality in context — and the right depth of investigation varies by clause type and contract context. This is the agent's scoped role.
- **Multi-agent system:** Not justified for the MVP. A single Risk Review Agent handling flagged clauses per contract (parallelized across contracts for throughput, not decomposed by role) is sufficient. Clause extraction is better treated as a deterministic structured-extraction pipeline stage (similar reasoning to Project 03's document intelligence) than as agent behavior, since it doesn't involve open-ended investigation.

## 9. Agent Roles

**Risk Review Agent:** "Given a contract's extracted clauses and the flags produced by comparing them against company policy, explain why each flagged item is a deviation, assess its practical risk implication, and compare it against how similar clauses have been handled in past contracts." A single, narrowly-scoped role — this project deliberately mirrors Project 07's restraint: the task doesn't naturally decompose into independent roles, so it isn't forced into one.

## 10. Tools the AI Needs

In business terms: the contract document itself, the company's legal playbook/policy definitions, and an archive of past reviewed contracts and their resolutions for comparison.

Technically: a document-intake connector with multimodal/OCR extraction capability for scanned or image-based contracts, a structured clause-extraction pipeline validated against defined clause-type schemas, a policy rules engine (deterministic, likely a configuration-driven system legal ops maintains directly rather than something engineers hard-code), and a read-only connector to the historical contract archive for comparison.

## 11. MCP Opportunities

The contract archive and policy/playbook definitions are reasonable MCP **Resource** candidates — the relevant comparison set for a given contract type should be host-loaded deterministically. A "search historical contracts for comparable clause language" capability is a good MCP **Tool**, since the agent decides when deeper precedent comparison is warranted based on how unusual a flagged clause appears. The document-extraction pipeline built here is directly reusable by Project 04 (Procurement & Vendor Negotiation), which needs the same clause-extraction capability for a different purpose — another concrete cross-project MCP reuse case in this portfolio. What should **not** be exposed via MCP or any agent tool: any capability to communicate with a counterparty or to mark a contract as approved/executed — those remain entirely human actions within existing legal workflow tools, never agent-invokable.

## 12. Human-in-the-Loop

**Low-risk (automatic):** Document classification, clause extraction, deterministic policy-rule comparison, generating flagged-item explanations.

**Medium-risk (requires legal review, standard process):** The full risk-review output — every flagged item is reviewed by a qualified legal reviewer against the actual contract text before any conclusion is treated as final; the AI's explanation is a starting point for review, never a substitute for it.

**High-risk (must never happen automatically, and structurally excluded from this system's action space):** Approving a contract, communicating a legal position or any content to a counterparty, and executing/signing anything. This system produces no action a counterparty would ever see — its entire output surface is internal to the legal team, which is itself a strong safety property distinct from most other projects in this portfolio that at least draft (even if human-gated) external-facing content.

## 13. Business Value

The clearest measurable driver is legal reviewer time per contract for the first-pass review phase, measurable directly via before/after time tracking segmented by contract type/complexity. A second driver is review consistency — reducing the variance in review depth/quality that currently depends on individual reviewer bandwidth, measurable via sampling-based quality audits comparing AI-assisted and unassisted historical reviews. A third, harder-to-quantify-upfront driver is risk reduction from catching clauses that would otherwise have been missed under time pressure; this should be tracked via the false-negative-detection metric in Section 14 rather than an invented dollar figure, since the actual cost-avoidance value of catching a bad clause depends entirely on what would have happened if it hadn't been caught, which isn't knowable in advance.

## 14. Success Metrics

- **Time per contract review** (first-pass phase), segmented by contract type and complexity.
- **Clause extraction accuracy** against a labeled contract set.
- **Flag precision** — of flagged items, what fraction legal review confirms as genuinely worth attention (avoiding review fatigue from excessive false flags).
- **Flag recall / false-negative rate** — on a curated test set of contracts with known risky clauses, does the system catch them? This is the most important quality metric, mirroring the same principle as Project 03.
- **Reviewer override/disagreement rate**, tracked as a signal for calibrating the playbook rules and agent explanation quality, not purely an accuracy score.
- **Turnaround time** for routine contracts, from submission to legal team disposition.
- **Cost per contract reviewed.**

## 15. Failure Scenarios

- **Misclassified contract type:** leads to wrong clause-schema extraction — mitigated by confidence thresholds routing low-confidence classifications to manual triage.
- **Extraction error on unusual drafting language:** mitigated by flagging low-confidence extractions explicitly for manual verification rather than presenting an uncertain extraction as settled fact.
- **Missing a genuinely risky clause not covered by existing playbook rules:** the deterministic rules engine can only check what it's configured to check — mitigated by periodic playbook review informed by what the agent's investigation surfaces as recurring "unusual but not yet playbook-covered" patterns, and by treating this as an expected limitation communicated clearly to legal reviewers, not a hidden gap.
- **Hallucinated risk explanation:** the agent asserts a risk implication not actually supported by the clause text or precedent — mitigated by requiring every explanation to cite the specific clause language and, where used, the specific historical precedent it's drawing on.
- **Stale playbook rules:** comparing against outdated company policy — mitigated by playbook versioning and requiring the rules engine to reference the currently active version explicitly.
- **Ambiguous or heavily negotiated clause language:** the agent should surface the ambiguity for legal judgment rather than resolving it confidently in one direction.

## 16. Safety and Security

Contract content is confidential and commercially sensitive, often covered by NDA obligations to counterparties — data handling must meet the same confidentiality standard the legal team already operates under, including model-provider data-retention/training-use guarantees given the sensitivity of contract content. Access is scoped by matter/deal — a reviewer or agent instance working one contract should not have blanket access to unrelated confidential deals unless their role requires it. All extraction, flagging, and review activity is logged with contract ID, timestamp, and reviewer disposition, forming an audit trail relevant both for internal quality assurance and for regulatory contexts where contract review process may itself be subject to scrutiny. Because contract documents are external input (often drafted by a counterparty, sometimes an adversarial party in a negotiation), they are treated as untrusted for instruction-following purposes — a contract should not be able to contain content that manipulates the agent's behavior, consistent with the defense-in-depth posture in Research Notes Section 27.

## 17. Evaluation

- **Extraction accuracy** against a labeled contract set spanning contract types and drafting styles.
- **Policy rule-comparison correctness:** tested as rules-engine logic — deterministic input/output pairs, not LLM-judged.
- **Flag recall on a curated risky-clause test set** — the single most important evaluation metric per Section 14.
- **Explanation grounding:** does every risk explanation cite the actual clause language and, where applicable, the actual historical precedent used?
- **Human evaluation:** legal-reviewer rating of explanation usefulness and accuracy, sampled regularly, separate from raw flag-agreement rate.
- **Regression suite:** a fixed set of historical contracts re-run on every extraction or rules-engine change.

## 18. Observability

Track, per contract: every clause extracted and its confidence, every policy rule checked and its result, every flagged item's investigation trace and cited evidence, and the reviewer's final disposition of each flag. This is essential both operationally (a legal ops lead needs to see review-time and flag-volume trends across the portfolio) and for the audit trail this domain requires — if a contract's terms are later disputed or scrutinized, the firm needs to reconstruct what was checked and what was flagged at review time. Track extraction-confidence trends by counterparty/contract-format as an ongoing signal, since a new frequent counterparty with an unusual template format is exactly the scenario likely to need playbook or extraction-pipeline attention.

## 19. Technology Options

**LlamaIndex / document-intelligence extraction pipeline:** *Why:* the same document-variety extraction problem as Project 03, well-suited to purpose-built document-AI tooling (Research Notes Section 14). *Why not:* a narrower custom pipeline may suffice for a company with a small, well-templated contract set. *Alternative:* a dedicated document-AI/extraction API for the extraction stage specifically.

**PydanticAI:** *Why:* clause extraction is a typed-structured-output problem per clause schema, matching PydanticAI's core design center. *Why not:* less relevant to the investigation/explanation stage. *Alternative:* provider-native structured output if not otherwise standardized on Pydantic.

**A deterministic rules engine (business-configuration-driven, maintained by legal ops, not engineers alone):** *Why:* this is the correct home for policy-comparison logic — legal ops needs to be able to update playbook rules without needing an engineer to modify agent prompts, and the comparison itself is a rules-matching problem, not a reasoning one. *Why not an LLM for this step:* less auditable, less consistent, and legal ops loses direct configuration control if policy comparison lives inside a prompt instead of a rules engine. *Alternative:* n/a — this is a firm architectural recommendation, not a close call.

**MCP:** *Why:* the contract-extraction and archive-comparison connectors are directly reusable by Project 04's procurement negotiation work, a concrete cross-project case. *Why not:* unnecessary overhead for a genuinely single-consumer prototype. *Alternative:* direct integration if no near-term second consumer.

## 20. Proposed Architecture

```
Contract Intake (upload / CLM integration)
        |
  Document Classification & Clause Extraction Pipeline (structured output, per-clause schema)
        |
  Deterministic Policy Rules Engine  <----  Playbook/Policy Definitions (legal-ops maintained)
        |
  Risk Review Agent (per contract, parallelized across contracts for throughput)
        |
   Tool Layer (MCP): Historical Contract Archive, Policy Definitions
        |
  Structured Risk Review -> Legal Reviewer -> Judgment & Decision -> (existing legal workflow, unchanged)
        |
  Evaluation & Observability / Audit Trail Layer
```

## 21. MVP

The smallest version that proves value: for one contract type with a well-defined playbook (e.g., standard vendor NDAs or a single common commercial agreement type), a clause-extraction pipeline with deterministic policy comparison, producing a reviewer-facing flagged-item list with cited explanations — no expansion to other contract types, no historical-precedent comparison yet. This validates extraction accuracy and flag usefulness before investing in broader contract-type coverage or deeper precedent-based investigation.

## 22. Future Version

MVP → expand contract-type coverage with type-specific playbooks → add historical-precedent comparison to the Risk Review Agent's investigation → add legal-ops-facing playbook analytics (which clause deviations recur most, informing playbook updates) → add portfolio-level risk-pattern reporting for General Counsel → maintain the "no counterparty-facing action, no legal-conclusion capability" boundary as permanent, not something that relaxes as the system matures.

## 23. What Makes This Project Difficult?

Document and drafting-style variety is a genuine, ongoing extraction challenge, similar to Project 03 — every counterparty drafts differently, and a system tuned on one company's typical contracts may extract poorly from an unusual format until it's specifically evaluated against that variety. The rules engine has to stay current with an evolving playbook, and disconnecting policy-configuration from engineering (letting legal ops own the rules directly) is both the right design and a real implementation challenge to get genuinely usable for non-engineers. Evaluation requires real legal expertise to build a labeled risky-clause test set — this isn't a task generalist annotators can reliably do, which raises the cost and time of building a rigorous evaluation set. The professional-responsibility boundary (decision support only, never legal advice) has to be maintained rigorously in the product's actual behavior and framing, not just stated as a disclaimer, since a reviewer who starts treating AI flags as authoritative conclusions rather than starting points for judgment undermines the entire safety architecture of the system.

## 24. What I Would Demonstrate When Implementing It

Structured clause extraction from varied contract formats with confidence scoring; a deterministic, legal-ops-configurable policy rules engine cleanly separated from the AI investigation layer; a citation-grounded explanation agent evaluated on flag recall against a curated risky-clause test set; MCP integration for the shared document-extraction and archive connectors; matter-level data isolation and audit logging; and a system design where no counterparty-facing action or legal-conclusion capability exists anywhere in the agent's action space.

## 25. Portfolio Story

"Legal teams were doing the same first-pass clause comparison, over and over, under inconsistent time pressure, which meant review depth varied more by reviewer bandwidth than by actual contract risk. I separated the policy-comparison logic — is this clause within approved bounds — into a deterministic rules engine that legal ops can configure directly, and reserved the AI for the part that actually needs reasoning: explaining why a flagged deviation matters and how it compares to similar past contracts, with every explanation citing the specific clause language it's based on. The system has no counterparty-facing capability at all — its entire output surface stays inside the legal team — which is a stronger safety property than an approval gate on an action, because there's no external action to gate in the first place. I measured this by flag recall on a curated set of contracts with known risky clauses, because a missed risk, not review speed, is the failure that actually costs the company."

## 26. Questions a CTO Might Ask Me

1. Why is policy comparison a rules engine instead of letting the AI judge deviations directly?
2. How do you build a labeled risky-clause evaluation set that's actually legally rigorous?
3. What happens when a clause is genuinely ambiguous even to a human reviewer?
4. How do you keep the playbook rules current without creating an engineering bottleneck for legal ops?
5. What's your extraction accuracy on an unusual counterparty-drafted format you've never seen before?
6. How do you prevent reviewers from over-trusting flagged output and skipping their own judgment?
7. What data-confidentiality guarantees do you have with your model provider given NDA-covered contract content?
8. Why does this system have zero counterparty-facing capability — wouldn't drafting redlines be valuable too?
9. How do you handle a contract governed by a jurisdiction your playbook doesn't cover?
10. What's the audit trail if a flagged (or unflagged) clause is later disputed?
11. How would extraction and flagging accuracy differ across contract types with very different structures?
12. What's the false-negative cost here, concretely — what happens when a risky clause slips through?
13. Why build a shared document-extraction connector instead of one-off pipelines per project?
14. How do you evaluate explanation quality when legal reviewers themselves might disagree on materiality?
15. How would this system need to change to operate across multiple jurisdictions with different legal standards?

## 27. Research Sources

- [LlamaIndex — official site](https://www.llamaindex.ai/)
- [Pydantic AI — Output docs](https://pydantic.dev/docs/ai/core-concepts/output/)
- [OWASP Top 10 Agents & AI Vulnerabilities (2026 Cheat Sheet)](https://blog.alexewerlof.com/p/owasp-top-10-ai-llm-agents)
- [Human-in-the-Loop AI Agents — StackAI](https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation)
- See also [../RESEARCH_NOTES.md](../RESEARCH_NOTES.md) for full ecosystem sourcing.

**Note:** This document intentionally avoids citing jurisdiction-specific legal standards, since these vary and any real implementation must be reviewed by qualified legal counsel for the specific jurisdiction(s) and practice area(s) it will operate in.
