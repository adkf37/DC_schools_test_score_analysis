# Task 04 — Interactive Dashboard

## Summary
Verify and enhance the Dash dashboard (`app/app_simple.py`) so it correctly loads both same-grade and cohort growth data and renders all five chart types without errors.

## Owner
Data Engineer

## Phase
Build (Phase 3)

## Acceptance Criteria
- [ ] `python app/app_simple.py` starts without errors when `combined_all_years.csv`, `cohort_growth_detail.csv`, and `cohort_growth_summary.csv` are present.
- [ ] Dashboard renders five output figures: time-series chart, cohort bar chart, cohort box/grouped-bar plot, and at least two additional views.
- [ ] Subject, student-group, school, and year-range filters work correctly in all chart tabs.
- [ ] Map view loads without errors when `input_data/school_locations.csv` is present (gracefully skips map if file is absent).
- [ ] No unhandled exceptions in the browser console during normal interaction.

## Steps
1. Ensure Tasks 01–03 are complete so all CSV inputs exist.
2. Install dashboard dependencies: `pip install dash plotly`.
3. Run `python app/app_simple.py` and open `http://127.0.0.1:8050/` in a browser.
4. Exercise each filter control and verify charts update correctly.
5. (Optional) Add `input_data/school_locations.csv` and confirm map view renders.
6. Fix any `KeyError` or `AttributeError` exceptions encountered during testing.

## Dependencies
- Tasks 01–03 must be complete.
- `pip install dash plotly` (in addition to base `requirements.txt`).
- `app/app_simple.py` — main dashboard script.

## Notes
- Dashboard dependencies (`dash`, `plotly`) are optional and are separated from the core analysis pipeline dependencies. They do not need to be in `requirements.txt` unless the project decides to require the dashboard.
- If the school-locations CSV is absent, the map tab should display a friendly "data not available" message rather than crashing.
