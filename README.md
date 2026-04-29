# DC Schools Test Score Analysis

This repository is intended to analyze DC OSSE assessment files across the 2021–22 through 2024–25 school years, combine them into a single cleaned dataset, and then compute cohort-growth outputs for policy analysis.

## Current project state

**As of 2026-04-29, loop 8 Closeout is complete: the reproducible 7-workbook wide-format pipeline now includes geographic-equity outputs and a 7-sheet summary workbook, and the repo returns to Build for the remaining backlog scope.**

What was validated from a fresh clone:

- `python -m pip install -r requirements.txt` ✅
- `python -m pip install dash plotly` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_wide_format_data.py` ✅
- `python src/analyze_cohort_growth.py` ✅
- `python src/equity_gap_analysis.py` ✅
- `python src/generate_school_rankings.py` ✅
- `python src/proficiency_trend_analysis.py` ✅
- `python src/geographic_equity_analysis.py` ✅
- `python src/generate_summary_report.py` ✅
- `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component` ✅

### What this signoff covers

- The in-repo wide-format workbooks for 2015-16, 2016-17, 2017-18, 2018-19, 2021-22, 2022-23, and 2023-24
- Regeneration of:
  - `output_data/combined_all_years.csv` (28,069 rows)
  - `output_data/processing_report.txt`
  - `output_data/cohort_growth_detail.csv` (12,956 rows)
  - `output_data/cohort_growth_summary.csv` (2,560 rows)
  - `output_data/cohort_growth_pivot.xlsx` (6 sheets)
  - `output_data/equity_gap_detail.csv` (13,008 rows)
  - `output_data/equity_gap_summary.csv` (2,138 rows)
  - `output_data/proficiency_trends.csv` (25,629 rows)
  - `output_data/geographic_equity_by_school.csv` (210 rows)
  - `output_data/geographic_equity_by_quadrant.csv` (8 rows)
  - `output_data/summary_report.xlsx` (7-sheet Excel policy summary)
- Stuart-Hobson benchmark transitions staying within ±0.1 pp
- Task 05 significance fields (`p_value`, `significant`, `pct_significant_transitions`)
- Loop 2 equity-gap outputs and Task 04 dashboard startup plus live callback rendering of all ten figures
- Loop 3 policy-analysis outputs on the expanded historical dataset:
  - `output_data/school_rankings.csv` (422 rows)
  - `output_data/school_equity_rankings.csv` (414 rows)
- Loop 4 dashboard map path with `input_data/school_locations.csv` present:
  - file contains 115 school locations
  - live callback returns a real `School Performance Map`
  - current 2024 Math / All Students view plots 113 schools (the citywide `DC Public Schools` aggregate has no map point)
- Loop 8 geographic-equity outputs and handoff findings:
  - `geographic_equity_by_quadrant.csv` shows NW average ELA proficiency at 42.71% vs. 24.09% in NE and 20.15% in SE
  - the dashboard callback now returns a 10th figure: `Math – Average Proficiency & Cohort Growth by DC Quadrant`
  - `summary_report.xlsx` now includes a `Geographic Equity` sheet
- Cohort transitions for consecutive year pairs only: 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. There is no 2019→2022 transition because OSSE did not release comparable annual school-level assessment files for the COVID-disrupted 2020 and 2021 school years.

### Remaining gaps

- `src/load_clean_data.py` still targets the normalized 4-workbook OSSE path and depends on files that are not committed in this repo.
- The 2024-25 source workbook is still missing from the in-repo dataset, so the original full-data backlog target is not met.
- The original normalized-data success criteria in `backlog/README.md` are still open: four exact OSSE workbooks are not all present in-repo, `load_clean_data.py` is not reproducible here, and the repo therefore does not meet the full ≥395,000-row ingestion target.
- Direct browser-console inspection during manual interaction remains blocked in this environment.
- Historical school names vary across eras (for example shortened vs. full school names), so cross-era school comparisons should be interpreted carefully even though within-pair cohort transitions are valid.

## Expected pipeline

For the reproducible in-repo path, use:

```bash
python -m pip install -r requirements.txt
python src/load_wide_format_data.py
python src/analyze_cohort_growth.py
python src/equity_gap_analysis.py
python src/generate_school_rankings.py
python src/proficiency_trend_analysis.py
python src/geographic_equity_analysis.py
python src/generate_summary_report.py
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
python src/proficiency_trend_analysis.py
python src/geographic_equity_analysis.py
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
- `output_data/proficiency_trends.csv`
- `output_data/geographic_equity_by_school.csv`
- `output_data/geographic_equity_by_quadrant.csv`
- `output_data/summary_report.xlsx`

The current closeout review regenerated these files from a fresh clone via the wide-format loader path listed above.

## Supporting documentation

- `STATUS.md` — current phase, blockers, and next recommended step
- `.squad/validation_report.md` — prior validation evidence for the wide-format smoke path
- `.squad/review_report.md` — closeout decision and explicit return-to-work recommendation
- `docs/methods.md` — cohort-growth and statistical-significance methodology

## Next steps

**Loop 8 (closed out):** the geographic-equity outputs, the 10-figure dashboard path, and the 7-sheet summary workbook are validated and handoff-ready for the reproducible in-repo path.

**Future Build loops:**
1. Restore the full normalized-data / 2024-25 ingestion path (requires downloading OSSE workbooks).
2. Confirm browser-console cleanliness during manual interaction with the 10-figure dashboard.
3. Re-run Validate + Closeout after the next Build loop changes the evidence or scope.
