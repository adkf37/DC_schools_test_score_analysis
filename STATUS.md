# Project Status — DC Schools Test Score Analysis

## Current Objective

**Validate Phase result: Task 03 / Task 05 validation failed and the repo must return to Build.**

Validation on 2026-04-25 installed the declared Python dependencies, passed a syntax sanity check, and then failed on the documented smoke commands. `src/load_clean_data.py` currently expects four exact workbook names in the top-level `input_data/` directory, but the repo snapshot contains differently named files under `input_data/School and Demographic Group Aggregation/` and no exact 2024-25 match. Because `combined_all_years.csv` was not generated, `src/analyze_cohort_growth.py` could not run and the Task 03 / Task 05 acceptance criteria remain unmet.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | 🔄 In Progress (return target) |
| 4 | Validate | ⚠️ Failed / Blocked |
| 5 | Closeout | 🔲 Pending |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ⚠️ Blocked (repo data layout/filenames do not match loader contract; no exact 2024-25 workbook match) |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ⚠️ Blocked (Task 01 / loader discovery issue prevents `combined_all_years.csv`) |
| 03 | Cohort growth analysis | Validate | ⚠️ Validation blocked (`combined_all_years.csv` not generated) |
| 04 | Interactive dashboard | Build | Data Engineer | 🔲 Pending |
| 05 | Statistical significance tests | Validate | ⚠️ Validation blocked (depends on Task 03 outputs) |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ❌ Not generated in validation run |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ❌ Not generated in validation run |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ❌ Not generated in validation run |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ❌ Not generated in validation run |
| Processing report | `output_data/processing_report.txt` | ❌ Not generated in validation run |
| Statistical methods note | `docs/methods.md` | ✅ Created |
| Validation report | `.squad/validation_report.md` | ✅ Created |

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

- Validation installed `requirements.txt` successfully and `python -m py_compile src/*.py app/*.py inspect_data.py` passed, so the current blocker is not a syntax error.
- `src/load_clean_data.py` hardcodes four exact filenames in top-level `input_data/`, but the repo snapshot stores available workbooks under `input_data/School and Demographic Group Aggregation/` with different names.
- No exact match for the expected 2024-25 workbook (`2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx`) was present during validation.
- Because `combined_all_years.csv` was not generated, the Stuart-Hobson regression benchmark and Task 05 significance-output checks remain blocked.
- **Next recommended step:** return to Build to align loader input discovery or repo data placement, generate the combined dataset, rerun `python src/load_clean_data.py`, then rerun `python src/analyze_cohort_growth.py` and the Stuart-Hobson validation.
