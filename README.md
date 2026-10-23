# Release Second Opinion

**Live dashboard:** https://eshwarpotturi.github.io/release-second-opinion/

How often does Veeva change its own risk ratings after publishing them, and in which direction? This page reads Veeva's change logs for 23 Vault releases (2019 to 2026) and shows every rating change.

## Findings

- **Veeva rarely changes its mind.** In the 11 releases that publish old and new ratings, 91 of 2,547 features (3.6%) were revised after publishing.
- **When it does, it usually lowers the risk.** 86 of 121 revisions (71%) lowered the rating.
- **Few revisions change a testing decision.** 31 switched testing off and 17 switched it on (1.9% of features). Planning from the first list would over-test 31 and miss 17.
- **"Low" is the least settled rating.** 6.7% of features first rated Low were revised, against 3.6% for Medium, 2.6% for High and 0.8% for N/A. The commonest move is Low to N/A, which does not change testing.
- **The overall bar is steady.** Share rated High: 10.1% (2019 to 2021), 8.3% (2022), 10.2% (2023 to 2024), 11.3% (2025 to 2026).
- Direction differs by Veeva section. Every revision in LIMS (4) and Safety (3) lowered the rating. Among the larger sections, Regulatory has the highest share raised (5 of 14). Counts are small.

## Correction to an earlier version

An earlier version said Veeva's High share fell from 12.3% to 5.0%, and that the first rating is "a draft" because 53% of corrections crossed the testing line. Both came from an incomplete read of the 2019 to 2022 PDFs (539 features instead of 1,817) and from counting only the corrections with old and new ratings. The complete data does not support the falling bar, and the testing-line effect is much smaller.

## Data

- `data/features_all.csv`: 5,698 features from 23 public Veeva Vault release impact assessments, including the eConsent/eCOA/Sites and QualityOne/RegulatoryOne sheets.
- `data/drift.csv`: corrections with old and new ratings (19R1 to 21R2, 25R3 to 26R2).
- `data/story.json`: everything the page shows.
- Releases 21R3 to 25R2 list corrected features by name only (120 revisions, direction not published). They are not in the direction figures or the section bars.

Limits: one vendor; the testing line is Medium and High; some revisions could not be placed in a section (their feature is not in the final list); a feature revised twice is counted once, from first to last rating.

## Rebuild

`python3 scripts/parse_pdf2.py` (PDF features), `scripts/parse_extra.py <folder of xlsx>` (extra sheets), `scripts/study.py` (all analysis, writes `data/story.json`), `scripts/story_squares.py` (adds one record per feature for the grid), `scripts/build_story.py` (writes `index.html`). Release impact assessments are Veeva's and not redistributed. Earlier scripts that rated features with GPT remain in the repo but are not used.
