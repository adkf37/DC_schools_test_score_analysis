# Validation Report

**Date:** 2026-04-25  
**Reviewer:** Ralph  
**Recommendation:** **PASS — advance the current equity-aware wide-format loop to Closeout**

## Scope

Validate the latest build output against the repo's current commitments: the reproducible wide-format ingestion path, cohort-growth/significance outputs, the loop-2 equity gap outputs documented in `STATUS.md` / `.squad/decisions.md`, and the dashboard startup/rendering path using the regenerated CSVs.

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

4. **Wide-format data pipeline smoke test**
   - Command: `python src/load_wide_format_data.py`
   - Result: ✅ Passed
   - Evidence:
     - Detected and loaded 3 in-repo wide-format workbooks:
       - `input_data/School and Demographic Group Aggregation/DC PARCC Scores – School Year 2021-22.xlsx`
       - `input_data/School and Demographic Group Aggregation/DC PARCC Scores – School Year 2022-23.xlsx`
       - `input_data/School and Demographic Group Aggregation/DC Cape Scores 2023-2024.xlsx`
     - Wrote `output_data/combined_all_years.csv` with **12,378 rows**
     - Wrote `output_data/processing_report.txt`

5. **Cohort analysis smoke test**
   - Command: `python src/analyze_cohort_growth.py`
   - Result: ✅ Passed
   - Evidence:
     - Wrote `output_data/cohort_growth_detail.csv` with **5,391 rows**
     - Wrote `output_data/cohort_growth_summary.csv` with **1,234 rows**
     - Wrote `output_data/cohort_growth_pivot.xlsx` with **6 sheets**

6. **Equity gap analysis smoke test**
   - Command: `python src/equity_gap_analysis.py`
   - Result: ✅ Passed
   - Evidence:
     - Wrote `output_data/equity_gap_detail.csv` with **5,977 rows**
     - Wrote `output_data/equity_gap_summary.csv` with **1,042 rows**
     - Citywide summary output printed subgroup proficiency-gap / growth-gap metrics for both ELA and Math

7. **Output schema / benchmark inspection**
   - Command: inspect regenerated CSV schemas, workbook sheets, and Stuart-Hobson benchmark rows
   - Result: ✅ Passed
   - Evidence:
     - `cohort_growth_detail.csv` contains the Task 03 fields plus Task 05 fields `p_value` and `significant`
     - `cohort_growth_summary.csv` contains Task 05 field `pct_significant_transitions`
     - `equity_gap_detail.csv` contains `proficiency_gap`, `followup_gap`, `gap_change`, `growth_gap`, and `is_disadvantaged`
     - `equity_gap_summary.csv` contains `avg_proficiency_gap`, `avg_followup_gap`, `avg_gap_change`, `avg_growth_gap`, `n_transitions`, and `pct_narrowing`
     - `cohort_growth_pivot.xlsx` was regenerated with **6 sheets**
     - Stuart-Hobson 2022→2023 transitions remained within ±0.1 pp:
       - ELA Gr6→Gr7: `33.5% → 40.5% (+7.0 pp)`; max absolute deviation from target = **0.048 pp**
       - ELA Gr7→Gr8: `36.2% → 46.6% (+10.3 pp)`; max absolute deviation from target = **0.050 pp**
       - Math Gr6→Gr7: `11.0% → 14.7% (+3.6 pp)`; max absolute deviation from target = **0.039 pp**
       - Math Gr7→Gr8: `13.7% → 19.6% (+5.9 pp)`; max absolute deviation from target = **0.045 pp**

8. **Dashboard startup / rendering smoke test**
   - Commands:
     - `python app/app_simple.py` (start server)
     - `GET http://127.0.0.1:8050/`
     - `GET http://127.0.0.1:8050/_dash-layout`
     - `GET http://127.0.0.1:8050/_dash-dependencies`
     - `POST http://127.0.0.1:8050/_dash-update-component`
   - Result: ✅ Passed
   - Evidence:
     - App startup loaded the regenerated CSVs without exceptions and exposed filters for **3 years**, **2 subjects**, **11 subgroups**, and **116 schools**
     - `/_dash-dependencies` advertised **7 callback outputs**
     - Dash callback returned **all seven figures** for a live interaction (`Math`, `All Students`, Stuart-Hobson, 2022–2024):
       - `timeseries`: `Math - Percent Meeting/Exceeding Over Time`
       - `bars`: `Math - Year 2024: Top Schools`
       - `cohort-bars`: `Math – Avg Cohort Growth (pp)`
       - `cohort-detail`: `Math – Cohort Growth by Transition`
       - `map`: `Add school_locations.csv to enable mapping`
       - `equity-gaps`: `Math – Proficiency Gap vs All Students`
       - `equity-gap-change`: `Math – Gap Change (+ = narrowing)`
     - The map view degraded gracefully without `input_data/school_locations.csv`

## Acceptance-Criteria Status

- **Task 03**
  - `python src/analyze_cohort_growth.py` exits with code 0 — ✅
  - `cohort_growth_detail.csv` exists with ≥ 4,500 rows and required columns — ✅ (`5,391` rows)
  - `cohort_growth_summary.csv` exists — ✅
  - `cohort_growth_summary.csv` has ≥ 1,700 rows — ⚠️ **Not met** (`1,234` rows)
  - `cohort_growth_pivot.xlsx` exists with ≥ 6 sheets — ✅ (`6` sheets)
  - Stuart-Hobson benchmark matches within ±0.1 pp — ✅

- **Task 04**
  - `python app/app_simple.py` starts without errors with regenerated CSV inputs — ✅
  - Dashboard baseline requirement of five figures is satisfied — ✅
  - Current loop's expanded seven-figure callback path is validated — ✅
  - Subject / student-group / school / year-range interaction path responds without server-side errors — ✅
  - Map view handles missing locations file gracefully — ✅
  - No unhandled browser-console exceptions during manual browser interaction — ⚠️ **Blocked in this environment**

- **Task 05**
  - Two-proportion significance output present in detail rows — ✅
  - `pct_significant_transitions` present in summary output — ✅
  - Methods note exists (`docs/methods.md`) — ✅
  - Task 03 runtime / benchmark checks still pass — ✅ with the summary-row limitation noted above

- **Loop 2 equity gap deliverable**
  - `python src/equity_gap_analysis.py` exits with code 0 — ✅
  - `equity_gap_detail.csv` exists and includes the documented gap fields — ✅
  - `equity_gap_summary.csv` exists and includes aggregate gap metrics — ✅
  - Dashboard exposes the two additional equity figures — ✅

## Blocked Checks / Remaining Gaps

- **Direct browser-console inspection is blocked by the environment.** Playwright could not open a browser session because the browser profile was already locked. Dashboard startup and callback responses passed, and no server-side exceptions were observed.
- **Original full-data backlog targets remain only partially satisfied.** The repo contains 3 in-repo wide-format workbooks (2021-22 through 2023-24 school years), not the full 4-year normalized OSSE set described in the oldest Task 01 acceptance criteria.
- **Summary-row target remains below the original 1,700-row threshold.** The current output is `1,234` rows; the repo docs attribute the shortfall to the absent 2024-25 source plus OSSE subgroup suppression.

## Conclusion

Validation succeeds for the **current equity-aware wide-format loop**. The documented smoke path is reproducible from a fresh clone, the analytical outputs regenerate cleanly, the new equity outputs are present, and the dashboard serves all seven figure payloads for a live callback request. The remaining issues are explicit scope limitations or environment-blocked inspection steps, so the next phase should be **Closeout**.
