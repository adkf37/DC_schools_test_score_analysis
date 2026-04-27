# Sprint Plan

## Current Phase: Build loop 4 complete → Validate/Closeout next

Loop 4 extends the wide-format data loader to ingest the four historical PARCC workbooks (2015-16 through 2018-19) already committed to the repository. This resolves the Task 03 summary-row shortfall: `cohort_growth_summary.csv` now has 2,560 rows, exceeding the ≥ 1,700 acceptance criterion. All four Stuart-Hobson benchmark transitions remain within ±0.1 pp. The next step is a fresh-clone Validate run to confirm smoke tests pass with the expanded dataset.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | ✅ Unblocked — `load_wide_format_data.py` reads files in repo |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | ✅ `combined_all_years.csv` generated |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Verified — 5,391 detail rows, benchmarks pass |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | ✅ Validated — app starts without errors, 7-figure callback path renders |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Verified — p_value and significant columns present |
| 6 | [Loop 2] Equity gap analysis | Statistician | Task 03 | ✅ Verified — equity CSVs generated and dashboard extended with 2 equity charts |
| 7 | [Loop 3] School rankings | Statistician | Loop 2 equity outputs | ✅ Verified — `generate_school_rankings.py` regenerates 192 growth rankings and 187 equity rankings |
| 8 | [Loop 3] Locations-backed dashboard map | Data Engineer | Task 04 | ✅ Verified — `school_locations.csv` present and live callback returns a real map with 113 plotted schools |
| 9 | [Loop 4] Ingest historical PARCC files (2015-16 through 2018-19) | Statistician | Task 01 | ✅ Built — `load_wide_format_data.py` now loads all 7 in-repo workbooks; summary rows = 2,560 (target ≥ 1,700 met) |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `pip install dash plotly` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py` → `python src/equity_gap_analysis.py` → `python src/generate_school_rankings.py` → `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component`
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` now has 2,560 rows (Task 03 target was ≥ 1,700 — **target met** in loop 4).
- No cohort transitions cross the 2019–2022 COVID gap; only within-year-pair transitions (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) are produced.
- Next action: run Validate/Closeout for loop 4, then assess remaining scope (2024-25 data, normalized OSSE path, browser-console dashboard check).
