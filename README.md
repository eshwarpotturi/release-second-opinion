# Release Second Opinion

**Live dashboard:** https://eshwarpotturi.github.io/release-second-opinion/

An AI agent reads vendor release-impact assessments (RIAs) and rates every feature's GxP validation risk **blind** (it never sees the vendor's rating). We then compare with the vendor's published rating and with the vendor's own post-publication corrections.

**Data:** 23 public Veeva Vault RIAs, 19R1 (2019) to 26R2 (2026): 4,016 features, 129 rating corrections with from/to ratings. 19R1–22R3 are PDFs; 23R1–26R2 are Excel files (main Vault RIA sheet only; the separate eConsent/ePRO/Sites sheets are not included).
**Models:** gpt-4.1 and gpt-5.1, zero-shot with Veeva's published rubric (nothing tuned, so no train/test leakage). Cost: a few dollars at most.

## Results

| Measure | gpt-4.1 | gpt-5.1 |
|---|---|---|
| Exact agreement with Veeva | 41.9% | 39.0% |
| Cohen's kappa | 0.19 | 0.17 |
| Rates higher than Veeva / lower | 48% / 10% | 54% / 7% |
| Share sent to testing (Medium or High) | 75% | 82% (Veeva: 41.5%) |

The two models agree with each other on 77% of features. Both are far more cautious than Veeva.

## Non-obvious insights

1. **Veeva's High bar moves.** Veeva rated 12.3% of features High in 19R1–21R2, 5.0% in 21R3–22R3 (p = 0.006), then 9.6% in 23R1–26R2 (p = 0.036 against the middle period). The models' High shares change less and not significantly between periods. An earlier version of this analysis (22R3 and before only) read the dip as a lasting collapse; the newer releases show it partly recovered. Last year's thresholds do not carry over.
2. **The first published rating is a draft.** 129 ratings were corrected in change logs; 93 (72%) were downgrades, and 69 (53%) crossed the line that decides whether Veeva validation-tests the feature (46 switched testing off, 23 switched it on). The share of downgrades is similar in 2019–2021 (70%) and 2025–2026 (74%). Only releases 19R1–21R2 and 25R3–26R2 publish from/to ratings; others list names only and are not counted.
3. **The AI does not anticipate the corrections.** On the 80 corrected features matched by name, the AI rating sat closer to Veeva's original rating than to the corrected one about twice as often (gpt-4.1: 54 vs 23; gpt-5.1: 49 vs 27). Corrections mostly move away from the AI's view. It is a challenge list, not a replacement for tracking vendor revisions.
4. **A review list with a hard edge.** 176 features are rated High by both models and N/A or Low by Veeva (109 N/A, 127 auto-on); 41 have audit, signature, permission or security in the name, which Veeva's own rubric lists as High. Wider: 756 of the 1,298 features Veeva rates N/A are rated Medium or High by both models. `data/review_queue.csv` has all 965 rows with each model's reason. These are items to check, not proven errors.

## Why it matters

Under risk-based validation (CSA), testing scope follows the vendor's rating. This shows how stable that rating is and gives a ranked list to challenge, at low cost per release. Similar products exist (USDM Cloud Assurance, Sware Res_Q); the angle here is auditing the vendor rating itself.

## Reproduce

`scripts/parse.py` (PDF features), `scripts/parse_xlsx.py` (Excel features), `scripts/drift.py` and `scripts/drift_new.py` (corrections), `scripts/blind.py <model>` (needs env `FOUNDRY_TOKEN_FILE` pointing at an API token file), `scripts/final.py` (all numbers, writes `data/summary.json`), `scripts/build_dashboard.py` (writes `index.html`). RIAs are Veeva's and not redistributed: `https://rn.veevavault.help/en/assets/downloads/Vault-Release-Impact-Assessment-<release>.pdf` (up to 22R3) or `.xlsx` (23R1 onwards).

Limits: one vendor; models unvalidated against expert reviewers; corrections matched to feature rows by name for only 80 of 129; RIAs are published before release, so ratings may change after the last log entry.
