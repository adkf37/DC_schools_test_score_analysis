# DC Schools Test Score Analysis

This repository is intended to analyze DC OSSE assessment files across the 2021–22 through 2024–25 school years, combine them into a single cleaned dataset, and then compute cohort-growth outputs for policy analysis.

## Current project state

**As of 2026-04-27, closeout is complete for the validated loop-3 wide-format path: cohort analysis, equity outputs, school rankings, and the school-locations dashboard map are all reproducible from a fresh clone. The repo now returns to Build for remaining scope.**

What was validated from a fresh clone:

- `python -m pip install -r requirements.txt` ✅
- `python -m pip install dash plotly` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_wide_format_data.py` ✅
- `python src/analyze_cohort_growth.py` ✅
- `python src/equity_gap_analysis.py` ✅
- `python src/generate_school_rankings.py` ✅
- `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component` ✅

### What this signoff covers

- The in-repo wide-format workbooks for 2021-22, 2022-23, and 2023-24
- Regeneration of:
  - `output_data/combined_all_years.csv` (12,378 rows)
  - `output_data/processing_report.txt`
  - `output_data/cohort_growth_detail.csv` (5,391 rows)
  - `output_data/cohort_growth_summary.csv` (1,234 rows)
  - `output_data/cohort_growth_pivot.xlsx` (6 sheets)
  - `output_data/equity_gap_detail.csv` (5,977 rows)
  - `output_data/equity_gap_summary.csv` (1,042 rows)
- Stuart-Hobson benchmark transitions staying within ±0.1 pp
- Task 05 significance fields (`p_value`, `significant`, `pct_significant_transitions`)
- Loop 2 equity-gap outputs and Task 04 dashboard startup plus live callback rendering of all seven figures
- Loop 3 policy-analysis outputs:
  - `output_data/school_rankings.csv` (192 rows)
  - `output_data/school_equity_rankings.csv` (187 rows)
- Loop 3 dashboard map path with `input_data/school_locations.csv` present:
  - file contains 115 school locations
  - live callback returns a real `School Performance Map`
  - current 2024 All Students view plots 113 schools (the citywide `DC Public Schools` aggregate has no map point)

### Remaining gaps

- `src/load_clean_data.py` still targets the normalized 4-workbook OSSE path and depends on files that are not committed in this repo.
- The 2024-25 source workbook is still missing from the in-repo dataset, so the original full-data backlog target is not met.
- `cohort_growth_summary.csv` reaches 1,234 rows, below the original Task 03 target of ≥ 1,700, because only 3 years of data are present and OSSE suppresses many small subgroup cells.
- Direct browser-console inspection during manual interaction remains blocked in this environment.

## Expected pipeline

For the reproducible in-repo path, use:

```bash
python -m pip install -r requirements.txt
python src/load_wide_format_data.py
python src/analyze_cohort_growth.py
python src/equity_gap_analysis.py
python src/generate_school_rankings.py
```

If you want to run the dashboard after the analytical outputs are regenerated:

```bash
python -m pip install dash plotly
python app/app_simple.py
```

If you have downloaded the full normalized OSSE files separately, the intended alternative workflow is:

```bash
python -m pip install -r requirements.txt
python src/load_clean_data.py
python src/analyze_cohort_growth.py
python src/equity_gap_analysis.py
python src/generate_school_rankings.py
```

## Required source files

Backlog Task 01 still expects these four annual workbooks for the normalized loader:

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
- `output_data/equity_gap_detail.csv`
- `output_data/equity_gap_summary.csv`
- `output_data/school_rankings.csv`
- `output_data/school_equity_rankings.csv`

The current closeout review regenerated these files from a fresh clone via the wide-format loader path listed above.

## Supporting documentation

- `STATUS.md` — current phase, blockers, and next recommended step
- `.squad/validation_report.md` — prior validation evidence for the wide-format smoke path
- `.squad/review_report.md` — closeout decision and explicit return-to-work recommendation
- `docs/methods.md` — cohort-growth and statistical-significance methodology

## Next steps for the next Build loop

1. Choose the next Build target:
   - restore the full normalized-data / 2024-25 ingestion path, or
   - extend dashboard validation to the remaining blocked browser-console / manual interaction checks.
2. If pursuing the normalized-data path, align `src/load_clean_data.py` with the actual input contract or add/document the required OSSE files.
3. If pursuing dashboard work, confirm there are no unhandled browser-console errors during manual interaction with the seven-figure dashboard and decide whether to tighten any map-data coverage gaps.
4. Re-run Validate and Closeout after the next Build loop changes the scope or evidence.
