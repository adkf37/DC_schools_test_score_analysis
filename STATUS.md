# Project Status — DC Schools Test Score Analysis

## Current Objective

**Closeout loop 5 complete — the current 7-workbook wide-format + heatmap path is handoff-ready, and the repo now returns to Build for remaining scope.**

Loop 5 closeout rechecked the backlog tasks, sprint Definition of Done, validation evidence, and handoff docs, then reran the documented smoke path from a fresh clone:
1. `python -m pip install -r requirements.txt`
2. `python -m pip install dash plotly`
3. `python -m py_compile src/*.py app/*.py inspect_data.py`
4. `python src/load_wide_format_data.py`
5. `python src/analyze_cohort_growth.py`
6. `python src/equity_gap_analysis.py`
7. `python src/generate_school_rankings.py`
8. `python src/proficiency_trend_analysis.py`
9. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (returns **8 figures**, including the Grade × Year heatmap).

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete for loops 2-5 — equity gap, school map, rankings, historical data ingestion, and proficiency heatmap |
| 4 | Validate | ✅ Complete for loops 1-5 |
| 5 | Closeout | ✅ Complete for loops 2-5 — loop 5 signs off the wide-format + heatmap path and returns the repo to Build |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves 8 figures (loop 5 adds heatmap), school-level and citywide grade × year views functional |
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
| Equity gap detail | `output_data/equity_gap_detail.csv` | ✅ 13,008 rows |
| Equity gap summary | `output_data/equity_gap_summary.csv` | ✅ 2,138 rows |
| School rankings | `output_data/school_rankings.csv` | ✅ 422 rows |
| School equity rankings | `output_data/school_equity_rankings.csv` | ✅ 414 rows |
| **Proficiency trends** | `output_data/proficiency_trends.csv` | ✅ **25,629 rows** — new in loop 5 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to 8 figures; 8th figure is Grade × Year heatmap |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 5 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 5 |

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

- **Smoke test commands (loop 5 — fresh-clone re-verified in Closeout):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. `python src/proficiency_trend_analysis.py`
  9. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies` (callback returns 8 figures, including the new Grade × Year heatmap)
- **Loop 5 closeout evidence:**
  - `src/proficiency_trend_analysis.py` exits 0; produces `output_data/proficiency_trends.csv` (**25,629 rows**).
  - Dashboard callback now returns **8 figures** (was 7); the 8th is the Grade × Year heatmap.
  - `GET /`, `/_dash-layout`, and `/_dash-dependencies` all return **200**; `POST /_dash-update-component` also returns **200**.
  - All 4 Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied).
  - `py_compile` passes for all `src/*.py`, `app/*.py`, and `inspect_data.py`.
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:** (same as loop 4 — see loop 4 notes in decisions.md D-020)
- **School location coordinates** are approximate; see loop 3 notes.
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Validation blocker still open:** direct browser-console inspection remains blocked in this environment.
- **Charter vs. DCPS comparison** remains unimplemented: the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools; all schools in the repo files are DCPS schools. A future loop could add a school-type lookup CSV if the 4-workbook normalized OSSE path (which carries full LEA metadata) is restored.
- **Next recommended step:** Return to **Build** and choose the next backlog slice: (a) restore the normalized 4-workbook / 2024-25 ingestion path, (b) finish the blocked browser-console dashboard review, or (c) implement the remaining scatter-plot visualization from `backlog/phases.md` Phase 3.
