# Sprint Plan

## Current Phase: All tasks complete → advance to Validate

All five backlog tasks are now implemented. The dashboard (`app/app_simple.py`) was fixed to use the current Dash and Plotly APIs. The next loop should run **Validate** to smoke-test the full pipeline and then **Closeout**.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | ✅ Unblocked — `load_wide_format_data.py` reads files in repo |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | ✅ `combined_all_years.csv` generated |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Verified — 5,391 detail rows, benchmarks pass |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | ✅ Fixed — app starts without errors, 5 figures render |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Verified — p_value and significant columns present |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py`
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` has 1,234 rows (Task 03 target was ≥ 1,700); shortfall is due to 3 years of data only (no 2024-25) and OSSE demographic suppression.
- Closeout outcome: sign off the current wide-format loop as handoff-ready documentation, but return the repo to Build because Task 04 is still pending and the normalized 4-workbook path is still unavailable in-repo.
- Next action: start the next Build loop for either Task 04 dashboard work or the missing normalized-data / 2024-25 ingestion path.
