# Release Second Opinion

**Live dashboard:** https://eshwarpotturi.github.io/release-second-opinion/

Veeva rates the validation risk of every feature in each Vault release, and later corrects some of those ratings. This page uses Veeva's own change logs to show how its ratings move after publishing.

## Finding

- Veeva corrected 129 ratings that publish an old and a new value (19R1 to 21R2 and 25R3 to 26R2).
- 93 (72%) lowered the rating; 36 raised it.
- 69 (53%) changed whether the feature gets tested: 46 switched testing off, 23 switched it on.
- The same pattern holds five years apart: 70% lowered in 2019 to 2021, 74% in 2025 to 2026.
- Takeaway: treat the first published rating as a cautious estimate.

Limits: releases 21R3 to 25R2 list corrected features without old and new ratings, so they are not counted. 62 of the 129 corrections could be placed in a Veeva section; 67 could not, because the feature is not in the final list.

## Data and rebuild

`data/features.csv` (4,016 features from 23 public Veeva Vault release impact assessments), `data/drift.csv` (corrections), `data/story.json` (corrections with section). Rebuild: `python3 scripts/story_data.py` then `python3 scripts/build_story.py`. Release impact assessments are Veeva's and not redistributed.

An earlier version compared Veeva with GPT ratings. It is removed because the comparison does not show that Veeva is wrong; the older scripts and `data/` files remain in the repo.
