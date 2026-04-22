# Task 03 — Cohort Growth Analysis

## Summary
Run `src/analyze_cohort_growth.py` to compute cohort-based growth (Grade N → Grade N+1, Year Y → Year Y+1) for every school, subject, and student subgroup. Validate outputs against the Stuart-Hobson manual benchmark.

## Owner
Statistician

## Phase
Build (Phase 3)

## Acceptance Criteria
- [ ] `python src/analyze_cohort_growth.py` exits with code 0.
- [ ] `output_data/cohort_growth_detail.csv` exists with ≥ 4,500 rows and columns: `School Name`, `Subject`, `Student Group Value`, `baseline_grade`, `baseline_year`, `baseline_pct`, `followup_grade`, `followup_year`, `followup_pct`, `pp_growth`, `transition_label`.
- [ ] `output_data/cohort_growth_summary.csv` exists with ≥ 1,700 rows.
- [ ] `output_data/cohort_growth_pivot.xlsx` exists with ≥ 6 sheets.
- [ ] Stuart-Hobson validation: all four transitions match within ±0.1 pp:
  | Transition | Expected Baseline | Expected Followup | Expected Growth |
  |-----------|------------------|------------------|----------------|
  | ELA Gr6→Gr7 (2022→2023) | 33.5% | 40.5% | +7.0 pp |
  | ELA Gr7→Gr8 (2022→2023) | 36.3% | 46.6% | +10.3 pp |
  | Math Gr6→Gr7 (2022→2023) | 11.0% | 14.7% | +3.6 pp |
  | Math Gr7→Gr8 (2022→2023) | 13.7% | 19.6% | +5.9 pp |

## Steps
1. Ensure Task 01 and Task 02 are complete and `combined_all_years.csv` is up to date.
2. Run `python src/analyze_cohort_growth.py`.
3. Open `cohort_growth_detail.csv` and filter to `School Name == "Stuart-Hobson"`.
4. Compare the four transitions against the table above.
5. If any value is off by more than 0.1 pp, investigate the deduplication logic in `src/load_clean_data.py` (see `IMPROVEMENTS.md` Phase 2 section).

## Dependencies
- Task 01 and Task 02 must be complete.
- `src/analyze_cohort_growth.py` — cohort engine.
- `src/load_clean_data.py` — source data (Grade of Enrollment column).

## Notes
- The cohort engine uses **Grade of Enrollment** (not Tested Grade/Subject) for cohort assignment. This is critical for middle-school math where the same enrolled-grade cohort may take multiple test levels.
- Rows where `Tested Grade/Subject == "All"` are preferred to avoid subset bias (e.g., Algebra I only covering 43 of 145 enrolled students).
- `minimum N = 10` is enforced to avoid noisy small-sample results.
