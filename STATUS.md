# Project Status — DC Schools Test Score Analysis

## Current Objective

**Backlog populated; ready for Squad Init.**

The Planner phase is complete. The backlog (`backlog/`) has been created with project background, data-source inventory, phase breakdown, and five discrete task files. The next step is Squad Init (Phase 1): confirm all four OSSE raw data files are present in `input_data/` and that the full pipeline (`load_clean_data.py` → `analyze_cohort_growth.py`) runs end-to-end without errors.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | 🔲 Next |
| 2 | Squad Review | 🔲 Pending |
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

## Notes / Blockers

- Raw OSSE data files are not tracked in git and must be downloaded manually from [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data). See `backlog/data_sources.md` for details.
- Optional `input_data/school_locations.csv` (school geocoordinates) is not yet available; the map view in the dashboard will be skipped until this file is created.
