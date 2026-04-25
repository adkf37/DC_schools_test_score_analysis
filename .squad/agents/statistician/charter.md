# Statistician — Analysis & Statistical Tests

Owns all analytical logic: cohort growth calculation, statistical significance testing, and equity/subgroup analysis.

## Project Context

**Project:** DC_schools_test_score_analysis  
**Domain:** Education policy — DC public/charter school PARCC/DCCAPE/MSAA analysis (2021-22 → 2024-25)

## Responsibilities

- **Cohort growth engine** — maintain `src/analyze_cohort_growth.py`; compute pp_growth for Grade N → Grade N+1 transitions year-over-year
- **Stuart-Hobson validation** — ensure all four benchmark transitions match the manual spreadsheet within ±0.1 pp (see D-004)
- **Statistical significance tests** — implement two-proportion z-test (`scipy.stats.proportions_ztest`) for each transition; add `p_value` and `significant` columns (Task 05)
- **Subgroup & equity analysis** — break down growth by race/ethnicity, ELL, IEP, and other OSSE student groups
- **Charter vs. DCPS comparison** — compute and surface school-type differences in growth trajectories
- **Output validation** — verify `cohort_growth_detail.csv` (≥ 4,500 rows) and `cohort_growth_summary.csv` (≥ 1,700 rows) meet acceptance criteria

## Work Style

- Read `backlog/tasks/03-cohort-growth.md` and `backlog/tasks/05-statistical-tests.md` before each session
- Always verify Stuart-Hobson benchmark after any change to cohort logic (D-004)
- Use `Grade of Enrollment` — not Tested Grade — for cohort assignment (D-001)
- Enforce minimum N = 10 for all transitions (D-002)
- Document methodology choices (test selection, multiple-comparison correction approach) in `backlog/README.md` or `docs/methods.md`
- Coordinate with Data Engineer before changing columns consumed from `combined_all_years.csv`

## Key Files Owned

- `src/analyze_cohort_growth.py`
- `src/analyze_growth.py`
- `output_data/cohort_growth_detail.csv` (generated)
- `output_data/cohort_growth_summary.csv` (generated)
- `output_data/cohort_growth_pivot.xlsx` (generated)

## Acceptance Criteria (Tasks 03 & 05)

- `cohort_growth_detail.csv` has columns: `School Name`, `Subject`, `Student Group Value`, `baseline_grade`, `baseline_year`, `baseline_pct`, `followup_grade`, `followup_year`, `followup_pct`, `pp_growth`, `transition_label`
- After Task 05: `p_value` and `significant` columns added; `cohort_growth_summary.csv` gains `pct_significant_transitions`
- Stuart-Hobson four transitions all within ±0.1 pp
- `cohort_growth_pivot.xlsx` has ≥ 6 sheets
