# Project Status — DC Schools Test Score Analysis

## Current Objective

**Build loop 5 complete — proficiency trend analysis script and Grade × Year heatmap dashboard visualization added.**

Loop 5 implements the "heatmap" deliverable explicitly listed in `backlog/phases.md` Phase 3 Build. It adds:
1. `src/proficiency_trend_analysis.py` — reads `combined_all_years.csv`, deduplicates by school/grade/year/subgroup, and produces `output_data/proficiency_trends.csv` (25,629 rows: school × year × subject × grade × subgroup proficiency).
2. Extended `app/app_simple.py` — callback now returns 8 figures; the 8th is a `go.Heatmap` with RdYlGn colour scale showing Grade × Year proficiency. When a school is selected, the heatmap shows that school's grade-by-year grid; when no school is selected, it shows the citywide average.

Key finding surfaced by the heatmap: citywide ELA proficiency dropped from 35.2% (2019) to 29.4% (2022) and recovered to 32.1% (2024); Math dropped from 30.9% to 21.2% and recovered to 24.9%.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete for loops 2-5 — equity gap, school map, rankings, historical data ingestion, and proficiency heatmap |
| 4 | Validate | ✅ Complete for loops 1-4 — loop 5 Validate pending |
| 5 | Closeout | ✅ Complete for loops 2-4 — loop 5 Closeout pending |

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
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 4 (loop 5 update pending) |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 4 (loop 5 update pending) |

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

- **Smoke test commands (loop 5 — fresh-clone verified):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. `python src/proficiency_trend_analysis.py`
  9. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies` (callback returns 8 figures, including the new Grade × Year heatmap)
- **Loop 5 build evidence:**
  - `src/proficiency_trend_analysis.py` exits 0; produces `output_data/proficiency_trends.csv` (25,629 rows).
  - Dashboard callback now returns 8 figures (was 7); 8th is a `go.Heatmap` with RdYlGn scale.
  - Citywide ELA proficiency: 22.7% (2016) → 35.2% (2019) → 29.4% (2022) → 32.1% (2024).
  - All 4 Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied).
  - `py_compile` passes for all src/*.py, app/*.py, inspect_data.py.
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:** (same as loop 4 — see loop 4 notes in decisions.md D-020)
- **School location coordinates** are approximate; see loop 3 notes.
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Validation blocker still open:** direct browser-console inspection remains blocked in this environment.
- **Charter vs. DCPS comparison** remains unimplemented: the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools; all schools in the repo files are DCPS schools. A future loop could add a school-type lookup CSV if the 4-workbook normalized OSSE path (which carries full LEA metadata) is restored.
- **Next recommended step:** Run **Validate/Closeout** for loop 5, then assess remaining scope: (a) scatter-plot visualization from backlog/phases.md Phase 3, or (b) restore the normalized 4-workbook / 2024-25 ingestion path.

