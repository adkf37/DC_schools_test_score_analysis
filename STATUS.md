# Project Status — DC Schools Test Score Analysis

## Current Objective

**Build Phase (Task 05): Statistical significance tests added to cohort growth analysis.**

Task 05 (statistical significance tests) has been implemented in `src/analyze_cohort_growth.py`. The two-proportion z-test is now computed for every cohort transition and surfaced in both output CSVs. A methods note has been added at `docs/methods.md`. The next step is to run the full pipeline against real data (Tasks 01–02) and validate the outputs per Task 03 and Task 05 acceptance criteria.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | 🔄 In Progress |
| 4 | Validate | 🔲 Pending |
| 5 | Closeout | 🔲 Pending |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | 🔲 Blocked (data files not in repo) |
| 02 | Clean & standardize data | Squad Review | Data Engineer | 🔲 Blocked (depends on Task 01) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Implemented (`src/analyze_cohort_growth.py`) |
| 04 | Interactive dashboard | Build | Data Engineer | 🔲 Pending |
| 05 | Statistical significance tests | Build | Statistician | ✅ Implemented (Task 03 extended) |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ⏳ Generated on pipeline run |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ⏳ Generated on pipeline run |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ⏳ Generated on pipeline run |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ⏳ Generated on pipeline run |
| Processing report | `output_data/processing_report.txt` | ⏳ Generated on pipeline run |
| Statistical methods note | `docs/methods.md` | ✅ Created |

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

- Raw OSSE data files are not tracked in git and must be downloaded manually from [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data). See `backlog/data_sources.md` for details. Tasks 01 and 02 are blocked on this.
- Tasks 03 and 05 are fully implemented and will run once Tasks 01/02 data are available.
- Statistical note: with a single middle school's grade cohort (~145 students), a 7 pp growth change is not statistically significant at p < 0.05 (requires N ≈ 366 per group). City-wide aggregations with larger N will yield more significant transitions.
- Optional `input_data/school_locations.csv` (school geocoordinates) is not yet available; the map view in the dashboard will be skipped until this file is created.

