"""A labeled set of 5 synthetic mutual vendor NDAs (PROJECT.md Section 21
MVP scope: one contract type, well-defined playbook).

Each contract has: (a) realistic full contract text, used for live LLM
extraction, and (b) a hand-labeled `ExtractedContract` -- the ground-truth
extraction a correct pipeline should produce. The labeled set lets
`playbook/rules.py` be tested deterministically (zero LLM cost, Section 17
"Policy rule-comparison correctness: tested as rules-engine logic") and
gives an extraction-accuracy baseline (Section 14) independent of any live
model call.

Contracts span: a fully compliant NDA, a worst-case NDA with a violation on
every checked clause, two borderline NDAs with 1-2 real deviations each, and
a compliant-but-verbosely-drafted NDA (false-positive-avoidance check).
"""

from __future__ import annotations

from contractreview.extraction.schemas import (
    AssignmentClause,
    AutoRenewalClause,
    ConfidentialityTermClause,
    ExtractedContract,
    GoverningLawClause,
    IndemnificationClause,
    LiabilityClause,
)

ACME_STANDARD_TEXT = """\
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into between Acme Robotics, Inc. \
("Acme") and the counterparty vendor identified in the signature block ("Vendor").

1. CONFIDENTIALITY OBLIGATION. Each party agrees to hold the other's Confidential Information in \
confidence for a period of three (3) years from the date of disclosure, after which this \
obligation shall terminate.

2. GOVERNING LAW. This Agreement shall be governed by and construed in accordance with the laws \
of the State of Delaware, without regard to its conflict of laws principles.

3. TERM AND RENEWAL. This Agreement shall remain in effect for one (1) year and shall \
automatically renew for successive one-year terms unless either party provides written notice of \
non-renewal at least forty-five (45) days prior to the end of the then-current term.

4. LIMITATION OF LIABILITY. Neither party's aggregate liability arising under this Agreement \
shall exceed two hundred fifty thousand dollars ($250,000).

5. INDEMNIFICATION. Each party shall indemnify the other solely for direct damages arising from \
that party's breach of its confidentiality obligations under Section 1.

6. ASSIGNMENT. Neither party may assign this Agreement without the prior written consent of the \
other party, which consent shall not be unreasonably withheld.
"""

GLOBEX_RISKY_TEXT = """\
MUTUAL NON-DISCLOSURE AGREEMENT

This Agreement is made between Globex Materials Ltd. ("Globex") and the Vendor.

1. CONFIDENTIALITY. The parties' obligation to protect Confidential Information disclosed under \
this Agreement shall survive in perpetuity and shall not terminate.

2. GOVERNING LAW. Any dispute arising from this Agreement shall be governed by the laws of the \
Cayman Islands.

3. RENEWAL. This Agreement automatically renews for successive one-year terms. A party wishing \
to prevent renewal must notify the other party no later than ten (10) days before the renewal \
date.

4. LIABILITY. There shall be no limitation on either party's liability for any claim arising \
under or in connection with this Agreement.

5. INDEMNIFICATION. Each party shall indemnify, defend, and hold harmless the other party and its \
affiliates from any and all claims, losses, and damages of any kind, including indirect, \
consequential, and punitive damages, and claims brought by third parties of any nature, arising \
directly or indirectly from this Agreement.

6. ASSIGNMENT. Either party may freely assign this Agreement, in whole or in part, to any third \
party without the consent of the other party.
"""

INITECH_BORDERLINE_TEXT = """\
MUTUAL NON-DISCLOSURE AGREEMENT

Entered into between Initech Systems LLC ("Initech") and the Vendor.

1. CONFIDENTIALITY. Confidential Information disclosed under this Agreement shall be protected \
for a period of two (2) years from the date of disclosure.

2. GOVERNING LAW. This Agreement is governed by the laws of the State of Texas.

3. TERM. This Agreement is effective for one (1) year from the Effective Date and does not \
automatically renew; it terminates at the end of the term unless the parties execute a new \
agreement.

4. LIABILITY. Each party's total liability under this Agreement shall not exceed one hundred \
thousand dollars ($100,000).

5. INDEMNIFICATION. Each party shall indemnify the other solely for direct damages caused by that \
party's breach of Section 1.

6. ASSIGNMENT. This Agreement, and any rights or obligations hereunder, may be assigned by either \
party to any successor or affiliate without requiring the other party's consent.
"""

UMBRELLA_CORP_TEXT = """\
MUTUAL NON-DISCLOSURE AGREEMENT

By and between Umbrella Corporation ("Umbrella") and the Vendor.

1. CONFIDENTIALITY. The receiving party shall maintain the confidentiality of the disclosing \
party's Confidential Information for a period of four (4) years following disclosure.

2. GOVERNING LAW. This Agreement shall be governed by the laws of the State of New York.

3. RENEWAL. This Agreement automatically renews for successive one-year periods unless a party \
gives notice of non-renewal at least fifteen (15) days before the renewal date.

4. LIABILITY. Neither party's liability under this Agreement shall exceed one million dollars \
($1,000,000) in the aggregate.

5. INDEMNIFICATION. Each party shall indemnify the other solely for direct damages resulting from \
a breach of the confidentiality obligations in Section 1.

6. ASSIGNMENT. Neither party may assign or transfer this Agreement without the prior written \
consent of the other party.
"""

WONKA_INDUSTRIES_TEXT = """\
MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Mutual Non-Disclosure and Confidentiality Agreement (this "Agreement"), entered into by and \
between Wonka Industries, Inc., a manufacturer of confectionery products ("Wonka"), and the \
counterparty vendor set forth in the signature page hereto (the "Vendor" and, together with \
Wonka, the "Parties," and each individually a "Party"), sets forth the Parties' respective \
obligations as follows.

1. TREATMENT OF CONFIDENTIAL INFORMATION. Each Party, in its capacity as a receiving Party, \
covenants and agrees that it shall not disclose, and shall take all commercially reasonable \
measures to safeguard, the Confidential Information of the disclosing Party for a period \
commencing on the date of this Agreement and continuing until the third (3rd) anniversary \
thereof, at which point this obligation shall lapse in its entirety.

2. CHOICE OF LAW. The interpretation, construction, and enforcement of this Agreement, and any \
dispute of whatever nature arising in connection herewith, shall in all respects be governed by \
the substantive laws of the State of California, exclusive of its choice-of-law rules.

3. DURATION OF AGREEMENT. This Agreement shall be effective as of the date first written above \
and shall continue for a single term of eighteen (18) months, at the conclusion of which it shall \
terminate automatically and without further notice; the Parties do not intend, and this Agreement \
does not provide, for any automatic extension or renewal of its term.

4. AGGREGATE LIABILITY. In no event shall either Party's aggregate liability to the other arising \
out of or relating to this Agreement exceed an amount equal to the fees, if any, paid or payable \
by one Party to the other in the twelve (12) months immediately preceding the event giving rise \
to the claim.

5. MUTUAL INDEMNIFICATION. Each Party shall indemnify, and hold harmless, the other Party solely \
with respect to direct damages proximately caused by the indemnifying Party's material breach of \
its confidentiality obligations set forth in Section 1 above, and for no other cause.

6. RESTRICTIONS ON ASSIGNMENT. This Agreement may not be assigned, delegated, or otherwise \
transferred, in whole or in part, by either Party without having first obtained the other Party's \
express prior written consent, such consent not to be unreasonably withheld, conditioned, or \
delayed.
"""


LABELED_EXTRACTIONS: dict[str, ExtractedContract] = {
    "acme_standard": ExtractedContract(
        contract_id="acme_standard",
        contract_type_confidence=0.98,
        confidentiality_term=ConfidentialityTermClause(
            raw_text="hold the other's Confidential Information in confidence for a period of three (3) years from the date of disclosure",
            years=3, is_perpetual=False,
        ),
        governing_law=GoverningLawClause(
            raw_text="governed by and construed in accordance with the laws of the State of Delaware",
            jurisdiction="Delaware",
        ),
        auto_renewal=AutoRenewalClause(
            raw_text="automatically renew for successive one-year terms unless either party provides written notice of non-renewal at least forty-five (45) days prior",
            has_auto_renewal=True, notice_days=45,
        ),
        liability=LiabilityClause(
            raw_text="Neither party's aggregate liability arising under this Agreement shall exceed two hundred fifty thousand dollars ($250,000)",
            has_cap=True, cap_description="$250,000",
        ),
        indemnification=IndemnificationClause(
            raw_text="indemnify the other solely for direct damages arising from that party's breach of its confidentiality obligations",
            scope="standard",
        ),
        assignment=AssignmentClause(
            raw_text="Neither party may assign this Agreement without the prior written consent of the other party",
            requires_consent=True,
        ),
    ),
    "globex_risky": ExtractedContract(
        contract_id="globex_risky",
        contract_type_confidence=0.95,
        confidentiality_term=ConfidentialityTermClause(
            raw_text="obligation to protect Confidential Information disclosed under this Agreement shall survive in perpetuity and shall not terminate",
            years=None, is_perpetual=True,
        ),
        governing_law=GoverningLawClause(
            raw_text="governed by the laws of the Cayman Islands",
            jurisdiction="Cayman Islands",
        ),
        auto_renewal=AutoRenewalClause(
            raw_text="automatically renews for successive one-year terms. A party wishing to prevent renewal must notify the other party no later than ten (10) days before",
            has_auto_renewal=True, notice_days=10,
        ),
        liability=LiabilityClause(
            raw_text="no limitation on either party's liability for any claim arising under or in connection with this Agreement",
            has_cap=False, cap_description=None,
        ),
        indemnification=IndemnificationClause(
            raw_text="claims, losses, and damages of any kind, including indirect, consequential, and punitive damages, and claims brought by third parties of any nature",
            scope="broad",
        ),
        assignment=AssignmentClause(
            raw_text="Either party may freely assign this Agreement, in whole or in part, to any third party without the consent of the other party",
            requires_consent=False,
        ),
    ),
    "initech_borderline": ExtractedContract(
        contract_id="initech_borderline",
        contract_type_confidence=0.96,
        confidentiality_term=ConfidentialityTermClause(
            raw_text="protected for a period of two (2) years from the date of disclosure",
            years=2, is_perpetual=False,
        ),
        governing_law=GoverningLawClause(
            raw_text="governed by the laws of the State of Texas",
            jurisdiction="Texas",
        ),
        auto_renewal=AutoRenewalClause(
            raw_text="does not automatically renew; it terminates at the end of the term unless the parties execute a new agreement",
            has_auto_renewal=False, notice_days=None,
        ),
        liability=LiabilityClause(
            raw_text="total liability under this Agreement shall not exceed one hundred thousand dollars ($100,000)",
            has_cap=True, cap_description="$100,000",
        ),
        indemnification=IndemnificationClause(
            raw_text="indemnify the other solely for direct damages caused by that party's breach of Section 1",
            scope="standard",
        ),
        assignment=AssignmentClause(
            raw_text="may be assigned by either party to any successor or affiliate without requiring the other party's consent",
            requires_consent=False,
        ),
    ),
    "umbrella_corp": ExtractedContract(
        contract_id="umbrella_corp",
        contract_type_confidence=0.97,
        confidentiality_term=ConfidentialityTermClause(
            raw_text="maintain the confidentiality of the disclosing party's Confidential Information for a period of four (4) years following disclosure",
            years=4, is_perpetual=False,
        ),
        governing_law=GoverningLawClause(
            raw_text="governed by the laws of the State of New York",
            jurisdiction="New York",
        ),
        auto_renewal=AutoRenewalClause(
            raw_text="automatically renews for successive one-year periods unless a party gives notice of non-renewal at least fifteen (15) days before",
            has_auto_renewal=True, notice_days=15,
        ),
        liability=LiabilityClause(
            raw_text="Neither party's liability under this Agreement shall exceed one million dollars ($1,000,000) in the aggregate",
            has_cap=True, cap_description="$1,000,000",
        ),
        indemnification=IndemnificationClause(
            raw_text="indemnify the other solely for direct damages resulting from a breach of the confidentiality obligations",
            scope="standard",
        ),
        assignment=AssignmentClause(
            raw_text="Neither party may assign or transfer this Agreement without the prior written consent of the other party",
            requires_consent=True,
        ),
    ),
    "wonka_industries": ExtractedContract(
        contract_id="wonka_industries",
        contract_type_confidence=0.93,
        confidentiality_term=ConfidentialityTermClause(
            raw_text="continuing until the third (3rd) anniversary thereof, at which point this obligation shall lapse in its entirety",
            years=3, is_perpetual=False,
        ),
        governing_law=GoverningLawClause(
            raw_text="governed by the substantive laws of the State of California",
            jurisdiction="California",
        ),
        auto_renewal=AutoRenewalClause(
            raw_text="the Parties do not intend, and this Agreement does not provide, for any automatic extension or renewal of its term",
            has_auto_renewal=False, notice_days=None,
        ),
        liability=LiabilityClause(
            raw_text="exceed an amount equal to the fees, if any, paid or payable by one Party to the other in the twelve (12) months immediately preceding the event giving rise to the claim",
            has_cap=True, cap_description="fees paid in the twelve months preceding the claim",
        ),
        indemnification=IndemnificationClause(
            raw_text="solely with respect to direct damages proximately caused by the indemnifying Party's material breach of its confidentiality obligations set forth in Section 1 above",
            scope="standard",
        ),
        assignment=AssignmentClause(
            raw_text="may not be assigned, delegated, or otherwise transferred, in whole or in part, by either Party without having first obtained the other Party's express prior written consent",
            requires_consent=True,
        ),
    ),
}

CONTRACT_TEXTS: dict[str, str] = {
    "acme_standard": ACME_STANDARD_TEXT,
    "globex_risky": GLOBEX_RISKY_TEXT,
    "initech_borderline": INITECH_BORDERLINE_TEXT,
    "umbrella_corp": UMBRELLA_CORP_TEXT,
    "wonka_industries": WONKA_INDUSTRIES_TEXT,
}
