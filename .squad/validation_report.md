# Validation Report

**Date:** 2026-04-27  
**Reviewer:** Ralph  
**Recommendation:** **PASS — advance loop 4 to Closeout**

## Scope

Validate the latest build output against the current sprint commitments for loop 4: the expanded 7-workbook wide-format ingestion path, regenerated cohort/significance outputs, equity-gap and rankings deliverables, and the dashboard HTTP/callback path using the refreshed CSVs.

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

4. **Wide-format pipeline smoke test**
   - Commands:
     - `python src/load_wide_format_data.py`
     - `python src/analyze_cohort_growth.py`
     - `python src/equity_gap_analysis.py`
     - `python src/generate_school_rankings.py`
   - Result: ✅ Passed
   - Evidence:
     - Loaded **7** in-repo workbooks covering school years **2016, 2017, 2018, 2019, 2022, 2023, 2024**
     - Wrote `output_data/combined_all_years.csv` with **28,069 rows**
     - Wrote `output_data/processing_report.txt`
     - Wrote `output_data/cohort_growth_detail.csv` with **12,956 rows**
     - Wrote `output_data/cohort_growth_summary.csv` with **2,560 rows**
     - Wrote `output_data/cohort_growth_pivot.xlsx` with **6 sheets**
     - Wrote `output_data/equity_gap_detail.csv` with **13,008 rows**
     - Wrote `output_data/equity_gap_summary.csv` with **2,138 rows**
     - Wrote `output_data/school_rankings.csv` with **422 rows**
     - Wrote `output_data/school_equity_rankings.csv` with **414 rows**

5. **Schema / benchmark inspection**
   - Command: inspect regenerated outputs with Python/pandas
   - Result: ✅ Passed
   - Evidence:
     - `cohort_growth_detail.csv` contains Task 05 fields `p_value` and `significant`
     - `cohort_growth_summary.csv` contains `pct_significant_transitions`
     - `equity_gap_detail.csv` contains `proficiency_gap`, `followup_gap`, `gap_change`, `growth_gap`, and `is_disadvantaged`
     - Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp:
       - ELA Gr6→Gr7: `33.5484% → 40.5405% (+6.9921 pp)`
       - ELA Gr7→Gr8: `36.2500% → 46.5753% (+10.3253 pp)`
       - Math Gr6→Gr7: `11.0390% → 14.6667% (+3.6277 pp)`
       - Math Gr7→Gr8: `13.7255% → 19.5804% (+5.8549 pp)`

6. **Dashboard startup / endpoint / callback smoke test**
   - Commands:
     - `python app/app_simple.py` (start server)
     - `GET http://127.0.0.1:8050/`
     - `GET http://127.0.0.1:8050/_dash-layout`
     - `GET http://127.0.0.1:8050/_dash-dependencies`
     - `POST http://127.0.0.1:8050/_dash-update-component`
   - Result: ✅ Passed
   - Evidence:
     - App startup loaded the regenerated CSVs without exceptions and exposed filters for **7 years**, **2 subjects**, **12 subgroups**, and **251 schools**
     - `GET /`, `GET /_dash-layout`, and `GET /_dash-dependencies` all returned **200**
     - `/_dash-dependencies` advertised the expected **7-output** callback
     - A live callback request returned all seven figures:
       - `timeseries`: `Math - Percent Meeting/Exceeding Over Time`
       - `bars`: `Math - Year 2024: Top Schools`
       - `cohort-bars`: `Math – Avg Cohort Growth (pp)`
       - `cohort-detail`: `Math – Cohort Growth by Transition`
       - `map`: `Math - 2024: School Performance Map`
       - `equity-gaps`: `Math – Proficiency Gap vs All Students`
       - `equity-gap-change`: `Math – Gap Change (+ = narrowing)`
     - With `input_data/school_locations.csv` present, the current 2024 Math / All Students map view would plot **113 schools**

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
  - Dashboard callback returns at least five figures — ✅ (returns **7**)
  - Subject / subgroup / school / year-range interaction path responds without server-side errors — ✅
  - Map view loads with `input_data/school_locations.csv` present — ✅
  - No unhandled browser-console exceptions during manual interaction — ⚠️ **Blocked in this environment**

- **Task 05 + loop deliverables**
  - Significance columns remain present — ✅
  - Equity gap outputs regenerate — ✅
  - Rankings outputs regenerate — ✅

## Blocked Checks / Remaining Follow-up

- **Browser-console inspection is still blocked.** Playwright could not open a browser session because the browser profile was already locked (`Browser is already in use for /root/.cache/ms-playwright/mcp-chrome`).
- **Original normalized-data backlog scope is still open.** The repo now validates the 7-workbook wide-format path, but `src/load_clean_data.py` still depends on external normalized OSSE workbooks, including 2024-25, that are not committed here.
- **Closeout still needs to decide final loop status.** This validate pass proves the current wide-format loop is reproducible; Closeout must explicitly sign off or return the repo to Build for the remaining scope.

## Conclusion

Validation passes for the current loop-4 wide-format pipeline. The documented smoke path is reproducible from a fresh clone, the expanded historical-data outputs regenerate cleanly, Task 03's summary-row threshold is now met, and the dashboard serves all seven figures with a real map when school locations are present. The next phase should be **Closeout**.
