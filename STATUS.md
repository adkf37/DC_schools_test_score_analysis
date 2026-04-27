# Project Status — DC Schools Test Score Analysis

## Current Objective

**Build loop 4 complete — historical PARCC data (2015-16 through 2018-19) ingested, Task 03 summary-row target now met.**

Loop 4 extends the wide-format loader to ingest the four historical PARCC workbooks already committed to the repository (2015-16, 2016-17, 2017-18, 2018-19) in addition to the current three files (2021-22, 2022-23, 2023-24). This resolves the long-standing gap between the actual output (1,234 summary rows) and the Task 03 acceptance criterion (≥ 1,700 rows).

Loop 4 adds:
1. Extended `FILE_YEAR_MAP` in `src/load_wide_format_data.py` — now maps all 7 in-repo workbooks (years 2016–2024, skipping 2020–2021 COVID gap).
2. Extended `SHEET_SUBGROUP` — handles the older long-form sheet naming conventions used in the 2015-16 through 2018-19 files (e.g. "Black Students", "Eng Lang Learner Students", "Econ Disadvantaged Students").
3. Extended `COL_PATTERNS` — adds alternative MSAA column-name patterns for the 2015-16/2016-17 format.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete for loops 2-4 — equity gap, school map, rankings, and historical data ingestion |
| 4 | Validate | ✅ Complete for loops 1-3; loop 4 smoke tests pass (see Notes) |
| 5 | Closeout | ✅ Complete for loops 2-3; loop 4 pending Validate/Closeout |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves 7 figures, and the loop-3 `school_locations.csv` path now renders a real map (113 plotted schools in the current 2024 All Students view) |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ✅ 28,069 rows (7 years: 2016–2024) |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ✅ 12,956 rows |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ✅ **2,560 rows** (Task 03 target met) |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ✅ 6 sheets |
| Equity gap detail | `output_data/equity_gap_detail.csv` | ✅ 13,008 rows — expanded in loop 4 |
| Equity gap summary | `output_data/equity_gap_summary.csv` | ✅ 2,138 rows — expanded in loop 4 |
| School rankings | `output_data/school_rankings.csv` | ✅ 422 rows — expanded in loop 4 |
| School equity rankings | `output_data/school_equity_rankings.csv` | ✅ 414 rows — expanded in loop 4 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates — validated in the dashboard map path |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to 7 figures; map now functional with school_locations.csv |
| Validation report | `.squad/validation_report.md` | ✅ Loop 2 validation retained; loop 3 closeout smoke evidence is summarized in `.squad/review_report.md` |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 3 — closeout signoff + return-to-Build recommendation |

---

## Squad

| Member | Role | Charter |
|--------|------|---------|
| Lead | Project Lead & Architect | `.squad/agents/lead/charter.md` |
| Data Engineer | Data Ingestion & Pipeline | `.squad/agents/data-engineer/charter.md` |
| Statistician | Analysis & Statistical Tests | `.squad/agents/statistician/charter.md` |
| Tester | Quality Assurance & Validation | `.squad/agents/tester/charter.md` |
| Scribe | Documentation & History | `.squad/agents/scribe/charter.md` |
| Ralph | Risk, Assumptions & Review | `.squad/agents/ralph/charter.md` |

---

## Notes / Blockers / Follow-up

- **Smoke test commands (loop 4 — fresh-clone verified):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (returns 7 figures, including a real map when `input_data/school_locations.csv` is present)
- **Loop 4 build evidence:**
  - `src/load_wide_format_data.py` now loads all 7 in-repo workbooks: years 2016, 2017, 2018, 2019, 2022, 2023, 2024 (COVID years 2020-21 are absent from the OSSE release schedule).
  - `output_data/combined_all_years.csv`: 28,069 rows (was 12,378)
  - `output_data/cohort_growth_detail.csv`: 12,956 rows (was 5,391)
  - `output_data/cohort_growth_summary.csv`: **2,560 rows** — Task 03 ≥ 1,700 target now met (was 1,234)
  - `output_data/equity_gap_detail.csv`: 13,008 rows (was 5,977)
  - `output_data/school_rankings.csv`: 422 rows (was 192)
  - All 4 Stuart-Hobson benchmark transitions pass within ±0.1 pp (D-004).
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:**
  - The 2017-18 file is missing the MSAA columns entirely; PARCC ELA and Math are loaded normally.
  - The 2015-16/2016-17 files use an older MSAA column naming scheme ("MSAA ELA # of Test Takers"); the updated `COL_PATTERNS` handles both formats.
  - School name standardisation is not applied across years (e.g., "Aiton ES" in 2016 vs. "Aiton Elementary School" in later years). This limits school-level cohort tracking across the 2019–2022 gap but does not affect within-period transitions.
- **School location coordinates** are approximate, based on DC neighborhood geography. They are suitable for exploratory map visualization; for precise geocoding, use the DC Open Data API: https://opendata.dc.gov/
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Next recommended step:** Run Validate/Closeout for loop 4. After closeout, the remaining open items are: (a) 2024-25 data file, (b) normalized 4-workbook ingestion path, and (c) environment-blocked browser-console dashboard check.
