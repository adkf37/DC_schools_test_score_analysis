# Project Status — DC Schools Test Score Analysis

## Current Objective

**Loop 9 Validate complete — same-grade year-over-year growth path passes; ready for Closeout.**

Loop 9 validation re-ran the documented fresh-clone smoke path and confirmed the same-grade year-over-year (YoY) growth deliverable is reproducible end to end. The repo still fulfills the backlog README goal of computing same-grade YoY growth for every school, subject, and student subgroup. Key findings remain: citywide ELA YoY growth averaged +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024); Math shows a similar pattern with a 2017→2018 dip (avg −4.32 pp) and recovery in 2022→2023 (+3.25 pp). The dashboard now renders **11 figures**; `summary_report.xlsx` now has **8 sheets** (adds "YoY Growth" sheet); direct browser-console inspection remains blocked in this environment.

Loop 9 Build completed:
1. Created `src/yoy_growth_analysis.py` — standalone script reading `combined_all_years.csv`, computing consecutive-year same-grade transitions (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024; COVID gap excluded), minimum N=10 filter.
2. Outputs: `yoy_growth_detail.csv` (14,391 rows: school × grade × subject × subgroup × transition) and `yoy_growth_summary.csv` (2,604 rows: school × subject × subgroup).
3. Extended `app/app_simple.py` — loads `yoy_growth_detail.csv`; callback now returns **11 figures** (11th is a YoY growth line chart by grade level or school).
4. Extended `src/generate_summary_report.py` — adds Sheet 8 "YoY Growth" to `summary_report.xlsx` when `yoy_growth_summary.csv` is present (graceful skip if absent).
5. All four Stuart-Hobson 2022→2023 benchmarks remain within ±0.1 pp.
6. Fresh-clone smoke path validated through `generate_summary_report.py` — all scripts exit 0.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete through loop 9 — equity gap, school map, rankings, historical data ingestion, proficiency heatmap, scatter plot, summary report, geographic equity, same-grade YoY growth |
| 4 | Validate | ✅ Complete for loops 1-9 |
| 5 | Closeout | ✅ Complete for loops 2-8; Loop 9 — Closeout next |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves **11 figures** (loop 9 adds YoY growth chart), school-level and citywide views functional |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |
| 07 | Formatted Excel summary report | Closeout | Statistician | ✅ Closed out — `generate_summary_report.py` exits 0; `summary_report.xlsx` regenerated with **8 sheets** (adds YoY Growth in loop 9) |

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
| **Geographic equity (school)** | `output_data/geographic_equity_by_school.csv` | ✅ **New in loop 8** — 210 rows (school × subject, with Quadrant/Neighborhood) |
| **Geographic equity (quadrant)** | `output_data/geographic_equity_by_quadrant.csv` | ✅ **New in loop 8** — 8 rows (4 quadrants × 2 subjects) |
| **YoY growth detail** | `output_data/yoy_growth_detail.csv` | ✅ **New in loop 9** — 14,391 rows (school × grade × subject × subgroup × transition) |
| **YoY growth summary** | `output_data/yoy_growth_summary.csv` | ✅ **New in loop 9** — 2,604 rows (school × subject × subgroup) |
| **Policy summary report** | `output_data/summary_report.xlsx` | ✅ **8 sheets** — adds YoY Growth sheet in loop 9 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| **Summary report script** | `src/generate_summary_report.py` | ✅ **Updated in loop 9** — now produces 8-sheet Excel workbook |
| **Geographic equity script** | `src/geographic_equity_analysis.py` | ✅ **New in loop 8** — joins school locations with performance data by DC quadrant |
| **YoY growth script** | `src/yoy_growth_analysis.py` | ✅ **New in loop 9** — same-grade year-over-year growth for every school, grade, subject, subgroup |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to **11 figures**; 11th figure is Same-Grade YoY Growth line chart by grade level |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 9 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 8 |

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

- **Smoke test commands (loop 9 — updated):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. `python src/proficiency_trend_analysis.py`
  9. `python src/geographic_equity_analysis.py`
  10. `python src/yoy_growth_analysis.py`
  11. `python src/generate_summary_report.py`
  12. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (callback returns **11 figures**, including the YoY growth chart)
- **Loop 9 Validate evidence:** re-ran the full smoke path from a fresh clone: dependencies, `py_compile`, `load_wide_format_data.py`, `analyze_cohort_growth.py`, `equity_gap_analysis.py`, `generate_school_rankings.py`, `proficiency_trend_analysis.py`, `geographic_equity_analysis.py`, `yoy_growth_analysis.py`, and `generate_summary_report.py` — all exit 0. Confirmed regenerated outputs: `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `geographic_equity_by_quadrant.csv` (8 rows), `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows), and `summary_report.xlsx` (8 sheets). Confirmed dashboard server path: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200, and `POST /_dash-update-component` returns **11 figures**, including the YoY growth chart.
- **Loop 9 YoY growth findings:** citywide ELA YoY avg was +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024). Math: +2.07 pp (2016→2017), −4.32 pp (2017→2018), +2.42 pp (2018→2019), +3.25 pp (2022→2023), +0.35 pp (2023→2024). COVID gap (2019→2022) is excluded — these reflect only consecutive-year within-period comparisons.
- **Loop 8 geographic equity findings:** NW avg ELA proficiency 42.7% vs. NE 24.1%, SE 20.1% (−18 pp to −23 pp gap). NW also leads in cohort growth (+4.85 pp ELA). SE schools show the largest gap vs. NW citywide. Math shows a similar pattern (NW 38.4% vs. NE/SE ~15%).
- **Loop 8 name-matching note:** 95/115 location schools match directly to growth/trends data. 20 unmatched schools are primarily high schools (no cohort transitions) and schools not represented in the 7 in-repo workbooks.
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:** (same as loop 4 — see loop 4 notes in decisions.md D-020)
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Validation blocker still open:** direct browser-console inspection remains blocked in this environment.
- **Charter vs. DCPS comparison** remains unimplemented: the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools.
- **Next recommended step:** Run **Closeout** for loop 9, using `.squad/validation_report.md` as the authoritative validation evidence.

Loop 8 closeout rechecked the backlog tasks, sprint plan, decision log, validation report, and human-facing docs, then re-ran the documented fresh-clone smoke path and dashboard callback path. The current handoff is approved for the reproducible in-repo path, but the full backlog is still not complete because `src/load_clean_data.py` still depends on external normalized OSSE files and direct browser-console inspection remains blocked in this environment.

Loop 8 closeout completed:
1. Re-ran the full smoke path from a fresh clone: dependencies, `py_compile`, `load_wide_format_data.py`, `analyze_cohort_growth.py`, `equity_gap_analysis.py`, `generate_school_rankings.py`, `proficiency_trend_analysis.py`, `geographic_equity_analysis.py`, and `generate_summary_report.py` — all exit 0.
2. Confirmed regenerated outputs: `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), and `summary_report.xlsx` (7 sheets).
3. Confirmed dashboard server path: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200, and `POST /_dash-update-component` returns **10 figures**, including the geographic-equity chart.
4. Confirmed Task 03 regression benchmark still passes: all four Stuart-Hobson 2022→2023 transitions remain within ±0.1 pp.
5. Recorded closeout signoff in `.squad/review_report.md` and `.squad/decisions.md`, with explicit follow-up to return to **Build**.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete through loop 8 — equity gap, school map, rankings, historical data ingestion, proficiency heatmap, scatter plot, summary report, and geographic equity |
| 4 | Validate | ✅ Complete for loops 1-8 |
| 5 | Closeout | ✅ Complete for loops 2-8 |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves **10 figures** (loop 8 adds geographic equity chart), school-level and citywide views functional |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |
| 07 | Formatted Excel summary report | Closeout | Statistician | ✅ Closed out — `generate_summary_report.py` exits 0; `summary_report.xlsx` regenerated with **7 sheets** (adds Geographic Equity in loop 8) |

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
| **Geographic equity (school)** | `output_data/geographic_equity_by_school.csv` | ✅ **New in loop 8** — 210 rows (school × subject, with Quadrant/Neighborhood) |
| **Geographic equity (quadrant)** | `output_data/geographic_equity_by_quadrant.csv` | ✅ **New in loop 8** — 8 rows (4 quadrants × 2 subjects) |
| **Policy summary report** | `output_data/summary_report.xlsx` | ✅ **7 sheets** — adds Geographic Equity sheet in loop 8 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| **Summary report script** | `src/generate_summary_report.py` | ✅ **Updated in loop 8** — now produces 7-sheet Excel workbook |
| **Geographic equity script** | `src/geographic_equity_analysis.py` | ✅ **New in loop 8** — joins school locations with performance data by DC quadrant |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to **10 figures**; 10th figure is Geographic Equity bar+line chart by DC quadrant |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 8 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 8 |

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

- **Smoke test commands (loop 8 — updated):**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. `python src/generate_school_rankings.py`
  8. `python src/proficiency_trend_analysis.py`
  9. `python src/geographic_equity_analysis.py`
  10. `python src/generate_summary_report.py`
  11. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (callback returns **10 figures**, including the geographic equity chart)
- **Loop 8 closeout evidence:** fresh-clone smoke path exits 0 through `generate_summary_report.py`; `output_data/summary_report.xlsx` is regenerated with 7 sheets; dashboard callback returns 10 figures including the geographic-equity chart; `.squad/review_report.md` signs off the current handoff and returns the repo to Build.
- **Loop 8 geographic equity findings:** NW avg ELA proficiency 42.7% vs. NE 24.1%, SE 20.1% (−18 pp to −23 pp gap). NW also leads in cohort growth (+4.85 pp ELA). SE schools show the largest gap vs. NW citywide. Math shows a similar pattern (NW 38.4% vs. NE/SE ~15%).
- **Loop 8 name-matching note:** 95/115 location schools match directly to growth/trends data. 20 unmatched schools are primarily high schools (no cohort transitions) and schools not represented in the 7 in-repo workbooks.
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:** (same as loop 4 — see loop 4 notes in decisions.md D-020)
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Validation blocker still open:** direct browser-console inspection remains blocked in this environment.
- **Charter vs. DCPS comparison** remains unimplemented: the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools.
- **Next recommended step:** Return to **Build** and choose the next backlog slice: restore the normalized-data / 2024-25 ingestion path or finish the blocked browser-console review for the current 10-figure dashboard.
