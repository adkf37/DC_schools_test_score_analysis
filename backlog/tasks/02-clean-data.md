# Task 02 — Clean and Standardize Data

## Summary
Verify that `src/load_clean_data.py` correctly normalizes column names, grade labels, subgroup values, and suppressed metrics across all four OSSE file schemas. Fix any normalization gaps found during Squad Review.

## Owner
Data Engineer

## Phase
Squad Review (Phase 2)

## Acceptance Criteria
- [ ] All column aliases in `src/config.py` cover headers present in all four source files (cross-check against `Field Differences 21-22 to 24-25.xlsx`).
- [ ] Grade normalization handles every observed format: `"Grade 6"`, `"Grade 6-All"`, `"HS-Algebra I"`, `"06"`, `"All"`.
- [ ] Subgroup labels are unified across years (e.g., `"White/Caucasian"` → `"White"`).
- [ ] Suppressed values (`DS`, `N<10`, `<5%`, `<=10%`, `N/A`) are stored as `NaN`, not 0.
- [ ] Deduplication retains the preferred row when multiple rows exist for the same school/year/grade/subject (specific assessment preferred over aggregate "All").
- [ ] `combined_all_years.csv` has a `Grade Number` column with numeric values for cohort tracking.

## Steps
1. Open `Field Differences 21-22 to 24-25.xlsx` and list every header that appears in at least one year but is not yet mapped in `src/config.py`.
2. Add any missing aliases to the `COLUMN_ALIASES` dict in `src/config.py`.
3. Run `python src/load_clean_data.py` and compare row counts before and after.
4. Spot-check a school known to have data in all four years (e.g., Stuart-Hobson) and confirm grade labels are consistent.
5. Verify suppressed values by checking that no numeric column contains the string `"DS"` or `"<5%"` in `combined_all_years.csv`.

## Dependencies
- Task 01 (ingest data) must be complete first.
- `src/config.py` — column aliases and subgroup mapping.
- `src/load_clean_data.py` — normalization logic.

## Notes
- The 2024–25 file introduced the `Enrolled Grade or Course` field which differs from earlier years' `Tested Grade` field. See `IMPROVEMENTS.md` for details.
- When in doubt, prefer the row that maximizes student count (N) to avoid subset bias.
