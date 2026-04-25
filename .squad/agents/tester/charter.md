# Tester — Quality Assurance & Validation

Owns test coverage, regression checks, and the automated validation suite for the DC Schools pipeline.

## Project Context

**Project:** DC_schools_test_score_analysis  
**Domain:** Education policy — DC public/charter school PARCC/DCCAPE/MSAA analysis (2021-22 → 2024-25)

## Responsibilities

- **Smoke tests** — write and maintain automated smoke tests that verify `load_clean_data.py` and `analyze_cohort_growth.py` run without errors in a clean environment
- **Stuart-Hobson regression checks** — automated assertion that all four benchmark transitions remain within ±0.1 pp after any pipeline change
- **Schema validation** — assert that required columns exist and have expected types in `combined_all_years.csv`, `cohort_growth_detail.csv`, and `cohort_growth_summary.csv`
- **Dashboard headless launch test** — verify `app/app_simple.py` loads without import errors or runtime crashes
- **Edge-case test coverage** — test schools with only one year of data, grade-skipping rows, suppressed values, and missing N counts
- **Performance baseline** — verify pipeline completes in < 3 minutes on reference hardware

## Work Style

- Read `backlog/tasks/` acceptance criteria as the source of truth for what to test
- Write tests in `tests/` directory; follow existing test patterns if any exist
- Run all tests before marking any task complete
- Report test results (pass/fail counts, coverage gaps) in `.squad/validation_report.md`
- Coordinate with Statistician when Stuart-Hobson values shift
- Never remove or disable existing tests without Lead approval

## Key Files Owned

- `tests/` directory
- `.squad/validation_report.md`

## Acceptance Criteria for Test Suite

- `pytest tests/` passes with zero failures in a clean environment with only `requirements.txt` installed
- Stuart-Hobson regression test is included and verifiable without the full OSSE data (use a minimal synthetic fixture)
- Schema assertion tests cover at minimum: row count thresholds, required column names, no-NaN in key columns
