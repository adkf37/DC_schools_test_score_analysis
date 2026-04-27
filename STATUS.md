# Project Status — DC Schools Test Score Analysis

## Current Objective

**Closeout complete for loop 3 — school map and policy rankings deliverables are verified, and the repo now returns to Build for remaining scope.**

Loop 3 adds:
1. `input_data/school_locations.csv` — geocoordinates for 115 DC public schools, enabling the dashboard map feature (Task 04 acceptance criterion: map view loads without errors when `school_locations.csv` is present).
2. `src/generate_school_rankings.py` — ranks all schools by cohort growth (All Students) and by equity-gap narrowing for disadvantaged subgroups, fulfilling the backlog goal of "ranking schools by cohort growth."

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete for loops 2-3 — equity gap, school map, and rankings deliverables |
| 4 | Validate | ✅ Complete for loops 1-3 |
| 5 | Closeout | ✅ Complete for loops 2-3 |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path validated for the 3 in-repo source files; normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (12,378 rows, 3 years, 116 raw schools / 96 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Smoke-tested end to end; all 4 Stuart-Hobson benchmarks pass; 5,391 detail rows, 1,234 summary rows |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves 7 figures, and the loop-3 `school_locations.csv` path now renders a real map (113 plotted schools in the current 2024 All Students view) |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (5,977 rows) and equity_gap_summary.csv (1,042 rows) added; dashboard extended |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ✅ 12,378 rows (3 years) |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ✅ 5,391 rows |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ✅ 1,234 rows |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ✅ 6 sheets |
| Equity gap detail | `output_data/equity_gap_detail.csv` | ✅ 5,977 rows — new in loop 2 |
| Equity gap summary | `output_data/equity_gap_summary.csv` | ✅ 1,042 rows — new in loop 2 |
| School rankings | `output_data/school_rankings.csv` | ✅ 192 rows — loop 3 validated |
| School equity rankings | `output_data/school_equity_rankings.csv` | ✅ 187 rows — loop 3 validated |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ New — alternative to load_clean_data.py |
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

- **Validated smoke test commands (loop 3):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (returns 7 figures, including a real map when `input_data/school_locations.csv` is present)
- **Loop 3 closeout evidence:**
  - `python src/generate_school_rankings.py` regenerates `school_rankings.csv` (192 rows) and `school_equity_rankings.csv` (187 rows)
  - `input_data/school_locations.csv` contains 115 school locations; the live dashboard map renders 113 schools in the current 2024 All Students view
  - The two non-plotted cases are expected: `DC Public Schools` is a citywide aggregate with no physical location, and two location rows (`Aiton Elementary School`, `Woodrow Wilson High School`) do not appear in the current 2024 All Students map dataset
- **School location coordinates** are approximate, based on DC neighborhood geography. They are suitable for exploratory map visualization; for precise geocoding, use the DC Open Data API: https://opendata.dc.gov/
- **Summary row count:** 1,234 rows vs Task 03 target of ≥ 1,700. The shortfall is because (a) we have only 3 years of data (no 2024-25 file), and (b) small demographic groups are suppressed by OSSE in many schools. This remains an explicit limitation.
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Next recommended step:** Start the next Build loop: either restore the normalized 4-workbook / 2024-25 ingestion path or finish the environment-blocked browser-console review for the live dashboard.
