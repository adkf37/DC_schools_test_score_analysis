# DC Schools Test Score Analysis

This repository is intended to analyze DC OSSE assessment files across the 2021–22 through 2024–25 school years, combine them into a single cleaned dataset, and then compute cohort-growth outputs for policy analysis.

## Current project state

**As of 2026-04-25, closeout did _not_ approve final handoff. The repo returns to Build.**

What was validated from a fresh clone:

- `python -m pip install -r requirements.txt` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_clean_data.py` ❌
- `python src/analyze_cohort_growth.py` ❌ (blocked because the loader did not generate `output_data/combined_all_years.csv`)

### Active blocker

`src/load_clean_data.py` currently expects four exact workbook names in the top-level `input_data/` directory. The repository snapshot instead contains differently named workbooks under `input_data/School and Demographic Group Aggregation/`, and no exact match for the required 2024-25 workbook was present during validation. Until that input-file contract is fixed, the pipeline cannot be reproduced from a fresh clone.

## Expected pipeline

Once the input-data contract is fixed, the intended workflow is:

```bash
python -m pip install -r requirements.txt
python src/load_clean_data.py
python src/analyze_cohort_growth.py
```

Optional after the core pipeline succeeds:

```bash
python app/app_simple.py
```

## Required source files

Backlog Task 01 expects these four annual workbooks:

- `2021-22 School Level PARCC and MSAA Data.xlsx`
- `2022-23 School Level PARCC and MSAA Data_9_5.xlsx`
- `DC Cape Scores 2023-2024.xlsx` or a documented equivalent that the loader recognizes
- `2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx`

## Intended outputs

If the loader and cohort analysis run successfully, the project should produce:

- `output_data/combined_all_years.csv`
- `output_data/processing_report.txt`
- `output_data/cohort_growth_detail.csv`
- `output_data/cohort_growth_summary.csv`
- `output_data/cohort_growth_pivot.xlsx`

The current closeout review could not regenerate these files from a fresh clone because of the active input-data blocker above.

## Supporting documentation

- `STATUS.md` — current phase, blockers, and next recommended step
- `.squad/validation_report.md` — latest validation evidence
- `.squad/review_report.md` — closeout decision and explicit return-to-work recommendation
- `docs/methods.md` — cohort-growth and statistical-significance methodology

## Next steps before another closeout attempt

1. Align `src/load_clean_data.py` with the actual repo input layout or place/rename the OSSE files so the documented loader command succeeds.
2. Resolve the missing 2024-25 workbook requirement.
3. Regenerate `output_data/combined_all_years.csv`.
4. Re-run `python src/analyze_cohort_growth.py` and verify the Stuart-Hobson benchmark plus Task 05 significance outputs.
5. Re-run validation and only then request another closeout review.
