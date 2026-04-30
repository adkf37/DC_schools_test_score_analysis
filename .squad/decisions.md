# Squad Decisions

## Active Decisions

### D-001 — Use Grade of Enrollment for Cohort Assignment
**Date:** 2026-04-25  
**Decision:** The cohort engine (`analyze_cohort_growth.py`) uses **Grade of Enrollment** (not Tested Grade/Subject) for cohort assignment.  
**Rationale:** Middle-school math cohorts can include students taking Algebra I or Pre-Algebra; using Tested Grade would split the cohort. Grade of Enrollment keeps the full enrolled cohort together.  
**Consequences:** Rows where `Tested Grade/Subject == "All"` are preferred over subject-specific sub-rows to avoid subset bias.

### D-002 — Minimum N = 10 for Cohort Transitions
**Date:** 2026-04-25  
**Decision:** Cohort transitions with fewer than 10 students in either the baseline or follow-up are excluded.  
**Rationale:** Small-sample percentages are noisy and can mislead policy decisions. OSSE itself suppresses cells with N < 10.  
**Consequences:** Some small schools or subgroups will have no cohort-growth values. This is expected and documented.

### D-003 — Suppressed Values Treatment
**Date:** 2026-04-25  
**Decision:** Cells marked `DS`, `N<10`, `<5%`, `>95%`, or similar OSSE suppression codes are treated as `NaN` and excluded from all growth calculations.  
**Rationale:** Re-identifying individual students from suppressed values would violate OSSE's data-use policy.  
**Consequences:** Suppressed-value rows are dropped; the processing report counts them.

### D-004 — Stuart-Hobson as Primary Validation Benchmark
**Date:** 2026-04-25  
**Decision:** The four manually computed Stuart-Hobson transitions (ELA/Math Gr6→Gr7 and Gr7→Gr8, 2022→2023) serve as the primary regression benchmark. All pipeline changes must preserve these within ±0.1 pp.  
**Rationale:** The manual spreadsheet (`StuartHobson_Manual_Growth_example.xlsx`) was independently verified and represents the gold-standard expectation.  
**Consequences:** Any pipeline refactor that shifts these values by >0.1 pp must be investigated and justified before merging.

### D-005 — Python Stack & Dependency Constraints
**Date:** 2026-04-25  
**Decision:** Python ≥ 3.9, pandas, openpyxl, Dash, and scipy are the approved dependencies. No additional ML or heavy-compute libraries without Lead approval.  
**Rationale:** Keeps the environment lightweight and reproducible for policy researchers who may run this on modest hardware.  
**Consequences:** Statistical tests are limited to classical frequentist tests available in scipy.

### D-006 — Two-Proportion Z-Test for Significance (Task 05)
**Date:** 2026-04-25  
**Decision:** A pooled two-proportion z-test (two-tailed, α = 0.05) is used to assess whether a cohort's proficiency rate changed significantly between baseline and follow-up. The test uses `scipy.stats.norm` to compute the p-value from the pooled z-statistic.  
**Rationale:** The z-test is the standard method for comparing two independent proportions when sample sizes are large enough. It is interpretable, reproducible, and available in scipy without additional dependencies.  
**Consequences:**  
- `cohort_growth_detail.csv` gains `p_value` (rounded to 4 dp) and `significant` (bool) columns.  
- `cohort_growth_summary.csv` gains `pct_significant_transitions` (% of transitions with p < 0.05).  
- No multiple-comparison correction is applied by default; `significant` is a screening flag, not a family-wise claim. See `docs/methods.md` for details.  
- Small school cohorts (N ≈ 145) have low power; a 7pp change at 33% baseline requires N ≈ 366 per group for significance. City-wide aggregations will see more significant results.  
- Proficient counts are reconstructed as `round(pct / 100 × total_count)` because OSSE files report percentages and totals but not always raw proficiency counts.

### D-007 — Validate returns to Build on input-file contract mismatch
**Date:** 2026-04-25  
**Decision:** Do not advance to Closeout. Return the repo to Build because the Validate smoke checks failed before any analytical outputs were generated.  
**Rationale:** After installing `requirements.txt`, `python -m py_compile src/*.py app/*.py inspect_data.py` passed. However, `python src/load_clean_data.py` searched only for four exact workbook names in the top-level `input_data/` directory and failed with file-not-found errors for all of them. The repo snapshot instead contains differently named workbooks under `input_data/School and Demographic Group Aggregation/`, and no exact match for the expected 2024-25 workbook was present. `python src/analyze_cohort_growth.py` then failed because `output_data/combined_all_years.csv` did not exist.  
**Consequences:** Task 03 and Task 05 acceptance criteria remain unmet in validation: the required cohort CSV/XLSX outputs were not produced, the Stuart-Hobson benchmark could not be checked, and significance output columns could not be verified on generated data. The next Build step is to align loader input discovery (or data placement/filenames), regenerate `combined_all_years.csv`, and rerun validation.

### D-008 — Closeout does not sign off; handoff returns to Build
**Date:** 2026-04-25  
**Decision:** Closeout for this loop records the project state and returns the repo to **Build** instead of approving final handoff.  
**Rationale:** Closeout rechecked the backlog, sprint, validation report, README/WORKFLOW handoff docs, and the documented smoke commands from a fresh clone. The same blocker remained: dependencies and syntax checks pass, but `src/load_clean_data.py` fails on a hardcoded input-file contract mismatch, so `output_data/combined_all_years.csv` and all downstream cohort outputs still cannot be regenerated.  
**Consequences:** `STATUS.md`, `README.md`, and `WORKFLOW.md` must describe the repo as blocked rather than handoff-ready; `.squad/review_report.md` becomes the authoritative closeout record; and the next loop must focus on fixing the loader/data contract before any further signoff attempt.



### D-009 — Wide-Format Alternative Loader to Unblock Pipeline
**Date:** 2026-04-25  
**Decision:** Implement `src/load_wide_format_data.py` as an alternative data ingestion script that reads the "School and Demographic Group Aggregation" wide-format OSSE workbooks already committed to the repository.  
**Rationale:** `src/load_clean_data.py` was designed for a normalized long-format schema that requires four specific OSSE workbooks not available in the repo (and not downloadable automatically). The wide-format files (2021-22, 2022-23, 2023-24 PARCC/DCCAPE) are already in `input_data/School and Demographic Group Aggregation/` and contain the same data in a different layout (wide: ELA+Math side-by-side, separate sheets per demographic group). The alternative loader uses dynamic column-name detection to handle the extra "Subgroup" column present in demographic (non-Overall) sheets.  
**Consequences:**  
- The pipeline can now run end-to-end from a fresh clone without downloading additional files.  
- Output uses placeholder `LEA Code = "0"` and `LEA Name = "DC Schools"` because the wide-format files do not include LEA metadata.  
- `cohort_growth_summary.csv` has 1,234 rows (vs. Task 03 target of ≥ 1,700) because only 3 years of data are available (no 2024-25) and OSSE suppresses small demographic cells.  
- All four Stuart-Hobson benchmark transitions pass within ±0.1 pp (D-004 constraint satisfied).  
- The normalized `load_clean_data.py` remains the preferred path when the full OSSE download set is available.

### D-010 — Validate Passes the Wide-Format Loop and Advances to Closeout
**Date:** 2026-04-25
**Decision:** Mark the current Validate pass as successful for the repo's documented wide-format pipeline and move the project to **Closeout** for this loop.
**Rationale:** Re-running the documented smoke path from a fresh clone succeeded: `python -m pip install -r requirements.txt`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, and `python src/analyze_cohort_growth.py` all exited 0. The run regenerated `combined_all_years.csv` (12,378 rows), `cohort_growth_detail.csv` (5,391 rows), `cohort_growth_summary.csv` (1,234 rows), and `cohort_growth_pivot.xlsx` (6 sheets); `cohort_growth_detail.csv` contains `p_value` and `significant`, `cohort_growth_summary.csv` contains `pct_significant_transitions`, and all four Stuart-Hobson benchmark transitions remained within ±0.1 pp of the manual targets.
**Consequences:**
- `.squad/validation_report.md` is now the authoritative validation evidence for the wide-format pipeline path.
- Closeout should describe the current loop as validated, while still calling out unresolved scope gaps: Task 04 dashboard work is pending, the repo still lacks a committed 2024-25 source workbook, and the original Task 03 summary target (≥ 1,700 rows) is not met because only 3 years of data are available and OSSE suppresses small subgroup cells.
- Any future validation of the full normalized-data path must be treated as a separate loop once the complete OSSE source set is available.

### D-011 — Closeout Signs Off the Wide-Format Loop and Returns the Repo to Build
**Date:** 2026-04-25
**Decision:** Closeout approves handoff for the **current wide-format loop** and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** A fresh-clone closeout re-run confirmed the documented smoke path succeeds: `python -m pip install -r requirements.txt`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, and `python src/analyze_cohort_growth.py` all exit 0. The run regenerated the expected outputs, preserved the Stuart-Hobson benchmark within ±0.1 pp, and kept the Task 05 significance fields. However, Task 04 dashboard work remains pending, the normalized 4-workbook OSSE path still depends on external data, and the original ≥ 1,700 summary-row target is still limited by missing 2024-25 data plus subgroup suppression.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe the repo as handoff-ready for the verified three-year wide-format path while clearly listing the remaining gaps.
- `.squad/review_report.md` becomes the authoritative closeout record for this loop and should explicitly recommend returning to **Build** next.
- The next Build loop must choose between dashboard validation work and the missing normalized-data / 2024-25 ingestion path before another Validate/Closeout cycle.

### D-012 — Fix Dashboard API Compatibility for Dash 4.x and Plotly 6.x
**Date:** 2026-04-25
**Decision:** Update `app/app_simple.py` and `app/app.py` to replace deprecated/removed APIs: `app.run_server()` → `app.run()`, and `px.scatter_mapbox` → `px.scatter_map` with `map_style='open-street-map'`.
**Rationale:** Dash 4.x removed `app.run_server()` (replaced by `app.run()`). Plotly 6.x deprecated `px.scatter_mapbox` in favour of `px.scatter_map` (the new MapLibre-based renderer that does not require a Mapbox API token). Without these fixes the dashboard raises an `ObsoleteAttributeException` at startup and produces `DeprecationWarning` at runtime, preventing Task 04 acceptance criteria from being met.
**Consequences:**
- `python app/app_simple.py` now starts without errors and serves all 5 required figures (timeseries, bar, cohort-bar, cohort-detail, map).
- The map placeholder renders correctly (open-street-map tile layer) when `school_locations.csv` is absent.
- Both `app/app.py` and `app/app_simple.py` are updated; `app.py` is the legacy entry point and `app_simple.py` is the current primary dashboard.
- `dash>=2.0.0` and `plotly>=5.0.0` version pins remain commented out in `requirements.txt` (dashboard is still an optional dependency per D-005); users must `pip install dash plotly` separately.

### D-013 — Validate Passes the Dashboard-Aware Wide-Format Loop
**Date:** 2026-04-25
**Decision:** Mark the current Validate pass as successful and advance the repo to **Closeout** for the latest wide-format loop, now including dashboard startup/rendering evidence in addition to the core analytical smoke tests.
**Rationale:** Re-running the repo checks succeeded end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, and `python src/analyze_cohort_growth.py` all exited 0. `python app/app_simple.py` also started successfully against the regenerated outputs, and a live `/_dash-update-component` request returned all five figures while the map view degraded gracefully without `school_locations.csv`. Direct browser-console inspection was blocked because the Playwright browser profile was locked in this environment, but no server-side exceptions were observed while serving the dashboard requests.
**Consequences:**
- `.squad/validation_report.md` is the authoritative validation record for this loop and now includes Task 04 evidence.
- `STATUS.md` should move the project to **Validate complete / Closeout next** rather than reporting closeout as already finished for the current loop.
- Closeout should focus on the remaining explicit limitations: missing normalized 4-workbook / 2024-25 data, the 1,234-row summary output versus the original ≥ 1,700 target, and the environment-blocked browser-console check.

### D-015 — Equity Gap Analysis as Build Loop 2 Deliverable
**Date:** 2026-04-25
**Decision:** Implement `src/equity_gap_analysis.py` to compute proficiency gaps and growth gaps by student subgroup, and extend the dashboard to display two new equity charts.
**Rationale:** All five original backlog tasks were complete. The next Build iteration needed a concrete deliverable that advances an explicitly stated project goal: "surfacing equity gaps (achievement growth by race/ethnicity and other subgroups)" (backlog/README.md). An equity gap analysis script was the most impactful and self-contained addition: it reads the already-produced `cohort_growth_detail.csv`, produces two new CSVs (`equity_gap_detail.csv`, `equity_gap_summary.csv`), and extends the dashboard from 5 to 7 figures.
**Consequences:**
- `src/equity_gap_analysis.py` is a new standalone script; run it after `analyze_cohort_growth.py`.
- New output files: `equity_gap_detail.csv` (5,977 rows) and `equity_gap_summary.csv` (1,042 rows).
- Dashboard callback now returns 7 figures; validated via POST `/_dash-update-component`.
- `docs/methods.md` documents the gap metrics (proficiency_gap, followup_gap, gap_change, growth_gap, is_disadvantaged).
- Smoke test commands updated to include `python src/equity_gap_analysis.py`.

### D-016 — Validate Passes the Equity-Aware Wide-Format Loop
**Date:** 2026-04-25
**Decision:** Mark the current Validate pass as successful and advance the repo to **Closeout** for the latest equity-aware wide-format loop.
**Rationale:** Re-running the documented smoke path succeeded end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, and `python src/equity_gap_analysis.py` all exited 0. `python app/app_simple.py` also started successfully against the regenerated outputs, `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200, and a live `POST /_dash-update-component` request returned all seven figures (including the two new equity charts). Direct browser-console inspection remained blocked because the Playwright browser profile was locked in this environment, but no server-side exceptions were observed while serving the dashboard requests.
**Consequences:**
- `.squad/validation_report.md` is the authoritative validation record for the current loop and now includes equity-output evidence.
- `STATUS.md` should move the project to **Validate complete / Closeout next** for loop 2.
- Closeout should focus on the remaining explicit limitations: the missing normalized 4-workbook / 2024-25 data path, the 1,234-row summary output versus the original ≥ 1,700 target, and the environment-blocked browser-console/manual locations-file checks.

### D-017 — Closeout Signs Off the Equity-Aware Wide-Format Loop and Returns to Build
**Date:** 2026-04-26
**Decision:** Closeout approves handoff for the current equity-aware wide-format loop and returns the repo to **Build** rather than marking the full project complete.
**Rationale:** A fresh-clone closeout re-run succeeded end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, and `python src/equity_gap_analysis.py` all exited 0. `python app/app_simple.py` also started successfully, `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200, and a live `POST /_dash-update-component` request returned all seven figures for the regenerated outputs. The repo is therefore handoff-ready for the current 3-year wide-format + equity path, but it still lacks the normalized 4-workbook / 2024-25 data path, still falls short of the original ≥ 1,700 summary-row target, and still has environment-blocked dashboard follow-up checks (browser console and optional locations file).
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 2 while explicitly sending the repo back to **Build**.
- `.squad/review_report.md` becomes the authoritative closeout record for the equity-aware loop.
- The next Build loop must choose between restoring the normalized-data / 2024-25 path or finishing the remaining manual dashboard checks before another Validate/Closeout pass.

### D-018 — Build Loop 3: School Locations and Rankings Deliverables
**Date:** 2026-04-26
**Decision:** Build loop 3 targets two deliverables: (a) `input_data/school_locations.csv` with geocoordinates for 115 DC public schools, and (b) `src/generate_school_rankings.py` that ranks all schools by cohort growth and equity-gap narrowing.
**Rationale:**
- The `school_locations.csv` file directly satisfies Task 04's acceptance criterion: "Map view loads without errors when `input_data/school_locations.csv` is present." In all prior loops, the map degraded gracefully but never fully rendered because this file was absent. Adding it completes Task 04.
- The school rankings script fulfills the explicit backlog goal ("ranking schools by cohort growth") that remained unimplemented after loop 2. It reads already-generated outputs (no new data pipeline changes), making it a low-risk, high-value addition.
- The normalized 4-workbook / 2024-25 ingestion path is still blocked by missing external OSSE data and is deferred.
**Consequences:**
- `input_data/school_locations.csv` contains approximate coordinates based on DC neighborhood geography. They are accurate enough for exploratory dashboard mapping; for precise geocoding, the DC Open Data API (`https://opendata.dc.gov/`) should be used in a future loop.
- "DC Public Schools" (citywide aggregate row in `combined_all_years.csv`) has no entry in `school_locations.csv` because it is not a physical location. The dashboard map will omit this row, which is the correct behavior.
- `school_rankings.csv` (192 rows) and `school_equity_rankings.csv` (187 rows) become new policy-analysis artifacts. Rankings are based on the 3-year wide-format dataset and inherit the same limitations (missing 2024-25, OSSE subgroup suppression).
- Updated smoke test path adds: `python src/generate_school_rankings.py`.
- Validate loop 3 should confirm: `py_compile src/*.py`, `generate_school_rankings.py` exits 0, and the dashboard map renders data points for the new locations file.

### D-019 — Closeout Signs Off the Rankings-and-Map Wide-Format Loop and Returns to Build
**Date:** 2026-04-27
**Decision:** Closeout approves handoff for the current loop-3 wide-format path, including the school-rankings outputs and the locations-backed dashboard map, and returns the repo to **Build** rather than marking the full project complete.
**Rationale:** A fresh-clone closeout re-run succeeded end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, and `python src/generate_school_rankings.py` all exited 0. `python app/app_simple.py` also started successfully, `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200, and a live `POST /_dash-update-component` request returned all seven figures with a real map once `input_data/school_locations.csv` was present. The current 2024 All Students map plots 113 schools; `DC Public Schools` is correctly omitted because it is a citywide aggregate row without a physical location. The repo is therefore handoff-ready for the three-year wide-format + equity + rankings + map path, but it still lacks the normalized 4-workbook / 2024-25 data path and still has an environment-blocked browser-console check.
**Consequences:**
- `STATUS.md`, `README.md`, `WORKFLOW.md`, and `.squad/sprint.md` should describe closeout as complete for loop 3 while explicitly sending the repo back to **Build**.
- `.squad/review_report.md` becomes the authoritative closeout record for the rankings-and-map loop.
- The next Build loop must choose between restoring the normalized-data / 2024-25 path or finishing the blocked browser-console dashboard review before another Validate/Closeout pass.

### D-020 — Build Loop 4: Ingest Historical PARCC Files (2015-16 through 2018-19)
**Date:** 2026-04-27
**Decision:** Extend `src/load_wide_format_data.py` to ingest the four historical PARCC workbooks already committed to the repository (2015-16, 2016-17, 2017-18, 2018-19) alongside the three files already being loaded (2021-22, 2022-23, 2023-24). This resolves the Task 03 summary-row shortfall (1,234 vs. ≥ 1,700 target).
**Rationale:**
- All four historical files are already present in `input_data/School and Demographic Group Aggregation/` and share the same wide-format schema (school × grade × ELA/Math columns with pre-computed proficiency counts and percentages).
- The `FILE_YEAR_MAP` only matched years 2022, 2023, and 2024; the historical files were silently ignored.
- The older files use different demographic sheet naming conventions (e.g., "Black Students" instead of "BlAfAm", "Econ Disadvantaged Students" instead of "EconDisad") and slightly different MSAA column names in 2015-16/2016-17. Adding these variants to `SHEET_SUBGROUP` and `COL_PATTERNS` is the minimal change needed.
- Cohort transitions across the 2019–2022 COVID gap are correctly absent because `analyze_cohort_growth.py` only matches `followup_year == baseline_year + 1`.
**Consequences:**
- `FILE_YEAR_MAP` now covers years 2016, 2017, 2018, 2019, 2022, 2023, 2024 (7 files).
- `SHEET_SUBGROUP` gains aliases for all older descriptive sheet names across the 2015-16 through 2018-19 naming evolution.
- `COL_PATTERNS` gains fallback patterns for the 2015-16/2016-17 MSAA column names.
- `output_data/combined_all_years.csv`: 28,069 rows (was 12,378; +127%).
- `output_data/cohort_growth_detail.csv`: 12,956 rows (was 5,391; +140%).
- `output_data/cohort_growth_summary.csv`: **2,560 rows** (was 1,234; Task 03 ≥ 1,700 target now met).
- All four Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied).
- School name variations across years (e.g., "Aiton ES" vs. "Aiton Elementary School") may limit cross-era comparisons at the school level but do not affect within-period cohort tracking.
- The 2017-18 file has no MSAA columns; the 2015-16/2016-17 MSAA columns load correctly with the new patterns.
- Next step: run Validate/Closeout for loop 4.

### D-021 — Validate Passes Loop 4 and Advances to Closeout
**Date:** 2026-04-27
**Decision:** Mark Validate as **PASS** for the loop-4 historical-data wide-format pipeline and advance the repo to **Closeout**.
**Rationale:** A fresh-clone validation re-ran the documented smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, and `python src/generate_school_rankings.py` all exited 0. The run regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), and `school_equity_rankings.csv` (414 rows). `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200, and a live `POST /_dash-update-component` request returned all seven figures, including a real 2024 Math map backed by `input_data/school_locations.csv` (113 plotted schools in the All Students view). Direct browser-console inspection remained blocked because the Playwright browser profile was locked.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation evidence for loop 4.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 4.
- Closeout should decide whether to sign off the current 7-workbook wide-format path and explicitly carry forward the remaining scope: the missing normalized 4-workbook / 2024-25 path and the blocked browser-console check.

### D-022 — Closeout Signs Off Loop 4 and Returns the Repo to Build
**Date:** 2026-04-27
**Decision:** Closeout approves handoff for the current 7-workbook wide-format loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, and `WORKFLOW.md`, then reran the documented smoke path in a clean environment: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, and `python src/generate_school_rankings.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), and `school_equity_rankings.csv` (414 rows). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all seven figures with a real 2024 Math / All Students map backed by `input_data/school_locations.csv` (113 plotted schools). The current loop is therefore handoff-ready, but the repo still lacks the normalized 4-workbook / 2024-25 path and still has an environment-blocked browser-console check.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 4 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the 7-workbook wide-format handoff.
- The next Build loop must choose one explicit follow-up: restore the normalized 4-workbook / 2024-25 ingestion path, or finish the blocked browser-console / manual dashboard validation work.

### D-023 — Build Loop 5: Proficiency Trend Analysis and Grade × Year Heatmap
**Date:** 2026-04-28
**Decision:** Implement `src/proficiency_trend_analysis.py` and extend the dashboard with an 8th figure — a Grade × Year proficiency heatmap.
**Rationale:**
- `backlog/phases.md` Phase 3 Build explicitly lists "Add heatmap and scatter-plot visualizations to the dashboard" as unimplemented scope.
- A Grade × Year heatmap is the most analytically interpretable heatmap for this dataset: it shows how each grade level's proficiency evolves across years at a selected school, or citywide when no school is selected. This directly complements the cohort growth analysis (which tracks students as they move up grades) with a fixed-grade lens.
- The charter vs. DCPS comparison and 2024-25 normalized-data path remain blocked (no school-type column in existing files; no 2024-25 workbook in repo), so the heatmap is the most impactful feasible deliverable for this loop.
- The pre-existing `analyze_growth.py` produces a wide-format YoY growth file but is not in the official smoke path and calls `analyze_cohort_growth.py` internally. The new `proficiency_trend_analysis.py` is a lean standalone script that replaces this for the dashboard use case.
**Consequences:**
- `src/proficiency_trend_analysis.py` — new standalone script; produces `output_data/proficiency_trends.csv` (25,629 rows: school × year × subject × grade × subgroup).
- `app/app_simple.py` — callback now returns 8 figures; 8th is a `go.Heatmap` with RdYlGn colour scale centred at 50% proficiency.
- When a school is selected, the heatmap shows that school's grade-by-year grid; when no school is selected, it shows the citywide average.
- `proficiency_trends.csv` reveals the COVID learning-loss pattern: citywide ELA avg dropped from 35.2% (2019) to 29.4% (2022) and recovered to 32.1% (2024); Math dropped from 30.9% to 21.2% and recovered to 24.9%.
- Smoke test path updated: adds `python src/proficiency_trend_analysis.py` as step 8.
- All four Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied); no changes to cohort engine.

### D-024 — Validate Passes Loop 5 and Advances to Closeout
**Date:** 2026-04-28
**Decision:** Mark Validate as **PASS** for the loop-5 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:** A fresh-clone validation reran the documented smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, and `python src/proficiency_trend_analysis.py` all exited 0. The run regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), and `proficiency_trends.csv` (25,629 rows). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all eight figures, including the new Grade × Year heatmap. Direct browser-console inspection remained blocked because the Playwright browser profile was locked.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation evidence for loop 5.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 5.
- Closeout should decide whether to sign off the current 7-workbook wide-format + heatmap path and explicitly carry forward the remaining scope: the missing normalized 4-workbook / 2024-25 path, the blocked browser-console check, and any remaining dashboard enhancements such as the backlog scatter plot.

### D-025 — Closeout Signs Off Loop 5 and Returns the Repo to Build
**Date:** 2026-04-28
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + heatmap loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, and `WORKFLOW.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, and `python src/proficiency_trend_analysis.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), and `proficiency_trends.csv` (25,629 rows). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all eight figures with the new Grade × Year heatmap. The current loop is therefore handoff-ready, but the repo still lacks the normalized 4-workbook / 2024-25 path, still has an environment-blocked browser-console check, and still has the backlog scatter-plot enhancement unimplemented.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 5 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the 7-workbook wide-format + heatmap handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized 4-workbook / 2024-25 ingestion path, finish the blocked browser-console / manual dashboard validation work, or add the remaining scatter-plot dashboard view.

### D-026 — Build Loop 6: Baseline Proficiency vs. Cohort Growth Scatter Plot
**Date:** 2026-04-28
**Decision:** Extend `app/app_simple.py` with a 9th figure — a Baseline Proficiency vs. Cohort Growth scatter plot — fulfilling the remaining "scatter-plot visualization" item from `backlog/phases.md` Phase 3 Build.
**Rationale:**
- All prior loops completed the heatmap but left the scatter-plot item unimplemented.
- A Baseline Proficiency vs. Cohort Growth scatter is the most analytically interpretable scatter for this dataset: each point is a school, the x-axis shows where students started (avg baseline proficiency %), the y-axis shows how much they grew (avg cohort growth in pp), and quadrant reference lines separate "beating the odds" (low baseline, positive growth) from struggling, high-and-growing, and high-but-declining schools.
- This directly advances the project goal of "ranking schools by cohort growth" by showing the growth-vs-baseline relationship at a glance, complementing the existing bar charts.
- The chart reads from the already-generated `cohort_growth_summary.csv` with no new pipeline scripts.
**Consequences:**
- `app/app_simple.py` callback now returns **9 figures** (was 8); the 9th is the scatter plot.
- Scatter uses `px.scatter` with: size = n_transitions, colour = pct_significant_transitions (Blues scale), quadrant reference lines (dashed grey) at x=50% and y=0, and four quadrant labels ("Beating the odds", "High & growing", "Struggling", "High but declining").
- Respects all existing filters: subject, student group, school selection, year range.
- `/_dash-dependencies` confirms 9 outputs in the single update callback.
- Smoke test path unchanged (no new standalone scripts); dashboard step now confirms 9 figures.
- Next recommended step: run Validate/Closeout for loop 6.

### D-027 — Validate Passes Loop 6 and Advances to Closeout
**Date:** 2026-04-29
**Decision:** Mark Validate as **PASS** for the loop-6 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:** A fresh-clone validation reran the documented smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, and `python src/proficiency_trend_analysis.py` all exited 0. The run regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), and `proficiency_trends.csv` (25,629 rows). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all nine figures, including the new Baseline Proficiency vs. Cohort Growth scatter plot. Direct browser-console inspection remained blocked because the Playwright browser profile was locked.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation evidence for loop 6.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 6.
- Closeout should decide whether to sign off the current 7-workbook wide-format + scatter path and explicitly carry forward the remaining scope: the missing normalized 4-workbook / 2024-25 path and the blocked browser-console check.

### D-028 — Closeout Signs Off Loop 6 and Returns the Repo to Build
**Date:** 2026-04-29
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + scatter loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, and `WORKFLOW.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, and `python src/proficiency_trend_analysis.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), and `proficiency_trends.csv` (25,629 rows). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all nine figures, including the new Baseline Proficiency vs. Cohort Growth scatter plot. The current loop is therefore handoff-ready, but the repo still lacks the normalized 4-workbook / 2024-25 path and still has an environment-blocked browser-console check.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 6 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the 7-workbook wide-format + scatter handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized 4-workbook / 2024-25 ingestion path or finish the blocked browser-console / manual dashboard review.

### D-029 — Build Loop 7: Formatted Excel Policy Summary Report
**Date:** 2026-04-29
**Decision:** Implement `src/generate_summary_report.py` to produce a formatted 6-sheet Excel workbook (`output_data/summary_report.xlsx`) for policy stakeholders.
**Rationale:**
- `backlog/phases.md` Phase 3 Build explicitly lists "Generate formatted Excel/PDF summary reports" as unimplemented scope that remained open after loop 6.
- All analytical outputs (cohort growth, equity gaps, school rankings, proficiency trends) already exist as CSVs; the summary report simply assembles them into a stakeholder-ready document without requiring new pipeline data.
- The charter vs. DCPS comparison remains blocked (no LEA-type column in wide-format OSSE files); the normalized 4-workbook / 2024-25 path requires external data. The summary report is therefore the most impactful feasible deliverable for this loop.
**Consequences:**
- `src/generate_summary_report.py` — new standalone script; run it after all other pipeline scripts.
- Reads: `cohort_growth_summary.csv`, `school_rankings.csv`, `school_equity_rankings.csv`, `equity_gap_summary.csv`, `proficiency_trends.csv`.
- Writes: `output_data/summary_report.xlsx` with 6 formatted sheets — Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory.
- Formatting uses openpyxl: dark-blue header rows, alternating row shading, green/red font for positive/negative growth values, frozen first row, auto-set column widths.
- Falls back to plain CSV exports if openpyxl is not installed (openpyxl is already in requirements.txt via pandas, so this should not occur in practice).
- Smoke test path updated: adds `python src/generate_summary_report.py` as step 9 (before dashboard startup).
- Next step: run Validate/Closeout for loop 7.


### D-030 — Validate Passes Loop 7 and Advances to Closeout
**Date:** 2026-04-29
**Decision:** Mark Validate as **PASS** for the loop-7 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:** A fresh-clone validation reran the documented smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, and `python src/generate_summary_report.py` all exited 0. The run regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), and `summary_report.xlsx` (6 sheets). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all nine figures. Direct browser-console inspection remained blocked because the Playwright browser profile was locked.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation evidence for loop 7.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 7.
- Closeout should decide whether to sign off the current 7-workbook wide-format + summary-report loop and explicitly carry forward the remaining scope: the missing normalized 4-workbook / 2024-25 path and the blocked browser-console check.

### D-031 — Closeout Signs Off Loop 7 and Returns the Repo to Build
**Date:** 2026-04-29
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + summary-report loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, and `WORKFLOW.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, and `python src/generate_summary_report.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), and `summary_report.xlsx` (6 sheets). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all nine figures. The current loop is therefore handoff-ready, but the repo still lacks the normalized 4-workbook / 2024-25 path and still has an environment-blocked browser-console check.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 7 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the 7-workbook wide-format + summary-report handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized 4-workbook / 2024-25 ingestion path or finish the blocked browser-console / manual dashboard review.

### D-032 — Build Loop 8: Geographic Equity Analysis
**Date:** 2026-04-29
**Decision:** Implement `src/geographic_equity_analysis.py` to compute and visualize school performance by DC geographic quadrant (NE / NW / SE / SW), add a 10th dashboard figure, and add a "Geographic Equity" sheet to `summary_report.xlsx`.
**Rationale:**
- `backlog/phases.md` Phase 3 Build lists "Implement charter vs. traditional public school comparison" as remaining scope; however, this is blocked because the wide-format OSSE files do not include an LEA-type column. Geographic equity analysis is the most impactful feasible alternative: `input_data/school_locations.csv` already provides Neighborhood and Quadrant for 115 DC schools, and DC has well-documented geographic performance disparities (NW vs. East-of-Rock-Creek) that are highly relevant to policy stakeholders.
- The 2024-25 data path remains blocked (external data not in repo), and the browser-console check is blocked in this environment.
- Geographic equity analysis adds new analytical value (quadrant-level proficiency + growth comparison, gap-vs-NW metric) without requiring new pipeline data or external downloads.
**Consequences:**
- `src/geographic_equity_analysis.py` — new standalone script; run after `proficiency_trend_analysis.py`.
- School name normalization bridges the 95/115 direct-match gap using abbreviation expansion + normalized-key matching; 95 schools are matched to growth/trends data.
- Outputs: `geographic_equity_by_school.csv` (210 rows: school × subject with Quadrant and Neighborhood) and `geographic_equity_by_quadrant.csv` (8 rows: 4 quadrants × 2 subjects).
- Key finding: NW avg ELA proficiency 42.7% vs. NE 24.1%, SE 20.1% (−18 pp to −23 pp gap). NW also leads cohort growth (+4.85 pp ELA). SE schools face the largest baseline-proficiency shortfall and below-citywide cohort growth. Math shows a similar geographic divide.
- Dashboard (`app/app_simple.py`) extended to load `geographic_equity_by_quadrant.csv` and render a 10th figure: dual-axis bar+line chart of avg proficiency (left axis) and avg cohort growth (right axis) by quadrant.
- `src/generate_summary_report.py` extended to write Sheet 7 "Geographic Equity" to `summary_report.xlsx` when `geographic_equity_by_quadrant.csv` is present; gracefully skips the sheet if the file is absent.
- Smoke path updated: adds `python src/geographic_equity_analysis.py` as step 9 (before `generate_summary_report.py`).
- Next step: Validate loop 8 (smoke path, 10 figures, 7 sheets), then Closeout.

### D-033 — Validate Passes Loop 8 and Advances to Closeout
**Date:** 2026-04-29
**Decision:** Mark Validate as **PASS** for the loop-8 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:** A fresh-clone validation reran the documented smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, and `python src/generate_summary_report.py` all exited 0. The run regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), and `summary_report.xlsx` (7 sheets). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all ten figures, including the new geographic-equity chart. Direct browser-console inspection remained blocked in this sandbox, but the server-side dashboard path showed no exceptions.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation evidence for loop 8.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 8.
- Closeout should decide whether to sign off the current 7-workbook wide-format + geographic-equity + summary-report loop and explicitly carry forward the remaining scope: the missing normalized 4-workbook / 2024-25 path and the blocked browser-console check.

### D-034 — Closeout Signs Off Loop 8 and Returns the Repo to Build
**Date:** 2026-04-29
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + geographic-equity + summary-report loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:** Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, and `python src/generate_summary_report.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), and `summary_report.xlsx` (7 sheets). `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; and a live `POST /_dash-update-component` request returned all ten figures. The current loop is therefore handoff-ready, but the repo still lacks the normalized 4-workbook / 2024-25 path and still has an environment-blocked browser-console check.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 8 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the loop-8 geographic-equity handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized-data / 2024-25 ingestion path or finish the blocked browser-console review for the current 10-figure dashboard before another Validate/Closeout cycle.

### D-035 — Build Loop 9: Same-Grade Year-over-Year Growth Analysis
**Date:** 2026-04-29
**Decision:** Implement `src/yoy_growth_analysis.py` as a standalone script computing same-grade year-over-year growth for every school, grade, subject, and student subgroup, and extend the dashboard with an 11th figure and `summary_report.xlsx` with an 8th sheet ("YoY Growth").
**Rationale:**
- `backlog/README.md` explicitly lists "same-grade year-over-year growth for every school, subject, and student subgroup" as a project goal alongside cohort growth. Loop 9 fulfils this goal.
- The existing `analyze_growth.py` was written as a prototype but was not standalone (it internally calls `analyze_cohort_growth.py`), so a clean dedicated script avoids duplicated work and confusion in the smoke path.
- The normalized 4-workbook / 2024-25 data path remains blocked (external files not in repo). The browser-console check is blocked in this environment. Charter vs. DCPS comparison is blocked (no LEA-type column in wide-format files). YoY growth is therefore the highest-value feasible deliverable for loop 9.
- YoY growth uses the same consecutive-year-pair logic as cohort growth (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) and applies the same minimum-N=10 filter.
**Consequences:**
- `src/yoy_growth_analysis.py` — new standalone script; run it after `geographic_equity_analysis.py` and before `generate_summary_report.py`.
- Outputs: `output_data/yoy_growth_detail.csv` (14,391 rows: school × grade × subject × subgroup × transition) and `output_data/yoy_growth_summary.csv` (2,604 rows: school × subject × subgroup).
- Dashboard (`app/app_simple.py`) extended to load `yoy_growth_detail.csv` and render an 11th figure: a same-grade YoY growth line chart (citywide mode: one line per grade; school mode: one line per school).
- `src/generate_summary_report.py` extended to write Sheet 8 "YoY Growth" to `summary_report.xlsx` when `yoy_growth_summary.csv` is present; gracefully skips the sheet if the file is absent.
- Key YoY findings: citywide ELA avg +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024). Math: +2.07, −4.32, +2.42, +3.25, +0.35 pp respectively. The 2017→2018 Math dip (−4.32 pp avg) is analytically interesting and warrants further investigation.
- All four Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied).
- Smoke path updated: adds `python src/yoy_growth_analysis.py` as step 10 (after `geographic_equity_analysis.py`, before `generate_summary_report.py`).
- Next step: run Validate/Closeout for loop 9.

### D-036 — Validate Passes Loop 9 and Advances to Closeout
**Date:** 2026-04-29
**Decision:** Mark Validate as **PASS** for the loop-9 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:**
- Re-ran the documented fresh-clone smoke path: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, `python src/yoy_growth_analysis.py`, and `python src/generate_summary_report.py`. All commands exited 0.
- The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows), and `summary_report.xlsx` (8 sheets).
- Workbook/schema inspection confirmed Task 03 and Task 05 still pass: the Stuart-Hobson 2022→2023 benchmark remains within ±0.1 pp, `cohort_growth_detail.csv` still includes `p_value` and `significant`, `cohort_growth_summary.csv` still includes `pct_significant_transitions`, and `summary_report.xlsx` now includes the `YoY Growth` sheet.
- `python app/app_simple.py` started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; Dash advertised an 11-output callback; and a live `POST /_dash-update-component` returned all eleven figures, including the new YoY growth chart. A headless Chromium screenshot confirmed the dashboard renders in this environment.
- The browser-console inspection remains environment-blocked, and the normalized 4-workbook / 2024-25 path remains outside the reproducible in-repo scope.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation record for the loop-9 YoY-aware handoff.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 9.
- Closeout must decide whether the current in-repo handoff is sufficient despite the still-blocked browser-console review and missing normalized-data ingestion path.

### D-037 — Closeout Signs Off Loop 9 and Returns the Repo to Build
**Date:** 2026-04-29
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + geographic-equity + same-grade YoY + summary-report loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:**
- Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, `python src/yoy_growth_analysis.py`, and `python src/generate_summary_report.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows), and `summary_report.xlsx` (8 sheets).
- `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; a live `POST /_dash-update-component` request returned all eleven figures; and a fresh headless Chromium screenshot confirmed the dashboard renders in this environment.
- The current loop is therefore handoff-ready for the reproducible in-repo path, but the repo still lacks the normalized 4-workbook / 2024-25 path required by Tasks 01–02, and direct browser-console inspection remains blocked in this environment.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 9 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the loop-9 YoY-aware handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized-data / 2024-25 ingestion path, finish the blocked browser-console review for the current 11-figure dashboard, or deliberately narrow the backlog to the verified wide-format scope before another Validate/Closeout cycle.

### D-038 — Build Loop 10: COVID Recovery Analysis
**Date:** 2026-04-29
**Decision:** Implement `src/covid_recovery_analysis.py` as a standalone script computing the 2019→2022 COVID impact and 2022→2024 recovery trajectory for every school, subject, and student subgroup; extend the dashboard with a 12th figure; and add Sheet 9 "COVID Recovery" to `summary_report.xlsx`.
**Rationale:**
- The repo contains data for 2019 (pre-COVID) and 2022, 2023, 2024 (post-COVID), making a COVID recovery analysis directly possible with no new data dependencies.
- This answers a high-priority policy question: "Which schools have recovered to pre-COVID performance levels, and which are still below?" The answer directly informs resource-allocation and intervention decisions.
- The normalized 4-workbook / 2024-25 data path remains blocked (external files not in repo). The browser-console check remains blocked in this environment. Charter vs. DCPS comparison is blocked (no LEA-type column in wide-format files). COVID recovery is therefore the highest-value feasible deliverable for loop 10.
- Minimum-N=10 filter is applied throughout; same suppression handling as existing scripts.
**Consequences:**
- `src/covid_recovery_analysis.py` — new standalone script; run it after `yoy_growth_analysis.py` and before `generate_summary_report.py`.
- Outputs: `output_data/covid_recovery_detail.csv` (1,239 rows: school × subject × subgroup with 2019/2022/2024 metrics) and `output_data/covid_recovery_summary.csv` (200 rows: school × subject, All Students only, with recovery status).
- Key findings: citywide ELA avg COVID impact −3.94 pp (2019→2022), recovery +1.75 pp (2022→2024), net vs. pre-COVID −2.15 pp. Math was hit harder: −8.56 pp impact, +3.17 pp recovery, net −5.43 pp. Recovery status distribution (200 school/subject observations): 38% Partially Recovered, 25% Still Below, 24% Exceeded, 12% Fully Recovered, 2% No 2024 Data.
- Dashboard (`app/app_simple.py`) extended to load `covid_recovery_summary.csv` and render a 12th figure: in citywide mode, a scatter plot of COVID Impact vs. Recovery progress (colour-coded by recovery status); in school-selection mode, a grouped bar chart comparing 2019/2022/2024 proficiency.
- `src/generate_summary_report.py` extended to write Sheet 9 "COVID Recovery" to `summary_report.xlsx` when `covid_recovery_summary.csv` is present; gracefully skips the sheet if the file is absent.
- Smoke path updated: adds `python src/covid_recovery_analysis.py` as step 11 (after `yoy_growth_analysis.py`, before `generate_summary_report.py`).
- All four Stuart-Hobson benchmark transitions remain within ±0.1 pp (D-004 satisfied).
- Next step: run Validate/Closeout for loop 10.

### D-039 — Validate Passes Loop 10 and Advances to Closeout
**Date:** 2026-04-29
**Decision:** Mark Validate as **PASS** for the loop-10 wide-format pipeline and advance the repo to **Closeout**.
**Rationale:**
- Re-ran the documented fresh-clone smoke path end to end: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, `python src/yoy_growth_analysis.py`, `python src/covid_recovery_analysis.py`, and `python src/generate_summary_report.py`. All commands exited 0.
- The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows), `covid_recovery_detail.csv` (1,239 rows), `covid_recovery_summary.csv` (200 rows), and `summary_report.xlsx` (9 sheets).
- Workbook/schema inspection confirmed Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, `summary_report.xlsx` includes the `COVID Recovery` sheet, the expected YoY transitions remain present, and the Stuart-Hobson 2022→2023 benchmark remains within ±0.1 pp.
- `python app/app_simple.py` started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; Dash advertised a 12-output callback; and a live `POST /_dash-update-component` returned all twelve figures, including the new COVID recovery chart. A headless Chromium screenshot confirmed the dashboard renders in this environment; the screenshot viewport height was raised to 3600 px to capture the taller 12-figure loop-10 page in one pass.
- The browser-console inspection remains environment-blocked, and the normalized 4-workbook / 2024-25 path remains outside the reproducible in-repo scope.
**Consequences:**
- `.squad/validation_report.md` becomes the authoritative validation record for the loop-10 COVID-recovery-aware handoff.
- `STATUS.md` should move the repo to **Validate complete / Closeout next** for loop 10.
- Closeout must decide whether the current in-repo handoff is sufficient despite the still-blocked browser-console review and missing normalized-data ingestion path.

### D-040 — Closeout Signs Off Loop 10 and Returns the Repo to Build
**Date:** 2026-04-29
**Decision:** Closeout approves handoff for the current 7-workbook wide-format + geographic-equity + same-grade YoY + COVID-recovery + summary-report loop and returns the repo to **Build** for the remaining backlog scope rather than marking the whole project complete.
**Rationale:**
- Closeout rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md`, then reran the documented smoke path in a fresh clone: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, `python src/yoy_growth_analysis.py`, `python src/covid_recovery_analysis.py`, and `python src/generate_summary_report.py`. The rerun regenerated `combined_all_years.csv` (28,069 rows), `cohort_growth_detail.csv` (12,956 rows), `cohort_growth_summary.csv` (2,560 rows), `equity_gap_detail.csv` (13,008 rows), `equity_gap_summary.csv` (2,138 rows), `school_rankings.csv` (422 rows), `school_equity_rankings.csv` (414 rows), `proficiency_trends.csv` (25,629 rows), `geographic_equity_by_school.csv` (210 rows), `geographic_equity_by_quadrant.csv` (8 rows), `yoy_growth_detail.csv` (14,391 rows), `yoy_growth_summary.csv` (2,604 rows), `covid_recovery_detail.csv` (1,239 rows), `covid_recovery_summary.csv` (200 rows), and `summary_report.xlsx` (9 sheets).
- `python app/app_simple.py` also started successfully; `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; a live `POST /_dash-update-component` request returned all twelve figures; and a fresh headless Chromium screenshot at `/tmp/loop10-closeout-dashboard.png` confirmed the dashboard renders in this environment.
- The current loop is therefore handoff-ready for the reproducible in-repo path, but the repo still lacks the normalized 4-workbook / 2024-25 path required by Tasks 01–02, direct browser-console inspection remains blocked in this environment, and charter-vs.-DCPS analysis is still not possible from the current wide-format files.
**Consequences:**
- `STATUS.md`, `README.md`, and `WORKFLOW.md` should describe closeout as complete for loop 10 while explicitly sending the repo back to **Build** next.
- `.squad/review_report.md` becomes the authoritative closeout record for the loop-10 COVID-recovery-aware handoff.
- The next Build loop must choose an explicit follow-up: restore the normalized-data / 2024-25 ingestion path, finish the blocked browser-console review for the current 12-figure dashboard, or deliberately narrow the backlog to the verified wide-format scope before another Validate/Closeout cycle.

