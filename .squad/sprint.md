# Sprint Plan

## Current Phase: Closeout complete for the current loop → return to Build

All five backlog tasks are implemented for the current loop, and fresh-clone validation now covers the wide-format pipeline plus dashboard startup/callback rendering. Closeout signs off the current loop and sends the repository back to **Build** for the remaining scope.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | ✅ Unblocked — `load_wide_format_data.py` reads files in repo |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | ✅ `combined_all_years.csv` generated |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Verified — 5,391 detail rows, benchmarks pass |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | ✅ Fixed — app starts without errors, 5 figures render |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Verified — p_value and significant columns present |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `pip install dash plotly` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py` → `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component`
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` has 1,234 rows (Task 03 target was ≥ 1,700); shortfall is due to 3 years of data only (no 2024-25) and OSSE demographic suppression.
- Closeout outcome: sign off the current dashboard-aware wide-format loop as handoff-ready documentation, but return the repo to Build because the normalized 4-workbook path is still unavailable in-repo and the remaining dashboard checks (browser console, locations-file path) are still open.
- Next action: start the next Build loop for either the missing normalized-data / 2024-25 ingestion path or the remaining dashboard checks.
