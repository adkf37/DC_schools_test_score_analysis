# Sprint Plan

## Current Phase: Loop 16 Closeout complete → Build next

Loop 16 adds `src/school_performance_index.py`, a standalone script that synthesises four analytical
dimensions into a single composite school performance score (0–100) for each school × subject
(All Students).  The four components are: (1) Proficiency — percentile rank of average proficiency
level (from school_consistency.csv); (2) Growth — percentile rank of average cohort-growth pp
(from school_rankings.csv); (3) Recovery — percentile rank of COVID recovery pp (from
covid_recovery_summary.csv); (4) Trajectory — percentile rank of OLS trend slope pp/yr (from
school_trajectory_classification.csv).  Each component is percentile-ranked within its subject; the
composite is the mean of available component scores.  Schools are placed in five quintiles: Q5 Top
Performers … Q1 Bottom Performers (schools with fewer than 2 valid components receive
"Insufficient Data").  Key findings: ELA Q5 Top Performers avg composite 81.1, avg proficiency
47.5%; Math Q5 avg composite 79.0, avg proficiency 45.0%.  Top ELA composite performers: Janney ES
(93.6), Hyde-Addison ES (92.7), Lafayette ES (92.0).  Top Math composite performers: Hyde-Addison
ES (96.0), Murch ES @ UDC (90.6), Bancroft ES @ Sharpe (88.4).  The dashboard now renders **18
figures**; `summary_report.xlsx` now has **15 sheets** (adds "Performance Index" sheet).

Loop 15 adds `src/school_consistency_analysis.py` as a first-class step in the smoke path.
Running the script produces `school_consistency.csv` (424 rows) and
`consistency_class_summary.csv` (10 rows).  The dashboard callback now returns **17** figures
(17th is the avg-proficiency × CV scatter coloured by consistency class), and `summary_report.xlsx`
regenerates with **14 sheets** (adds "Consistency").

Loop 14 adds `src/subgroup_trend_analysis.py`, a standalone script that computes average proficiency, COVID recovery, and same-grade YoY growth broken down by student demographic subgroup (All Students, Male, Female, Black or African American, Hispanic/Latino of any race, White, Asian, Two or more races, Economically Disadvantaged, EL Active, Students with Disabilities) for both ELA and Math across all DC schools. Unlike `equity_gap_analysis.py` (which focuses on cohort growth gaps relative to "All Students"), this analysis tracks absolute proficiency levels over time for each demographic group. Key findings: ELA proficiency gap between highest (White, 83.8%) and lowest (Students with Disabilities, 7.9%) subgroup is 75.9 pp; Hispanic/Latino took the largest COVID hit in both subjects (ELA −9.70 pp, Math −14.54 pp); Asian showed the strongest recovery (ELA +10.31 pp, Math +8.65 pp). The dashboard now renders **16 figures**; `summary_report.xlsx` now has **13 sheets** (adds "Subgroups" sheet).

Loop 11 adds `src/school_trajectory_analysis.py`, a standalone script that classifies each school's long-run proficiency trajectory by fitting an OLS linear trend to annual All Students proficiency data across all available years (2016–2024).  The slope (pp/yr) and R² measure how consistently and strongly each school is improving or declining over the multi-year period.  Key findings: ELA citywide avg slope +0.065 pp/yr (mostly Stable); Math avg slope −0.656 pp/yr (more Declining than Improving). Top ELA improver: Whittier ES (+8.2 pp/yr, 22%→39%). The dashboard now renders **13 figures**; `summary_report.xlsx` now has **10 sheets** (adds "School Trajectories" sheet).

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
| 16 | [Loop 11] School performance trajectory classification | Statistician | proficiency_trends.csv | ✅ Built — `school_trajectory_analysis.py` exits 0; `school_trajectory_classification.csv` (424 rows); dashboard returns **13 figures**; `summary_report.xlsx` has **10 sheets** |
| 17 | [Loop 12] School type (grade-band) performance analysis | Statistician | combined_all_years.csv | ✅ Built — `school_type_analysis.py` exits 0; `school_type_by_school.csv` (251 rows), `school_type_proficiency.csv` (70 rows), `school_type_summary.csv` (10 rows); dashboard returns **14 figures**; `summary_report.xlsx` has **11 sheets** |
| 18 | [Loop 13] Grade-level proficiency analysis | Statistician | combined_all_years.csv | ✅ Built — `grade_level_analysis.py` exits 0; `grade_level_proficiency.csv` (98 rows), `grade_level_summary.csv` (14 rows); dashboard returns **15 figures**; `summary_report.xlsx` has **12 sheets** |
| 19 | [Loop 14] Subgroup proficiency trend analysis | Statistician | combined_all_years.csv | ✅ Built — `subgroup_trend_analysis.py` exits 0; `subgroup_proficiency.csv` (152 rows), `subgroup_summary.csv` (22 rows); dashboard returns **16 figures**; `summary_report.xlsx` has **13 sheets** |
| 20 | [Loop 15] School performance consistency analysis | Statistician | proficiency_trends.csv | ✅ Built — `school_consistency_analysis.py` exits 0; `school_consistency.csv` (424 rows), `consistency_class_summary.csv` (10 rows); dashboard returns **17 figures**; `summary_report.xlsx` has **14 sheets** |
| 21 | [Loop 16] Multi-metric school performance index | Statistician | consistency, rankings, covid_recovery, trajectory | ✅ Built — `school_performance_index.py` exits 0; `school_performance_index.csv` (456 rows), `performance_index_summary.csv` (12 rows); dashboard returns **18 figures**; `summary_report.xlsx` has **15 sheets** |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `pip install dash plotly` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py` → `python src/equity_gap_analysis.py` → `python src/generate_school_rankings.py` → `python src/proficiency_trend_analysis.py` → `python src/geographic_equity_analysis.py` → `python src/yoy_growth_analysis.py` → `python src/covid_recovery_analysis.py` → `python src/school_trajectory_analysis.py` → `python src/school_type_analysis.py` → `python src/grade_level_analysis.py` → `python src/subgroup_trend_analysis.py` → `python src/school_consistency_analysis.py` → `python src/school_performance_index.py` → `python src/generate_summary_report.py` → `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies` (**18 figures**)
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` now has 2,560 rows (Task 03 target was ≥ 1,700 — **target met** in loop 4).
- No cohort transitions cross the 2019–2022 COVID gap; only within-year-pair transitions (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) are produced.
- `proficiency_trends.csv` has 25,629 rows covering school × year × subject × grade × subgroup proficiency.
- `summary_report.xlsx` has **15 sheets**: Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory, Geographic Equity, YoY Growth, COVID Recovery, School Trajectories, School Types, Grade Levels, Subgroups, Consistency, **Performance Index**.
- Trajectory key finding: ELA avg slope +0.065 pp/yr (Stable overall); Math avg slope −0.656 pp/yr (Declining overall). ~55% of schools have Insufficient Data (fewer than 3 years with All Students proficiency). Top improver in both ELA and Math: Whittier Elementary School.
- Grade-level key finding: Grade 4 highest ELA avg proficiency (32.7%); Grade 3 highest Math avg proficiency (33.8%); HS lowest Math (13.2%); Grade 7 largest ELA COVID impact (−10.78 pp); Grade 4 largest Math COVID impact (−11.55 pp).
- Subgroup key finding: White highest ELA avg proficiency (83.8%), Students with Disabilities lowest (7.9%), gap 75.9 pp; Hispanic/Latino took the largest COVID hit (ELA −9.70 pp, Math −14.54 pp); Asian showed the strongest recovery (ELA +10.31 pp, Math +8.65 pp).
- Consistency key finding: 212 schools have All Students ELA data; 38 High-Consistent ELA schools (avg 52.7%, avg CV 10.7%); 37 Low-Volatile ELA schools (avg 13.6%, avg CV 37.5%). Top High-Consistent ELA schools: Ross ES (86.1%), Janney ES (85.7%). Most volatile below-median ELA schools: Savoy ES (7.0% avg, 79.4% CV), Turner ES (8.3% avg, 67.8% CV). 55% of schools have Insufficient Data (fewer than 3 years).
- Performance Index key finding: ELA Q5 Top Performers avg composite 81.1, avg proficiency 47.5%; top ELA schools: Janney ES (93.6), Hyde-Addison ES (92.7), Lafayette ES (92.0). Math Q5 avg composite 79.0, avg proficiency 45.0%; top Math schools: Hyde-Addison ES (96.0), Murch ES @ UDC (90.6), Bancroft ES @ Sharpe (88.4). ~7% of schools per subject classified as "Insufficient Data" (fewer than 2 valid components).
- Next action: choose the next Build target for the next loop — normalized-data / 2024-25 ingestion, browser-console review for the current 18-figure dashboard, or deliberate narrowing of the backlog to the verified wide-format scope.


Loop 11 adds `src/school_trajectory_analysis.py`, a standalone script that classifies each school's long-run proficiency trajectory by fitting an OLS linear trend to annual All Students proficiency data across all available years (2016–2024).  The slope (pp/yr) and R² measure how consistently and strongly each school is improving or declining over the multi-year period.  Key findings: ELA citywide avg slope +0.065 pp/yr (mostly Stable); Math avg slope −0.656 pp/yr (more Declining than Improving). Top ELA improver: Whittier ES (+8.2 pp/yr, 22%→39%). The dashboard now renders **13 figures**; `summary_report.xlsx` now has **10 sheets** (adds "School Trajectories" sheet).

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
| 16 | [Loop 11] School performance trajectory classification | Statistician | proficiency_trends.csv | ✅ Built — `school_trajectory_analysis.py` exits 0; `school_trajectory_classification.csv` (424 rows); dashboard returns **13 figures**; `summary_report.xlsx` has **10 sheets** |
| 17 | [Loop 12] School type (grade-band) performance analysis | Statistician | combined_all_years.csv | ✅ Built — `school_type_analysis.py` exits 0; `school_type_by_school.csv` (251 rows), `school_type_proficiency.csv` (70 rows), `school_type_summary.csv` (10 rows); dashboard returns **14 figures**; `summary_report.xlsx` has **11 sheets** |
| 18 | [Loop 13] Grade-level proficiency analysis | Statistician | combined_all_years.csv | ✅ Built — `grade_level_analysis.py` exits 0; `grade_level_proficiency.csv` (98 rows), `grade_level_summary.csv` (14 rows); dashboard returns **15 figures**; `summary_report.xlsx` has **12 sheets** |
| 19 | [Loop 14] Subgroup proficiency trend analysis | Statistician | combined_all_years.csv | ✅ Built — `subgroup_trend_analysis.py` exits 0; `subgroup_proficiency.csv` (152 rows), `subgroup_summary.csv` (22 rows); dashboard returns **16 figures**; `summary_report.xlsx` has **13 sheets** |
| 20 | [Loop 15] School performance consistency analysis | Statistician | proficiency_trends.csv | ✅ Built — `school_consistency_analysis.py` exits 0; `school_consistency.csv` (424 rows), `consistency_class_summary.csv` (10 rows); dashboard returns **17 figures**; `summary_report.xlsx` has **14 sheets** |

## Notes

- Smoke test commands (from fresh clone): `pip install -r requirements.txt` → `pip install dash plotly` → `python -m py_compile src/*.py app/*.py inspect_data.py` → `python src/load_wide_format_data.py` → `python src/analyze_cohort_growth.py` → `python src/equity_gap_analysis.py` → `python src/generate_school_rankings.py` → `python src/proficiency_trend_analysis.py` → `python src/geographic_equity_analysis.py` → `python src/yoy_growth_analysis.py` → `python src/covid_recovery_analysis.py` → `python src/school_trajectory_analysis.py` → `python src/school_type_analysis.py` → `python src/grade_level_analysis.py` → `python src/subgroup_trend_analysis.py` → `python src/school_consistency_analysis.py` → `python src/generate_summary_report.py` → `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies` (**17 figures**)
- `load_clean_data.py` still requires normalized OSSE files (download from OSSE website) — use `load_wide_format_data.py` for the files already in the repo.
- `cohort_growth_summary.csv` now has 2,560 rows (Task 03 target was ≥ 1,700 — **target met** in loop 4).
- No cohort transitions cross the 2019–2022 COVID gap; only within-year-pair transitions (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) are produced.
- `proficiency_trends.csv` has 25,629 rows covering school × year × subject × grade × subgroup proficiency.
- `summary_report.xlsx` has **14 sheets**: Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory, Geographic Equity, YoY Growth, COVID Recovery, School Trajectories, School Types, Grade Levels, Subgroups, **Consistency**.
- Trajectory key finding: ELA avg slope +0.065 pp/yr (Stable overall); Math avg slope −0.656 pp/yr (Declining overall). ~55% of schools have Insufficient Data (fewer than 3 years with All Students proficiency). Top improver in both ELA and Math: Whittier Elementary School.
- Grade-level key finding: Grade 4 highest ELA avg proficiency (32.7%); Grade 3 highest Math avg proficiency (33.8%); HS lowest Math (13.2%); Grade 7 largest ELA COVID impact (−10.78 pp); Grade 4 largest Math COVID impact (−11.55 pp).
- Subgroup key finding: White highest ELA avg proficiency (83.8%), Students with Disabilities lowest (7.9%), gap 75.9 pp; Hispanic/Latino took the largest COVID hit (ELA −9.70 pp, Math −14.54 pp); Asian showed the strongest recovery (ELA +10.31 pp, Math +8.65 pp).
- Consistency key finding: 212 schools have All Students ELA data; 38 High-Consistent ELA schools (avg 52.7%, avg CV 10.7%); 37 Low-Volatile ELA schools (avg 13.6%, avg CV 37.5%). Top High-Consistent ELA schools: Ross ES (86.1%), Janney ES (85.7%). Most volatile below-median ELA schools: Savoy ES (7.0% avg, 79.4% CV), Turner ES (8.3% avg, 67.8% CV). 55% of schools have Insufficient Data (fewer than 3 years).
- Next action: Validate Loop 15 (run full smoke path including school_consistency_analysis.py, check 17-figure dashboard and 14-sheet workbook), then proceed to Closeout or next Build loop.
