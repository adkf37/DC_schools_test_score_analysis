# Task 05 — Statistical Significance Tests

## Summary
Add statistical significance testing to the cohort growth analysis so that observed percentage-point changes can be assessed for reliability. This addresses the "Add statistical tests" item in the WORKFLOW.md Next Steps section.

## Owner
Statistician

## Phase
Build (Phase 3)

## Acceptance Criteria
- [ ] A significance test is applied to each cohort transition — at minimum a two-proportion z-test comparing baseline and follow-up proficiency rates (using student counts N as the denominator).
- [ ] `cohort_growth_detail.csv` gains two new columns: `p_value` and `significant` (bool, threshold p < 0.05).
- [ ] `cohort_growth_summary.csv` gains a `pct_significant_transitions` column per school/subject/subgroup.
- [ ] Results are documented in a brief methods note added to `backlog/README.md` or a new `docs/methods.md`.
- [ ] All existing acceptance criteria for Task 03 still pass after this change.

## Steps
1. Research appropriate test: two-proportion z-test (`scipy.stats.proportions_ztest`) or chi-squared test.
2. Add the test to `src/analyze_cohort_growth.py` in the section that computes `pp_growth`.
3. Pass both `N_baseline` and `N_followup` (student counts) as denominators.
4. Update CSV output columns.
5. Verify Stuart-Hobson transitions: ELA Gr6→Gr7 (+7.0 pp) should be significant; very small growth transitions may not be.
6. Add `scipy` to `requirements.txt` if not already present.

## Dependencies
- Task 03 must be complete.
- `scipy` Python package (for `proportions_ztest`).

## Notes
- The OSSE files contain both a percentage and a count column (N) per row. Both are needed for the z-test. Confirm that `N_count` is preserved in `combined_all_years.csv` before implementing.
- Be cautious about multiple-comparison correction (Bonferroni or FDR) if running tests across hundreds of transitions. Document the chosen approach.
