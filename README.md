# Release Second Opinion

**Live dashboard:** https://eshwarpotturi.github.io/release-second-opinion/

An AI agent reads vendor release-impact assessments (RIAs), rates every feature's GxP validation risk **blind** (it never sees the vendor's rating), then compares against the vendor's published rating and the vendor's own post-publication corrections.

**Data:** 12 public Veeva Vault RIAs, 19R1 to 22R3 (539 features, 53 explicit rating corrections with from/to). Later RIAs (23R1+) were not at the same download path and are not included.
**Models:** gpt-4.1 and gpt-5.1 via an OpenAI-compatible endpoint, zero-shot with Veeva's published rubric (nothing tuned, so there is no train/test leakage). Total cost: a few cents.

## Results

| Measure | gpt-4.1 | gpt-5.1 |
|---|---|---|
| Exact agreement with Veeva | 44% | 42% |
| Within one level | 80% | 76% |
| Cohen's kappa | 0.21 | 0.18 |
| Rates higher than Veeva / lower | 47% / 9% | 50% / 8% |
| Share of features sent to testing (Medium or High) | 78% | 83% (Veeva: 45%) |

The two models agree with each other on 80% of features. Both are far more cautious than Veeva.

## Non-obvious insights

1. **Veeva's High bar moved, not its products.** Veeva rated 12.3% of features High in 19R1 to 21R2 but only 5.0% in 21R3 to 22R3 (zero High in 22R1 and 22R3; Fisher p = 0.006). Both models' High rates barely moved over the same features (16.5% to 12.7%, 19.8% to 15.5%; p = 0.31 and 0.24). A customer who reuses last year's risk thresholds to read a 2022 RIA is comparing against a different ruler. Caveat: the models are a reference, not ground truth, and the sample is 181 later features.
2. **The first published RIA is a draft.** 53 ratings were corrected in change logs; 37 (70%) were downgrades, and 30 (57%) crossed the line that decides whether Veeva validation-tests the feature at all (18 switched off, 12 switched on). Planning validation scope from the first-issue RIA misses these.
3. **The AI cannot predict these corrections.** On the 24 corrected features I could match, the models were as close to the initial rating as to the final one (10 to 12 closer to final vs initial, per model). So this is a triage aid, not a replacement for tracking vendor revisions.
4. **A review queue with a hard edge:** 98 of the 160 features Veeva rates N/A ("no validation impact") are rated Medium or High by both models, 77 of them auto-on. Several are audit-trail or signature items, which Veeva's own rubric lists as High, e.g. "Expand Time Period for Login Audit Logs", "Additional Signature Token", "Jobs: Audit Logs for External URL Call Jobs". 17 of 36 features whose text mentions audit/signature/security/permission terms are rated Low or N/A. `data/review_queue.csv` lists 129 features (98 above plus 47 where both models say High and Veeva does not, with overlap removed) with each model's one-line reason. These are items to look at, not proven errors; Veeva may know context the text lacks.

## Why it matters for a regulated IT/quality team

Under CSA-style risk-based validation, scope follows the vendor's risk rating. This shows how stable that rating is, where it may be soft, and gives a ranked list to challenge, at near-zero cost per release. Similar products exist (USDM Cloud Assurance, Sware Res_Q); the angle here is auditing the vendor rating itself.

## Reproduce

`scripts/parse.py` (features), `scripts/drift.py` (corrections), `scripts/blind.py <model>` (needs an API token in the path set at top; not included), `scripts/analyze.py`, `scripts/insights.py`. The RIA PDFs are Veeva's and not redistributed: `https://rn.veevavault.help/en/assets/downloads/Vault-Release-Impact-Assessment-<release>.pdf`.

Limits: one vendor, 2019 to 2022 only, models unvalidated against expert reviewers, PDF table parsing matched 24 of 53 corrected features to rows by name.
