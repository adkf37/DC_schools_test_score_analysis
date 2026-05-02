# Validation Report

**Date:** 2026-05-02  
**Reviewer:** Ralph  
**Recommendation:** **PASS — advance loop 17 to Closeout**

## Scope

Validate the latest build output against the current sprint commitments for loop 17: the 7-workbook wide-format ingestion path, regenerated cohort/significance/equity/rankings/proficiency-trend/geographic-equity/YoY/COVID/trajectory/school-type/grade-level/subgroup/consistency/performance-index/school-sector outputs, the 16-sheet policy summary workbook, and the dashboard startup/rendering path with the committed 19 analytical figures.

## Checks Run

1. **Core dependencies**
   - Command: `python -m pip install -r requirements.txt`
   - Result: ✅ Passed

2. **Optional dashboard dependencies**
   - Command: `python -m pip install dash plotly`
   - Result: ✅ Passed

3. **Python syntax sanity check**
   - Command: `python -m py_compile src/*.py app/*.py inspect_data.py`
   - Result: ✅ Passed

4. **Wide-format pipeline + reporting smoke test**
   - Commands:
      - `python src/load_wide_format_data.py`
      - `python src/analyze_cohort_growth.py`
      - `python src/equity_gap_analysis.py`
      - `python src/generate_school_rankings.py`
      - `python src/proficiency_trend_analysis.py`
      - `python src/geographic_equity_analysis.py`
      - `python src/yoy_growth_analysis.py`
      - `python src/covid_recovery_analysis.py`
      - `python src/school_trajectory_analysis.py`
      - `python src/school_type_analysis.py`
      - `python src/grade_level_analysis.py`
      - `python src/subgroup_trend_analysis.py`
      - `python src/school_consistency_analysis.py`
      - `python src/school_performance_index.py`
      - `python src/charter_dcps_analysis.py`
      - `python src/generate_summary_report.py`
    - Result: ✅ Passed
    - Evidence:
      - Loaded **7** in-repo workbooks covering school years **2016, 2017, 2018, 2019, 2022, 2023, 2024**
      - Wrote `output_data/combined_all_years.csv` with **28,069 rows**
      - Wrote `output_data/cohort_growth_detail.csv` with **12,956 rows**
      - Wrote `output_data/cohort_growth_summary.csv` with **2,560 rows**
      - Wrote `output_data/cohort_growth_pivot.xlsx` with **6 sheets**
      - Wrote `output_data/equity_gap_detail.csv` with **13,008 rows**
      - Wrote `output_data/equity_gap_summary.csv` with **2,138 rows**
      - Wrote `output_data/school_rankings.csv` with **422 rows**
      - Wrote `output_data/school_equity_rankings.csv` with **414 rows**
      - Wrote `output_data/proficiency_trends.csv` with **25,629 rows**
      - Wrote `output_data/geographic_equity_by_school.csv` with **210 rows**
      - Wrote `output_data/geographic_equity_by_quadrant.csv` with **8 rows**
      - Wrote `output_data/yoy_growth_detail.csv` with **14,391 rows**
      - Wrote `output_data/yoy_growth_summary.csv` with **2,604 rows**
      - Wrote `output_data/covid_recovery_detail.csv` with **1,239 rows**
      - Wrote `output_data/covid_recovery_summary.csv` with **200 rows**
      - Wrote `output_data/school_trajectory_classification.csv` with **424 rows**
      - Wrote `output_data/school_type_by_school.csv` with **251 rows**
      - Wrote `output_data/school_type_proficiency.csv` with **70 rows**
      - Wrote `output_data/school_type_summary.csv` with **10 rows**
      - Wrote `output_data/grade_level_proficiency.csv` with **98 rows**
      - Wrote `output_data/grade_level_summary.csv` with **14 rows**
      - Wrote `output_data/subgroup_proficiency.csv` with **152 rows**
      - Wrote `output_data/subgroup_summary.csv` with **22 rows**
      - Wrote `output_data/school_consistency.csv` with **424 rows**
      - Wrote `output_data/consistency_class_summary.csv` with **10 rows**
      - Wrote `output_data/school_performance_index.csv` with **456 rows**
      - Wrote `output_data/performance_index_summary.csv` with **12 rows**
      - Wrote `output_data/school_sector_by_school.csv` with **251 rows**
      - Wrote `output_data/school_sector_proficiency.csv` with **48 rows**
      - Wrote `output_data/school_sector_summary.csv` with **8 rows**
      - Wrote `output_data/summary_report.xlsx` with **16 sheets**

5. **Schema / benchmark / workbook inspection**
   - Command: inspect regenerated outputs with Python/pandas and `openpyxl`
   - Result: ✅ Passed
   - Evidence:
      - `cohort_growth_detail.csv` contains Task 03 required columns plus Task 05 fields `p_value` and `significant`
      - `cohort_growth_summary.csv` contains `pct_significant_transitions`
      - `cohort_growth_pivot.xlsx` contains **6** sheets: `All Students Summary`, `Full Summary`, `All Students Detail`, `ELA Cohort Pivot`, `Math Cohort Pivot`, `Full Detail`
      - `summary_report.xlsx` contains **16** sheets: `Executive Summary`, `Top Growth (ELA)`, `Top Growth (Math)`, `Top Equity Schools`, `Proficiency Trends`, `School Directory`, `Geographic Equity`, `YoY Growth`, `COVID Recovery`, `School Trajectories`, `School Types`, `Grade Levels`, `Subgroups`, `Consistency`, `Performance Index`, `School Sectors`
      - Stuart-Hobson 2022→2023 benchmark rows for `Stuart-Hobson Middle School (Capitol Hill Cluster)` remain within ±0.1 pp:
        - ELA Gr6→Gr7: `33.5484% → 40.5405% (+6.9921 pp)`
        - ELA Gr7→Gr8: `36.2500% → 46.5753% (+10.3253 pp)`
        - Math Gr6→Gr7: `11.0390% → 14.6667% (+3.6277 pp)`
        - Math Gr7→Gr8: `13.7255% → 19.5804% (+5.8549 pp)`
      - `yoy_growth_detail.csv` contains the expected consecutive transitions only: `2016→2017`, `2017→2018`, `2018→2019`, `2022→2023`, `2023→2024`
      - `covid_recovery_summary.csv` keeps the documented recovery-status mix: `Partially Recovered` **75**, `Still Below Pre-COVID` **50**, `Exceeded Pre-COVID` **48**, `Fully Recovered` **23**, `No 2024 Data` **4**
      - `school_trajectory_classification.csv` still contains **424** rows (212 schools × 2 subjects) and the documented average trend slopes: ELA **+0.065 pp/yr**, Math **−0.656 pp/yr**
      - `school_type_by_school.csv` still contains **251** rows with the validated type mix: `Elementary` **147**, `High School` **39**, `Elementary-Middle` **31**, `Middle School` **28**, `Middle-High` **6**
      - `grade_level_summary.csv` still contains **14** rows (`7` grade levels × `2` subjects)
      - `subgroup_summary.csv` still contains **22** rows (`11` subgroups × `2` subjects)
      - `school_consistency.csv` contains **424** rows and `consistency_class_summary.csv` contains **10** rows
      - Consistency findings remain unchanged from loop 15:
        - ELA classes: `High-Consistent` **38**, `High-Volatile` **10**, `Low-Consistent` **10**, `Low-Volatile` **37**, `Insufficient Data` **117**
        - Math classes: `High-Consistent` **39**, `High-Volatile` **9**, `Low-Consistent` **9**, `Low-Volatile` **38**, `Insufficient Data` **117**
      - `school_performance_index.csv` contains **456** rows and `performance_index_summary.csv` contains **12** rows
      - Performance-index findings remain unchanged from loop 16:
        - ELA quintiles: `Q5 – Top Performers` **43**, `Q4 – Above Average` **42**, `Q3 – Middle` **42**, `Q2 – Below Average` **42**, `Q1 – Bottom Performers` **42**, `Insufficient Data` **17**
        - Math quintiles: `Q5 – Top Performers` **43**, `Q4 – Above Average` **42**, `Q3 – Middle` **42**, `Q2 – Below Average` **42**, `Q1 – Bottom Performers` **42**, `Insufficient Data` **17**
      - `school_sector_by_school.csv` contains **251** rows, `school_sector_proficiency.csv` contains **48** rows, and `school_sector_summary.csv` contains **8** rows
      - School-sector classification counts match the loop-17 build claims: `DCPS Traditional` **222**, `DCPS Specialized` **13**, `DCPS Alternative` **13**, `Charter` **3**
      - School-sector findings match the loop-17 build claims:
        - ELA: `DCPS Specialized` **50.3%** avg proficiency, `COVID impact −1.4 pp`, `recovery −1.8 pp`, `avg cohort growth +5.7 pp`
        - ELA: `DCPS Alternative` **13.1%** avg proficiency with strongest recovery `+7.6 pp`
        - ELA: `DCPS Traditional` **29.8%** avg proficiency, `COVID impact −4.2 pp`, `recovery +2.0 pp`
        - ELA: `Charter` **32.1%** avg proficiency across **3** schools with only 2022–2024 history
        - Math: `DCPS Specialized` **34.2%** avg proficiency, `COVID impact −16.8 pp`, `recovery +7.0 pp`
        - Math: `DCPS Traditional` **25.9%** avg proficiency, `COVID impact −8.3 pp`, `recovery +3.3 pp`
        - Math: `DCPS Alternative` **2.6%** avg proficiency
        - Math: `Charter` **13.5%** avg proficiency and `avg cohort growth −14.4 pp`

6. **Dashboard startup / endpoint / rendering smoke test**
   - Commands:
      - `python app/app_simple.py` (start server)
      - `GET http://127.0.0.1:8050/`
      - `GET http://127.0.0.1:8050/_dash-layout`
      - `GET http://127.0.0.1:8050/_dash-dependencies`
      - `python -c "import app.app_simple as m; m.update_figures('Math', 'All Students', None, [2022, 2024])"`
      - `chromium-browser --headless --no-sandbox --disable-gpu --window-size=1440,7000 --screenshot=/tmp/loop17-validate-dashboard.png http://127.0.0.1:8050/`
   - Result: ✅ Passed
   - Evidence:
      - App startup loaded regenerated CSVs without exceptions and exposed filters for **7 years**, **2 subjects**, **12 subgroups**, and **251 schools**
      - `GET /`, `GET /_dash-layout`, and `GET /_dash-dependencies` all returned **200**
      - `/_dash-dependencies` advertises a grouped **19-output** callback ending with the new `sector-comparison.figure` output
      - Direct callback invocation returned **19 outputs** total, including the populated sector chart:
        - `timeseries`: `Math - Percent Meeting/Exceeding Over Time`
        - `bars`: `Math - Year 2024: Top Schools`
        - `cohort-bars`: `Math – Avg Cohort Growth (pp)`
        - `cohort-detail`: `Math – Cohort Growth Distribution by Transition`
        - `map`: `Math - 2024: School Performance Map`
        - `equity-gaps`: `Math – Citywide Avg Proficiency Gap vs All Students`
        - `equity-gap-change`: `Math – Citywide Avg Gap Change (+ = narrowing)`
        - `heatmap`: `Math – Citywide Average: Grade × Year Proficiency (%)`
        - `scatter`: `Math – Baseline Proficiency vs. Cohort Growth (All Students)`
        - `geo-equity`: `Math – Average Proficiency & Cohort Growth by DC Quadrant`
        - `yoy-growth`: `Math – Citywide Same-Grade YoY Growth by Grade Level`
        - `covid-recovery`: `Math – COVID Impact (2019→2022) vs Recovery (2022→2024)`
        - `trajectory`: `Math – School Proficiency Trajectory (2016–2024)`
        - `school-type`: `Math – Citywide Avg Proficiency by School Type`
        - `grade-level`: `Math – Citywide Avg Proficiency by Grade Level`
        - `subgroup-trend`: `Math – Citywide Avg Proficiency by Student Subgroup`
        - `consistency`: `Math – School Performance Consistency`
        - `performance-index`: `Math – Multi-Metric School Performance Index`
        - `sector-comparison`: `Math – Avg Proficiency by School Program Sector`
      - Captured a headless dashboard screenshot at `/tmp/loop17-validate-dashboard.png` to confirm the dashboard page renders in this environment

## Acceptance-Criteria Status

- **Problem-statement validation requirements**
  - Validation steps were run or explicitly documented as blocked — ✅
  - `.squad/validation_report.md` records commands, evidence, blockers, and recommendation — ✅
  - `STATUS.md` records the outcome and next recommended phase — ✅
  - Validation evidence is written to `.squad/decisions.md` — ✅
  - Remaining blockers / follow-up work are explicit — ✅

- **Task 03 — Cohort growth analysis**
  - `python src/analyze_cohort_growth.py` exits with code 0 — ✅
  - `cohort_growth_detail.csv` exists with ≥ 4,500 rows and required columns — ✅ (`12,956` rows)
  - `cohort_growth_summary.csv` exists with ≥ 1,700 rows — ✅ (`2,560` rows)
  - `cohort_growth_pivot.xlsx` exists with ≥ 6 sheets — ✅ (`6` sheets)
  - Stuart-Hobson benchmark matches within ±0.1 pp — ✅

- **Task 04 — Interactive dashboard**
  - `python app/app_simple.py` starts without errors with regenerated CSV inputs — ✅
  - Dashboard callback returns at least five figures — ✅ (returns **19** analytical figures)
  - Subject / subgroup / school / year-range interaction path responds without server-side errors — ✅
  - Map view loads without errors when `input_data/school_locations.csv` is present — ✅
  - YoY growth chart is present in the callback output — ✅
  - COVID recovery chart is present in the callback output — ✅
  - School trajectory chart is present in the callback output — ✅
  - School type chart is present in the callback output — ✅
  - Grade-level chart is present in the callback output — ✅
  - Subgroup trend chart is present in the callback output — ✅
  - Consistency chart is present in the callback output — ✅
  - Performance-index chart is present in the callback output — ✅
  - School-sector chart is present in the callback output — ✅
  - No unhandled browser-console exceptions during manual interaction — ⚠️ **Blocked in this environment**

- **Task 05 + loop deliverables**
  - Significance columns remain present — ✅
  - Equity gap outputs regenerate — ✅
  - Rankings outputs regenerate — ✅
  - Proficiency trend output regenerates — ✅
  - Geographic equity outputs regenerate — ✅
  - YoY growth outputs regenerate — ✅
  - COVID recovery outputs regenerate — ✅
  - School trajectory outputs regenerate — ✅
  - School type outputs regenerate — ✅
  - Grade-level outputs regenerate — ✅
  - Subgroup outputs regenerate — ✅
  - Consistency outputs regenerate — ✅
  - Performance-index outputs regenerate — ✅
  - School-sector outputs regenerate — ✅
  - Formatted Excel summary report regenerates with 16 expected sheets — ✅

## Blocked Checks / Remaining Follow-up

- **Browser-console inspection is still blocked.** A Playwright navigation attempt failed with `Browser is already in use for /root/.cache/ms-playwright/mcp-chrome`, so this pass confirms server startup, Dash endpoints, callback/rendering behavior, dependency metadata, and a rendered Chromium screenshot instead of direct console inspection.
- **Original normalized-data backlog scope is still open.** The repo validates the reproducible 7-workbook wide-format path, but `src/load_clean_data.py` still depends on external normalized OSSE workbooks, including 2024-25, that are not committed here.
- **The school-sector deliverable is still a partial charter-vs.-DCPS proxy.** The in-repo wide-format files expose only **3** charter-coded schools, so a full comparison across charter management organizations still requires separate OSSE charter-school source files.
- **Closeout still needs to decide final handoff status.** This validate pass proves the current loop-17 sector-aware path is reproducible; Closeout must explicitly sign off or return the repo to Build for the remaining backlog scope.

## Conclusion

Validation passes for the current loop-17 wide-format pipeline. The documented smoke path is reproducible from a fresh clone, the new school-sector CSVs regenerate cleanly, the dashboard returns all nineteen analytical figures including the sector-comparison chart, and `summary_report.xlsx` is produced with all sixteen expected sheets. The next phase should be **Closeout**.
