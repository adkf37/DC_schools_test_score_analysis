# Project Status — DC Schools Test Score Analysis

## Current Objective

**Build phase complete for Tasks 01–03 and 05 using the wide-format data pipeline.**

A new alternative data loader (`src/load_wide_format_data.py`) has been implemented and validated. It reads the wide-format OSSE demographic files already committed to `input_data/School and Demographic Group Aggregation/`, converts them to the standard `combined_all_years.csv` format, and allows `src/analyze_cohort_growth.py` to run successfully end-to-end. All four Stuart-Hobson benchmark transitions pass within ±0.1 pp.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ In Progress (wide-format pipeline operational) |
| 4 | Validate | 🔄 Ready to re-run |
| 5 | Closeout | 🔄 Pending re-run of validation |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Unblocked via `load_wide_format_data.py` (wide-format files in repo) |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` generated (12,378 rows, 3 years, 96 schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ All 4 Stuart-Hobson benchmarks pass; 5,391 detail rows, 1,234 summary rows |
| 04 | Interactive dashboard | Build | Data Engineer | 🔲 Pending |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ✅ 12,378 rows (3 years) |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ✅ 5,391 rows |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ✅ 1,234 rows |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ✅ 6 sheets |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ New — alternative to load_clean_data.py |
| Statistical methods note | `docs/methods.md` | ✅ Created |
| Validation report | `.squad/validation_report.md` | ✅ Created (prior run) |
| Review report | `.squad/review_report.md` | ✅ Created (prior run) |

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

## Notes / Blockers

- **Wide-format loader is now operational.** `python src/load_wide_format_data.py` followed by `python src/analyze_cohort_growth.py` completes successfully from a fresh clone.
- **Smoke test commands:** `pip install -r requirements.txt` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py`
- **Summary row count:** 1,234 rows vs Task 03 target of ≥ 1,700. The shortfall is because (a) we have only 3 years of data (no 2024-25 file), and (b) small demographic groups are suppressed by OSSE in many schools. This is an inherent data limitation.
- **normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo. These must be downloaded manually from OSSE. The wide-format alternative covers the available data.
- **Next recommended step:** Re-run Validate with the new smoke commands, then consider Task 04 (dashboard).
