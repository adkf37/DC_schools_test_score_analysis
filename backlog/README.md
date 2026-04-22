# DC Schools Test Score Analysis — Project Background

## Background

This project analyzes standardized test performance (PARCC/DCCAPE/MSAA) across DC public and public-charter schools from the 2021–22 through 2024–25 school years. Raw school-level files released annually by the DC Office of the State Superintendent of Education (OSSE) are ingested, cleaned, and joined into a unified dataset that supports two distinct growth analyses: same-grade year-over-year comparisons (e.g., how did Grade 6 ELA scores change at each school?) and cohort-based growth (e.g., how did students who were in Grade 6 in 2022 perform when they reached Grade 7 in 2023?). The cohort approach replicates the manual Stuart-Hobson example spreadsheet and extends it citywide, enabling education policy researchers to identify which schools accelerate student learning relative to their peers.

## Goals

- **Automate ingestion** of annual OSSE school-level PARCC/DCCAPE/MSAA Excel files with consistent schema normalization across years.
- **Compute cohort growth** (Grade N → Grade N+1, Year Y → Year Y+1) and same-grade year-over-year growth for every school, subject, and student subgroup.
- **Validate against manual benchmarks** — all four Stuart-Hobson transitions must match the manually calculated values within 0.1 percentage points.
- **Expose results interactively** via a Dash dashboard supporting filtering by school, subject, student group, and year range.
- **Support policy analysis** by surfacing equity gaps (achievement growth by race/ethnicity and other subgroups) and ranking schools by cohort growth.

## Success Criteria

- All four OSSE annual files (2021-22, 2022-23, 2023-24, 2024-25) ingest without errors and produce a single `combined_all_years.csv` with ≥ 395,000 rows.
- Cohort growth pipeline produces `cohort_growth_detail.csv` and `cohort_growth_summary.csv` covering ≥ 190 schools with ≥ 4,500 transitions.
- Stuart-Hobson validation: all four reference transitions match within ±0.1 pp.
- Dashboard (`app/app_simple.py`) loads and renders charts without errors when both combined CSV and cohort CSVs are present.
- `output_data/processing_report.txt` is generated on every run and accurately reflects files loaded, skipped, and failed.
- All scripts pass a basic smoke test (`python src/load_clean_data.py && python src/analyze_cohort_growth.py`) in a clean environment with only the packages listed in `requirements.txt`.
