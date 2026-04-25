# Sprint Plan

## Current Phase: Build (Phase 3)

Wide-format alternative loader implemented (Task 01/02 unblocked). Tasks 03 and 05 outputs are verified with Stuart-Hobson benchmarks passing. Re-run Validate next.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | ✅ Unblocked — `load_wide_format_data.py` reads files in repo |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | ✅ `combined_all_years.csv` generated |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Verified — 5,391 detail rows, benchmarks pass |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | 🔲 Pending |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Verified — p_value and significant columns present |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py`
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` has 1,234 rows (Task 03 target was ≥ 1,700); shortfall is due to 3 years of data only (no 2024-25) and OSSE demographic suppression.
- Next action: re-run Validate phase with updated smoke commands.

