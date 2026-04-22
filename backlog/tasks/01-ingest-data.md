# Task 01 — Ingest Raw Data

## Summary
Download and place all four OSSE school-level assessment Excel files in `input_data/`, then run `src/load_clean_data.py` to produce `output_data/combined_all_years.csv`.

## Owner
Data Engineer

## Phase
Squad Init (Phase 1)

## Acceptance Criteria
- [ ] All four OSSE files present under `input_data/`:
  - `2021-22 School Level PARCC and MSAA Data.xlsx`
  - `2022-23 School Level PARCC and MSAA Data_9_5.xlsx`
  - `DC Cape Scores 2023-2024.xlsx`
  - `2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx`
- [ ] `python src/load_clean_data.py` exits with code 0
- [ ] `output_data/combined_all_years.csv` exists with ≥ 395,000 rows
- [ ] `output_data/processing_report.txt` shows all four files as ✓ loaded
- [ ] No unexpected file in `output_data/` that should not be committed

## Steps
1. Download each file from [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data).
2. Place files in `input_data/` (nested subfolders are accepted by the loader).
3. Run `python src/load_clean_data.py` and review console output.
4. Open `output_data/processing_report.txt` and confirm four ✓ entries.
5. Spot-check row count: `wc -l output_data/combined_all_years.csv` should exceed 395,000.

## Dependencies
- Python ≥ 3.9
- `pip install -r requirements.txt`

## Notes
- Files are intentionally excluded from git (see `.gitignore`). Each team member must download them independently.
- If a file fails to load, check the processing report for the specific error message before debugging.
