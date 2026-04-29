# Sprint Plan

## Current Phase: Loop 10 Build complete → Validate next

Loop 10 adds `src/covid_recovery_analysis.py`, a standalone script that quantifies the pandemic's impact on DC school test performance and measures recovery.  Using 2019 as the pre-COVID benchmark and 2022/2024 as post-COVID years, it computes for every school × subject × student subgroup: COVID impact (2019→2022), recovery progress (2022→2024), net change vs. pre-COVID, and a recovery status classification (Exceeded Pre-COVID / Fully Recovered / Partially Recovered / Still Below Pre-COVID).  Key findings: citywide ELA avg COVID impact −3.94 pp, recovery +1.75 pp, net −2.15 pp; Math impact −8.56 pp, recovery +3.17 pp, net −5.43 pp.  The dashboard now renders 12 figures; `summary_report.xlsx` now has 9 sheets (adds "COVID Recovery" sheet).

Loop 9 adds `src/yoy_growth_analysis.py`, a standalone script that computes same-grade year-over-year (YoY) growth for every school, grade, subject, and student subgroup.  This fulfils the backlog README goal: "Compute cohort growth (Grade N → Grade N+1, Year Y → Year Y+1) and same-grade year-over-year growth for every school, subject, and student subgroup."  Key findings: citywide ELA YoY growth averaged +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024).  The dashboard now renders 11 figures; `summary_report.xlsx` now has 8 sheets (adds "YoY Growth" sheet).

Loop 8 adds `src/geographic_equity_analysis.py`, which joins school location data with cohort growth and proficiency trends to surface performance disparities by DC geographic quadrant (NE / NW / SE / SW).  Key finding: NW schools average 42.7% ELA proficiency vs. 20–24% in NE/SE, a 18–23 pp geographic gap.  The dashboard now renders 10 figures; `summary_report.xlsx` now has 7 sheets (adds "Geographic Equity" sheet).

Loop 7 adds `src/generate_summary_report.py`, a formatted 6-sheet Excel policy-summary workbook (`output_data/summary_report.xlsx`). This fulfills the "Generate formatted Excel/PDF summary reports" item from `backlog/phases.md` Phase 3 Build that remained open after loop 6. No new pipeline dependencies are required; the report reads from already-generated output CSVs.

## Ordered Execution Plan

| Order | Task | Owner | Depends On | Status |
|-------|------|-------|------------|--------|
| 1 | [Task 01] Ingest raw data | Data Engineer | — | ✅ Unblocked — `load_wide_format_data.py` reads files in repo |
| 2 | [Task 02] Clean & standardize data | Data Engineer | Task 01 | ✅ `combined_all_years.csv` generated |
| 3 | [Task 03] Cohort growth analysis | Statistician | Task 02 | ✅ Verified — 5,391 detail rows, benchmarks pass |
| 4 | [Task 04] Interactive dashboard | Data Engineer | Task 02 | ✅ Validated — app starts without errors, 7-figure callback path renders |
| 5 | [Task 05] Statistical significance tests | Statistician | Task 03 | ✅ Verified — p_value and significant columns present |
| 6 | [Loop 2] Equity gap analysis | Statistician | Task 03 | ✅ Verified — equity CSVs generated and dashboard extended with 2 equity charts |
| 7 | [Loop 3] School rankings | Statistician | Loop 2 equity outputs | ✅ Verified — `generate_school_rankings.py` regenerates 192 growth rankings and 187 equity rankings |
| 8 | [Loop 3] Locations-backed dashboard map | Data Engineer | Task 04 | ✅ Verified — `school_locations.csv` present and live callback returns a real map with 113 plotted schools |
| 9 | [Loop 4] Ingest historical PARCC files (2015-16 through 2018-19) | Statistician | Task 01 | ✅ Built — `load_wide_format_data.py` now loads all 7 in-repo workbooks; summary rows = 2,560 (target ≥ 1,700 met) |
| 10 | [Loop 5] Proficiency trend analysis + heatmap | Statistician | Task 02 | ✅ Built — `proficiency_trend_analysis.py` exits 0; dashboard now returns 8 figures including Grade × Year heatmap |
| 11 | [Loop 6] Baseline Proficiency vs. Cohort Growth scatter plot | Statistician | Task 03 | ✅ Built — dashboard now returns **9 figures**; scatter uses `cohort_growth_summary.csv` |
| 12 | [Loop 7] Formatted Excel policy summary report | Statistician | Tasks 03, 06, rankings, trends | ✅ Built — `generate_summary_report.py` exits 0; produces `output_data/summary_report.xlsx` (6 sheets) |
| 13 | [Loop 8] Geographic equity analysis | Statistician | school_locations.csv, trends, growth | ✅ Built — `geographic_equity_analysis.py` exits 0; dashboard returns **10 figures**; `summary_report.xlsx` has **7 sheets** |
| 14 | [Loop 9] Same-grade year-over-year growth analysis | Statistician | Task 02 | ✅ Built — `yoy_growth_analysis.py` exits 0; `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows); dashboard returns **11 figures**; `summary_report.xlsx` has **8 sheets** |
| 15 | [Loop 10] COVID recovery analysis | Statistician | Task 02 | ✅ Built — `covid_recovery_analysis.py` exits 0; `covid_recovery_detail.csv` (1,239 rows), `covid_recovery_summary.csv` (200 rows); dashboard returns **12 figures**; `summary_report.xlsx` has **9 sheets** |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `pip install dash plotly` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py` → `python src/equity_gap_analysis.py` → `python src/generate_school_rankings.py` → `python src/proficiency_trend_analysis.py` → `python src/geographic_equity_analysis.py` → `python src/yoy_growth_analysis.py` → `python src/covid_recovery_analysis.py` → `python src/generate_summary_report.py` → `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies` (12 figures)
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` now has 2,560 rows (Task 03 target was ≥ 1,700 — **target met** in loop 4).
- No cohort transitions cross the 2019–2022 COVID gap; only within-year-pair transitions (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) are produced.
- `proficiency_trends.csv` has 25,629 rows covering school × year × subject × grade × subgroup proficiency.
- Citywide avg proficiency (All Students): ELA rose from 22.7% (2016) to 35.2% (2019), dropped to 29.4% (2022), and recovered to 32.1% (2024); Math followed a similar pattern.
- `summary_report.xlsx` has 8 sheets: Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory, Geographic Equity, **YoY Growth**.
- YoY growth key finding: citywide ELA avg +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024). Math: +2.07, −4.32, +2.42, +3.25, +0.35 pp for the same periods.
- Next action: validate loop 9 outputs (run smoke path, confirm 11 figures, 8 sheets), then Closeout loop 9.
