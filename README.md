# DC Schools Test Score Analysis

This repository is intended to analyze DC OSSE assessment files across the 2021–22 through 2024–25 school years, combine them into a single cleaned dataset, and then compute cohort-growth outputs for policy analysis.

## Current project state

**As of 2026-05-02, Loop 17 Closeout is complete: `charter_dcps_analysis.py` is part of the approved smoke path; the reproducible in-repo pipeline produces a 19-figure analytical dashboard and a 16-sheet summary workbook, and the repo now returns to Build for remaining backlog scope.**

What was validated from a fresh clone:

- `python -m pip install -r requirements.txt` ✅
- `python -m pip install dash plotly` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_wide_format_data.py` ✅
- `python src/analyze_cohort_growth.py` ✅
- `python src/equity_gap_analysis.py` ✅
- `python src/generate_school_rankings.py` ✅
- `python src/proficiency_trend_analysis.py` ✅
- `python src/geographic_equity_analysis.py` ✅
- `python src/yoy_growth_analysis.py` ✅
- `python src/covid_recovery_analysis.py` ✅
- `python src/school_trajectory_analysis.py` ✅
- `python src/school_type_analysis.py` ✅
- `python src/grade_level_analysis.py` ✅
- `python src/subgroup_trend_analysis.py` ✅
- `python src/school_consistency_analysis.py` ✅
- `python src/school_performance_index.py` ✅
- `python src/charter_dcps_analysis.py` ✅
- `python src/generate_summary_report.py` ✅
- `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component` ✅

### What this signoff covers

- The in-repo wide-format workbooks for 2015-16, 2016-17, 2017-18, 2018-19, 2021-22, 2022-23, and 2023-24
- Regeneration of:
  - `output_data/combined_all_years.csv` (28,069 rows)
  - `output_data/processing_report.txt`
  - `output_data/cohort_growth_detail.csv` (12,956 rows)
  - `output_data/cohort_growth_summary.csv` (2,560 rows)
  - `output_data/cohort_growth_pivot.xlsx` (6 sheets)
  - `output_data/equity_gap_detail.csv` (13,008 rows)
  - `output_data/equity_gap_summary.csv` (2,138 rows)
  - `output_data/proficiency_trends.csv` (25,629 rows)
  - `output_data/geographic_equity_by_school.csv` (210 rows)
  - `output_data/geographic_equity_by_quadrant.csv` (8 rows)
  - `output_data/yoy_growth_detail.csv` (14,391 rows)
  - `output_data/yoy_growth_summary.csv` (2,604 rows)
  - `output_data/covid_recovery_detail.csv` (1,239 rows)
  - `output_data/covid_recovery_summary.csv` (200 rows)
  - `output_data/school_trajectory_classification.csv` (424 rows)
  - `output_data/school_type_by_school.csv` (251 rows)
  - `output_data/school_type_proficiency.csv` (70 rows)
  - `output_data/school_type_summary.csv` (10 rows)
  - `output_data/grade_level_proficiency.csv` (98 rows)
  - `output_data/grade_level_summary.csv` (14 rows)
  - `output_data/subgroup_proficiency.csv` (152 rows)
  - `output_data/subgroup_summary.csv` (22 rows)
  - `output_data/school_consistency.csv` (424 rows)
  - `output_data/consistency_class_summary.csv` (10 rows)
  - `output_data/school_performance_index.csv` (456 rows)
  - `output_data/performance_index_summary.csv` (12 rows)
  - `output_data/school_sector_by_school.csv` (251 rows)
  - `output_data/school_sector_proficiency.csv` (48 rows)
  - `output_data/school_sector_summary.csv` (8 rows)
  - `output_data/summary_report.xlsx` (16-sheet Excel policy summary)
- Stuart-Hobson benchmark transitions staying within ±0.1 pp
- Task 05 significance fields (`p_value`, `significant`, `pct_significant_transitions`)
- Loop 2 equity-gap outputs and Task 04 dashboard startup plus live callback rendering of all **nineteen** analytical figures in the current handoff
- Loop 3 policy-analysis outputs on the expanded historical dataset:
  - `output_data/school_rankings.csv` (422 rows)
  - `output_data/school_equity_rankings.csv` (414 rows)
- Loop 4 dashboard map path with `input_data/school_locations.csv` present:
  - file contains 115 school locations
  - live callback returns a real `School Performance Map`
  - current 2024 Math / All Students view plots 113 schools (the citywide `DC Public Schools` aggregate has no map point)
- Loop 8 geographic-equity outputs and handoff findings:
  - `geographic_equity_by_quadrant.csv` shows NW average ELA proficiency at 42.71% vs. 24.09% in NE and 20.15% in SE
  - the dashboard callback returns a geographic-equity figure: `Math – Average Proficiency & Cohort Growth by DC Quadrant`
  - `summary_report.xlsx` now includes a `Geographic Equity` sheet
- Loop 9 same-grade YoY outputs and handoff findings:
  - `yoy_growth_detail.csv` confirms only consecutive transitions are included: 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024
  - citywide ELA YoY averages are +4.82, +0.94, +4.91, +2.02, and +0.48 pp across those transitions; Math is +2.07, −4.32, +2.42, +3.25, and +0.35 pp
  - the dashboard callback now returns an 11th figure: `Math – Citywide Same-Grade YoY Growth by Grade Level`
  - `summary_report.xlsx` now includes a `YoY Growth` sheet
- Loop 10 COVID recovery outputs and handoff findings:
  - `covid_recovery_detail.csv` compares 2019, 2022, and 2024 proficiency for 1,239 school × subject × subgroup observations
  - `covid_recovery_summary.csv` classifies 200 school/subject rows as Exceeded Pre-COVID, Fully Recovered, Partially Recovered, Still Below Pre-COVID, or No 2024 Data
  - citywide ELA averages show a −3.94 pp COVID impact, +1.75 pp recovery, and −2.15 pp net gap vs. pre-COVID; Math shows −8.56 pp impact, +3.17 pp recovery, and −5.43 pp net gap
  - the dashboard callback now returns a 12th figure: `Math – COVID Impact (2019→2022) vs Recovery (2022→2024)`
  - `summary_report.xlsx` now includes a `COVID Recovery` sheet
- Loop 11 school trajectory outputs and handoff findings:
  - `school_trajectory_classification.csv` contains 424 school × subject rows with OLS slope, R², and a trajectory class
  - citywide average slopes are +0.065 pp/yr in ELA and −0.656 pp/yr in Math
  - Whittier Elementary School is the top improver in both subjects
  - the dashboard callback now returns a 13th figure: `Math – School Proficiency Trajectory (2016–2024)`
  - `summary_report.xlsx` now includes a `School Trajectories` sheet
- Loop 12 school type outputs and handoff findings:
  - `school_type_by_school.csv` contains 251 school-level type assignments: 147 Elementary, 39 High School, 31 Elementary-Middle, 28 Middle School, and 6 Middle-High
  - `school_type_summary.csv` shows Elementary schools leading average proficiency in both ELA (31.85%) and Math (30.91%)
  - Elementary-Middle schools have the strongest ELA cohort growth (+6.56 pp/yr), Middle School has the strongest ELA recovery (+3.37 pp), and Elementary has the strongest Math recovery (+4.06 pp)
  - the dashboard callback now returns a 14th figure: `Math – Citywide Avg Proficiency by School Type`
  - `summary_report.xlsx` now includes a `School Types` sheet
- Loop 13 grade-level outputs and handoff findings:
  - `grade_level_proficiency.csv` contains 98 grade × subject × year rows
  - `grade_level_summary.csv` contains 14 grade × subject summary rows
  - ELA average proficiency peaks at Grade 4 (32.74%) and bottoms at Grade 6 (26.04%)
  - Math average proficiency peaks at Grade 3 (33.76%) and bottoms at High School (13.17%)
  - Grade 7 has the largest ELA COVID impact (−10.78 pp), Grade 4 has the largest Math COVID impact (−11.55 pp), Grade 6 has the strongest ELA recovery (+4.49 pp), and Grade 4 has the strongest Math recovery (+4.70 pp)
  - the dashboard callback now returns a 15th figure: `Math – Citywide Avg Proficiency by Grade Level`
  - `summary_report.xlsx` now includes a `Grade Levels` sheet
- Loop 15 consistency outputs and handoff findings:
  - `school_consistency.csv` contains 424 rows (one per school × subject) with avg proficiency, std deviation, CV, min, max, range, and consistency class
  - `consistency_class_summary.csv` contains 10 rows (per consistency class × subject)
  - ELA: 38 High-Consistent schools (avg 52.7%, avg CV 10.7%), 37 Low-Volatile schools (avg 13.6%, avg CV 37.5%), 55% Insufficient Data
  - Math: 39 High-Consistent schools (avg 47.1%, avg CV 13.2%), 38 Low-Volatile schools (avg 9.0%, avg CV 59.0%), 55% Insufficient Data
  - Top ELA High-Consistent: Ross ES (86.1% avg, CV 3.9%), Janney ES (85.7% avg, CV 3.9%), Key ES (79.6% avg, CV 3.8%)
  - Most volatile below-median ELA: Savoy ES (7.0% avg, CV 79.4%), Turner ES (8.3% avg, CV 67.8%), Kramer MS (6.3% avg, CV 62.6%)
  - the dashboard callback now returns a 17th figure: avg-proficiency × CV scatter coloured by consistency class
  - `summary_report.xlsx` now includes a `Consistency` sheet
- Loop 16 performance-index outputs and handoff findings:
  - `school_performance_index.csv` contains 456 rows (school × subject composite score, quintile, valid-component count, and four percentile-rank component scores)
  - `performance_index_summary.csv` contains 12 rows (per composite quintile × subject, including Insufficient Data)
  - ELA quintiles: 43 Q5 / 42 Q4 / 42 Q3 / 42 Q2 / 42 Q1 / 17 Insufficient Data; top ELA composite schools are Janney ES (93.6), Hyde-Addison ES (92.7), and Lafayette ES (92.0)
  - Math quintiles: 43 Q5 / 42 Q4 / 42 Q3 / 42 Q2 / 42 Q1 / 17 Insufficient Data; top Math composite schools are Hyde-Addison ES (96.0), Murch ES @ UDC (90.6), and Bancroft ES @ Sharpe (88.4)
  - the dashboard callback now returns an 18th figure: `Math – Multi-Metric School Performance Index`
  - `summary_report.xlsx` now includes a `Performance Index` sheet
- Loop 17 school-sector outputs and handoff findings:
  - `school_sector_by_school.csv` contains 251 school-level sector assignments: 222 DCPS Traditional, 13 DCPS Specialized, 13 DCPS Alternative, and 3 Charter
  - `school_sector_summary.csv` contains 8 rows (4 sectors × 2 subjects)
  - ELA sector averages: DCPS Specialized 50.3%, Charter 32.1%, DCPS Traditional 29.8%, DCPS Alternative 13.1%
  - Math sector averages: DCPS Specialized 34.2%, DCPS Traditional 25.9%, Charter 13.5%, DCPS Alternative 2.6%
  - the dashboard callback now returns a 19th figure: `Math – Avg Proficiency by School Program Sector`
  - `summary_report.xlsx` now includes a `School Sectors` sheet
- Cohort transitions for consecutive year pairs only: 2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024. There is no 2019→2022 transition because OSSE did not release comparable annual school-level assessment files for the COVID-disrupted 2020 and 2021 school years.

### Remaining gaps

- `src/load_clean_data.py` still targets the normalized 4-workbook OSSE path and depends on files that are not committed in this repo.
- The 2024-25 source workbook is still missing from the in-repo dataset, so the original full-data backlog target is not met.
- The original normalized-data success criteria in `backlog/README.md` are still open: four exact OSSE workbooks are not all present in-repo, `load_clean_data.py` is not reproducible here, and the repo therefore does not meet the full ≥395,000-row ingestion target.
- Direct browser-console inspection during manual interaction remains blocked in this environment.
- Historical school names vary across eras (for example shortened vs. full school names), so cross-era school comparisons should be interpreted carefully even though within-pair cohort transitions are valid.

## Expected pipeline

For the reproducible in-repo path, use:

```bash
python -m pip install -r requirements.txt
python src/load_wide_format_data.py
python src/analyze_cohort_growth.py
python src/equity_gap_analysis.py
python src/generate_school_rankings.py
python src/proficiency_trend_analysis.py
python src/geographic_equity_analysis.py
python src/yoy_growth_analysis.py
python src/covid_recovery_analysis.py
python src/school_trajectory_analysis.py
python src/school_type_analysis.py
python src/grade_level_analysis.py
python src/subgroup_trend_analysis.py
python src/school_consistency_analysis.py
python src/school_performance_index.py
python src/charter_dcps_analysis.py
python src/generate_summary_report.py
```

If you want to run the dashboard after the analytical outputs are regenerated:

```bash
python -m pip install dash plotly
python app/app_simple.py
```

If you have downloaded the full normalized OSSE files separately, the intended alternative workflow is:

```bash
python -m pip install -r requirements.txt
python src/load_clean_data.py
python src/analyze_cohort_growth.py
python src/equity_gap_analysis.py
python src/generate_school_rankings.py
python src/proficiency_trend_analysis.py
python src/geographic_equity_analysis.py
python src/yoy_growth_analysis.py
python src/covid_recovery_analysis.py
python src/school_trajectory_analysis.py
python src/school_type_analysis.py
python src/grade_level_analysis.py
python src/subgroup_trend_analysis.py
python src/school_consistency_analysis.py
python src/school_performance_index.py
python src/charter_dcps_analysis.py
python src/generate_summary_report.py
```

## Required source files

Backlog Task 01 still expects these four annual workbooks for the normalized loader:

- `2021-22 School Level PARCC and MSAA Data.xlsx`
- `2022-23 School Level PARCC and MSAA Data_9_5.xlsx`
- `DC Cape Scores 2023-2024.xlsx` or a documented equivalent that the loader recognizes
- `2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx`

## Intended outputs

If the loader and cohort analysis run successfully, the project should produce:

- `output_data/combined_all_years.csv`
- `output_data/processing_report.txt`
- `output_data/cohort_growth_detail.csv`
- `output_data/cohort_growth_summary.csv`
- `output_data/cohort_growth_pivot.xlsx`
- `output_data/equity_gap_detail.csv`
- `output_data/equity_gap_summary.csv`
- `output_data/school_rankings.csv`
- `output_data/school_equity_rankings.csv`
- `output_data/proficiency_trends.csv`
- `output_data/geographic_equity_by_school.csv`
- `output_data/geographic_equity_by_quadrant.csv`
- `output_data/yoy_growth_detail.csv`
- `output_data/yoy_growth_summary.csv`
- `output_data/covid_recovery_detail.csv`
- `output_data/covid_recovery_summary.csv`
- `output_data/school_trajectory_classification.csv`
- `output_data/school_type_by_school.csv`
- `output_data/school_type_proficiency.csv`
- `output_data/school_type_summary.csv`
- `output_data/grade_level_proficiency.csv`
- `output_data/grade_level_summary.csv`
- `output_data/subgroup_proficiency.csv`
- `output_data/subgroup_summary.csv`
- `output_data/school_consistency.csv`
- `output_data/consistency_class_summary.csv`
- `output_data/school_performance_index.csv`
- `output_data/performance_index_summary.csv`
- `output_data/school_sector_by_school.csv`
- `output_data/school_sector_proficiency.csv`
- `output_data/school_sector_summary.csv`
- `output_data/summary_report.xlsx`

The current closeout review regenerated these files from a fresh clone via the wide-format loader path listed above.

## Supporting documentation

- `STATUS.md` — current phase, blockers, and next recommended step
- `.squad/validation_report.md` — prior validation evidence for the wide-format smoke path
- `.squad/review_report.md` — closeout decision and explicit return-to-work recommendation
- `docs/methods.md` — cohort-growth and statistical-significance methodology

## Next steps

**Loop 17 (closed out):** the geographic-equity + same-grade YoY + COVID recovery + school trajectory + school type + grade-level + subgroup-trend + consistency + performance-index + school-sector outputs, the 19-figure dashboard path, and the 16-sheet summary workbook are validated and handoff-ready for the reproducible in-repo path.

**Future Build loops:**
1. Restore the full normalized-data / 2024-25 ingestion path (requires downloading OSSE workbooks).
2. Confirm browser-console cleanliness during manual interaction with the 19-figure dashboard.
3. Re-run Validate + Closeout after the next Build loop changes the evidence or scope.
