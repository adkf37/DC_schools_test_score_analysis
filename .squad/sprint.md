# Sprint Plan

## Current Phase: Build (Phase 3)

Statistical significance tests (Task 05) have been implemented. Task 03 (cohort growth engine) was already complete. Tasks 01/02 are blocked on manual OSSE data downloads.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | 🔲 Blocked (data not in repo) |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | 🔲 Blocked |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Implemented |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | 🔲 Pending |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Implemented |

## Notes

- Tasks 03 and 04 can proceed in parallel once Task 02 is complete.
- Task 05 is now merged into `src/analyze_cohort_growth.py` (extends Task 03 output).
- Next action: download OSSE files into `input_data/`, run `python src/load_clean_data.py`, then `python src/analyze_cohort_growth.py`, and validate against Task 03 acceptance criteria.
- Statistical note: `p_value` and `significant` columns appear in `cohort_growth_detail.csv`; `pct_significant_transitions` appears in `cohort_growth_summary.csv`. See `docs/methods.md` for methodology.

