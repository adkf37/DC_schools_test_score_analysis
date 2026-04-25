# Project Status — DC Schools Test Score Analysis

## Current Objective

**Squad initialized; ready for Squad Review.**

The Squad Init phase is complete. The `.squad/` directory has been bootstrapped with the full team roster (Lead, Data Engineer, Statistician, Tester, Scribe, Ralph), routing rules, an initialized decision log, and individual charter files for each agent. The next step is Squad Review (Phase 2): tighten backlog tasks, surface risks, and turn the backlog into an ordered execution plan in `.squad/sprint.md`.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | 🔲 Next |
| 3 | Build | 🔲 Pending |
| 4 | Validate | 🔲 Pending |
| 5 | Closeout | 🔲 Pending |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | 🔲 Pending |
| 02 | Clean & standardize data | Squad Review | Data Engineer | 🔲 Pending |
| 03 | Cohort growth analysis | Build | Statistician | 🔲 Pending |
| 04 | Interactive dashboard | Build | Data Engineer | 🔲 Pending |
| 05 | Statistical significance tests | Build | Statistician | 🔲 Pending |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ⏳ Generated on pipeline run |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ⏳ Generated on pipeline run |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ⏳ Generated on pipeline run |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ⏳ Generated on pipeline run |
| Processing report | `output_data/processing_report.txt` | ⏳ Generated on pipeline run |

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

- Raw OSSE data files are not tracked in git and must be downloaded manually from [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data). See `backlog/data_sources.md` for details.
- Optional `input_data/school_locations.csv` (school geocoordinates) is not yet available; the map view in the dashboard will be skipped until this file is created.
