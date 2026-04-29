# Validation Report

**Date:** 2026-04-29  
**Reviewer:** Ralph  
**Recommendation:** **PASS — advance loop 8 to Closeout**

## Scope

Validate the latest build output against the current sprint commitments for loop 8: the 7-workbook wide-format ingestion path, regenerated cohort/significance/equity/rankings/proficiency-trend outputs, the new geographic-equity outputs, the 7-sheet policy summary workbook, and the dashboard HTTP/callback path with the new 10-figure experience.

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
     - Wrote `output_data/summary_report.xlsx` with **7 sheets**

5. **Schema / benchmark / workbook inspection**
   - Command: inspect regenerated outputs with Python/pandas and `openpyxl`
   - Result: ✅ Passed
   - Evidence:
     - `cohort_growth_detail.csv` contains Task 03 required columns plus Task 05 fields `p_value` and `significant`
     - `cohort_growth_summary.csv` contains `pct_significant_transitions`
     - `cohort_growth_pivot.xlsx` contains **6** sheets: `All Students Summary`, `Full Summary`, `All Students Detail`, `ELA Cohort Pivot`, `Math Cohort Pivot`, `Full Detail`
     - `summary_report.xlsx` contains **7** sheets: `Executive Summary`, `Top Growth (ELA)`, `Top Growth (Math)`, `Top Equity Schools`, `Proficiency Trends`, `School Directory`, `Geographic Equity`
     - Stuart-Hobson 2022→2023 benchmark rows for `Stuart-Hobson Middle School (Capitol Hill Cluster)` remain within ±0.1 pp:
       - ELA Gr6→Gr7: `33.5484% → 40.5405% (+6.9921 pp)`
       - ELA Gr7→Gr8: `36.2500% → 46.5753% (+10.3253 pp)`
       - Math Gr6→Gr7: `11.0390% → 14.6667% (+3.6277 pp)`
       - Math Gr7→Gr8: `13.7255% → 19.5804% (+5.8549 pp)`
     - `geographic_equity_by_quadrant.csv` confirms the loop-8 quadrant findings:
       - ELA: NW `42.71%` avg proficiency / `+4.85 pp` avg growth vs. NE `24.09%` / `+3.13 pp` and SE `20.15%` / `+4.51 pp`
       - Math: NW `38.41%` avg proficiency vs. NE `15.29%` and SE `16.18%`

6. **Dashboard startup / endpoint / callback smoke test**
   - Commands:
     - `python app/app_simple.py` (start server)
     - `GET http://127.0.0.1:8050/`
     - `GET http://127.0.0.1:8050/_dash-layout`
     - `GET http://127.0.0.1:8050/_dash-dependencies`
     - `POST http://127.0.0.1:8050/_dash-update-component`
   - Result: ✅ Passed
   - Evidence:
     - App startup loaded regenerated CSVs without exceptions and exposed filters for **7 years**, **2 subjects**, **12 subgroups**, and **251 schools**
     - `GET /`, `GET /_dash-layout`, and `GET /_dash-dependencies` all returned **200**
     - `/_dash-dependencies` advertised the expected **10-output** callback
     - A live callback request returned all ten figures:
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
  - Dashboard callback returns at least five figures — ✅ (returns **10**)
  - Subject / subgroup / school / year-range interaction path responds without server-side errors — ✅
  - Map view loads without errors when `input_data/school_locations.csv` is present — ✅
  - Geographic-equity chart is present in the callback output — ✅
  - No unhandled browser-console exceptions during manual interaction — ⚠️ **Blocked in this environment**

- **Task 05 + loop deliverables**
  - Significance columns remain present — ✅
  - Equity gap outputs regenerate — ✅
  - Rankings outputs regenerate — ✅
  - Proficiency trend output regenerates — ✅
  - Geographic equity outputs regenerate — ✅
  - Formatted Excel summary report regenerates with 7 expected sheets — ✅

## Blocked Checks / Remaining Follow-up

- **Browser-console inspection is still blocked.** This validation pass confirmed server startup, Dash endpoints, and a live 10-figure callback response, but it did not produce direct browser-console evidence from an interactive session in this sandbox.
- **Original normalized-data backlog scope is still open.** The repo validates the reproducible 7-workbook wide-format path, but `src/load_clean_data.py` still depends on external normalized OSSE workbooks, including 2024-25, that are not committed here.
- **Closeout still needs to decide final project handoff status.** This validate pass proves the current loop-8 geographic-equity path is reproducible; Closeout must explicitly sign off or return the repo to Build for remaining backlog scope.

## Conclusion

Validation passes for the current loop-8 wide-format pipeline. The documented smoke path is reproducible from a fresh clone, the analytical outputs regenerate cleanly, the new geographic-equity CSVs and dashboard figure are present, and `summary_report.xlsx` is produced with all seven expected sheets. The next phase should be **Closeout**.
