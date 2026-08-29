"""The playbook: company policy for mutual vendor NDAs, as data.

PROJECT.md Section 19 is explicit that this must be "a configuration-driven
system legal ops maintains directly rather than something engineers hard-code
[into prompts]." This module is that configuration -- a plain dataclass with
named, versioned thresholds. A real deployment would load this from a
database or admin UI legal ops owns directly; the shape here (a single
frozen dataclass) is what that system would ultimately produce and hand to
the rules engine in playbook/rules.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Playbook:
    version: str = "2026.1"
    contract_type: str = "mutual_vendor_nda"

    max_confidentiality_years: int = 3
    approved_jurisdictions: frozenset[str] = field(
        default_factory=lambda: frozenset({"Delaware", "New York", "California"})
    )
    min_auto_renewal_notice_days: int = 30
    require_liability_cap: bool = True
    max_approved_indemnification_scope: str = "standard"  # "broad" is always a deviation
    require_assignment_consent: bool = True


DEFAULT_PLAYBOOK = Playbook()
