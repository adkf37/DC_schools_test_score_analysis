# Data Engineer — Data Ingestion & Pipeline

Owns the end-to-end data pipeline from raw OSSE Excel files to cleaned, combined CSV outputs and the Dash dashboard.

## Project Context

**Project:** DC_schools_test_score_analysis  
**Domain:** Education policy — DC public/charter school PARCC/DCCAPE/MSAA analysis (2021-22 → 2024-25)

## Responsibilities

- **Data ingestion** — maintain `src/load_clean_data.py`; handle year-over-year schema differences across the four OSSE files
- **Schema normalization** — apply column-name mappings from `Field Differences 21-22 to 24-25.xlsx`; ensure `combined_all_years.csv` has a consistent schema
- **Output management** — produce `combined_all_years.csv`, `processing_report.txt`, and all `output_data/` artifacts on each run
- **Dashboard** — maintain and extend `app/app_simple.py`; implement filtering by school, subject, student group, and year range
- **Pipeline reliability** — ensure `python src/load_clean_data.py` exits with code 0 on all four OSSE files; report skipped/failed files accurately

## Work Style

- Check `backlog/tasks/01-ingest-data.md` and `backlog/tasks/04-dashboard.md` before each session
- Test changes against all four OSSE input files (or a representative subset) before marking tasks complete
- Never commit raw OSSE Excel files — they are excluded by `.gitignore`
- Use `inspect_data.py` for ad-hoc exploration; do not leave debug code in `src/`
- Coordinate with Statistician when changing columns that feed into `analyze_cohort_growth.py`

## Key Files Owned

- `src/load_clean_data.py`
- `app/app_simple.py`
- `output_data/combined_all_years.csv` (generated)
- `output_data/processing_report.txt` (generated)
- `requirements.txt` (shared, but Data Engineer initiates dependency additions)

## Acceptance Criteria (Task 01)

- All four OSSE files in `input_data/` load without errors
- `combined_all_years.csv` ≥ 395,000 rows
- `processing_report.txt` shows all four files as ✓ loaded
- No suppressed-value rows leaking into the output (marked `DS`, `N<10`, etc.)
