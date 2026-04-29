# Project Status — DC Schools Test Score Analysis

## Current Objective

**Loop 10 Build complete — COVID Recovery Analysis added; return to Validate next.**

Loop 10 builds `src/covid_recovery_analysis.py`, which quantifies the pandemic's impact on DC school test performance and measures recovery progress. Using 2019 as the pre-COVID benchmark and 2022/2024 as post-COVID years, it computes COVID impact (2019→2022), recovery (2022→2024), net change vs. pre-COVID, and a recovery-status classification (Exceeded Pre-COVID / Fully Recovered / Partially Recovered / Still Below Pre-COVID) for every school × subject × student-subgroup combination.

Loop 10 Build completed:
1. Created `src/covid_recovery_analysis.py` — standalone script reading `combined_all_years.csv`, computing 2019→2022 COVID impact and 2022→2024 recovery for 100 schools per subject (All Students); minimum N=10 filter applied throughout.
2. Outputs: `covid_recovery_detail.csv` (1,239 rows: school × subject × subgroup × milestone years) and `covid_recovery_summary.csv` (200 rows: school × subject, All Students only, with recovery status).
3. Extended `app/app_simple.py` — loads `covid_recovery_summary.csv`; callback now returns **12 figures** (12th is a COVID recovery scatter/grouped-bar chart).
4. Extended `src/generate_summary_report.py` — adds Sheet 9 "COVID Recovery" to `summary_report.xlsx` when `covid_recovery_summary.csv` is present (graceful skip if absent); workbook now has **9 sheets**.
5. All four Stuart-Hobson 2022→2023 benchmarks remain within ±0.1 pp.
6. Fresh-clone smoke path validated through `generate_summary_report.py` — all scripts exit 0.

Loop 9 closeout rechecked the backlog tasks, sprint plan, decision log, validation report, and human-facing docs, then re-ran the documented fresh-clone smoke path plus the dashboard HTTP/callback path. The same-grade year-over-year (YoY) growth deliverable remains reproducible end to end: citywide ELA YoY growth averaged +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024); Math shows a similar pattern with a 2017→2018 dip (avg −4.32 pp) and recovery in 2022→2023 (+3.25 pp). The dashboard renders **11 figures**; `summary_report.xlsx` now has **8 sheets** (adds "YoY Growth" sheet); the current in-repo handoff is approved, but the original normalized-data / 2024-25 path and direct browser-console inspection remain open.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete through loop 10 — equity gap, school map, rankings, historical data ingestion, proficiency heatmap, scatter plot, summary report, geographic equity, same-grade YoY growth, COVID recovery analysis |
| 4 | Validate | ✅ Complete for loops 1-9; loop 10 pending |
| 5 | Closeout | ✅ Complete for loops 2-9; loop 10 pending |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves **12 figures** (loop 10 adds COVID recovery chart), school-level and citywide views functional |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |
| 07 | Formatted Excel summary report | Closeout | Statistician | ✅ Closed out — `generate_summary_report.py` exits 0; `summary_report.xlsx` regenerated with **9 sheets** (adds COVID Recovery in loop 10) |

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
| **COVID recovery detail** | `output_data/covid_recovery_detail.csv` | ✅ **New in loop 10** — 1,239 rows (school × subject × subgroup × milestone years) |
| **COVID recovery summary** | `output_data/covid_recovery_summary.csv` | ✅ **New in loop 10** — 200 rows (school × subject, All Students, with recovery status) |
| **Policy summary report** | `output_data/summary_report.xlsx` | ✅ **9 sheets** — adds COVID Recovery sheet in loop 10 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| **Summary report script** | `src/generate_summary_report.py` | ✅ **Updated in loop 10** — now produces 9-sheet Excel workbook |
| **Geographic equity script** | `src/geographic_equity_analysis.py` | ✅ **New in loop 8** — joins school locations with performance data by DC quadrant |
| **YoY growth script** | `src/yoy_growth_analysis.py` | ✅ **New in loop 9** — same-grade year-over-year growth for every school, grade, subject, subgroup |
| **COVID recovery script** | `src/covid_recovery_analysis.py` | ✅ **New in loop 10** — 2019→2022 COVID impact and 2022→2024 recovery per school, subject, subgroup |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to **12 figures**; 12th figure is COVID Recovery scatter/grouped-bar chart |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 9 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 9 |

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

- **Smoke test commands (loop 10 — updated):**
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
  11. `python src/covid_recovery_analysis.py`
  12. `python src/generate_summary_report.py`
  13. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (callback returns **12 figures**, including the COVID recovery chart)
- **Loop 10 Build evidence:** ran full smoke path from a fresh clone; all scripts exit 0. Generated `covid_recovery_detail.csv` (1,239 rows) and `covid_recovery_summary.csv` (200 rows); `summary_report.xlsx` now has 9 sheets; dashboard declares 12 figure outputs.
- **Loop 10 COVID recovery findings:** citywide ELA avg COVID impact −3.94 pp (2019→2022), recovery +1.75 pp (2022→2024), net vs. pre-COVID −2.15 pp. Math was hit harder: −8.56 pp impact, +3.17 pp recovery, net −5.43 pp. Recovery status: 38% Partially Recovered, 25% Still Below Pre-COVID, 24% Exceeded Pre-COVID, 12% Fully Recovered, 2% No 2024 Data (200 school/subject observations, All Students).
- **Loop 9 YoY growth findings:** citywide ELA YoY avg was +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024). Math: +2.07 pp (2016→2017), −4.32 pp (2017→2018), +2.42 pp (2018→2019), +3.25 pp (2022→2023), +0.35 pp (2023→2024). COVID gap (2019→2022) is excluded — these reflect only consecutive-year within-period comparisons.
- **Loop 8 geographic equity findings:** NW avg ELA proficiency 42.7% vs. NE 24.1%, SE 20.1% (−18 pp to −23 pp gap). NW also leads in cohort growth (+4.85 pp ELA). SE schools show the largest gap vs. NW citywide. Math shows a similar pattern (NW 38.4% vs. NE/SE ~15%).
- **Loop 8 name-matching note:** 95/115 location schools match directly to growth/trends data. 20 unmatched schools are primarily high schools (no cohort transitions) and schools not represented in the 7 in-repo workbooks.
- **Cohort-transition years available:** 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. No transitions cross the 2019–2022 COVID gap.
- **Historical data caveats:** (same as loop 4 — see loop 4 notes in decisions.md D-020)
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo.
- **Validation blocker still open:** direct browser-console inspection remains blocked in this environment.
- **Charter vs. DCPS comparison** remains unimplemented: the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools.
- **Next recommended step:** Run **Validate** for loop 10 — re-run the smoke path, confirm 12 figures and 9 workbook sheets, then advance to **Closeout**.
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
