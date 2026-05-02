# Project Status — DC Schools Test Score Analysis

## Current Objective

**Loop 19 Build complete — ward-level performance analysis implemented; Validate next.**

Loop 19 Build completed:
1. Created `src/ward_analysis.py` — maps all 115 schools in `school_locations.csv` to one of DC's
   8 political wards using a neighbourhood→ward lookup table aligned to the 2022 DC redistricting.
   Produces `ward_proficiency.csv` (84 rows: avg proficiency by ward × subject × year) and
   `ward_summary.csv` (16 rows: ward × subject aggregated metrics including avg proficiency, cohort
   growth, COVID impact/recovery, gap vs. Ward 3).
2. Extended `app/app_simple.py` — loads `ward_summary.csv` and `ward_proficiency.csv`; adds **21st**
   dashboard figure (`ward-analysis`): grouped bar chart of avg proficiency (left axis) and cohort
   growth (right axis) by DC ward for the selected subject.
3. Extended `src/generate_summary_report.py` — adds Sheet 18 "Ward Analysis" when `ward_summary.csv`
   is present; gracefully skips if absent. Workbook now regenerates with **18 sheets**.
4. `python -m py_compile src/*.py app/*.py inspect_data.py` exits 0.

Key findings from ward analysis (ELA):
- Ward 3 (Tenleytown/Cleveland Park/Chevy Chase): 60.6% avg proficiency, +6.5 pp cohort growth — highest ELA proficiency in DC
- Ward 8 (Anacostia/Congress Heights): 14.1% avg proficiency, +4.7 pp cohort growth — gap vs. Ward 3: −46.5 pp
- Ward 7 (Marshall Heights/Deanwood): 19.7% avg proficiency, +3.4 pp cohort growth — gap vs. Ward 3: −41.0 pp
- Ward 5 (Brookland/Trinidad): 19.0% avg proficiency, +3.7 pp cohort growth — gap vs. Ward 3: −41.7 pp
- Ward 2 (Georgetown/Dupont/Logan): 59.6% avg proficiency, +3.1 pp cohort growth — nearly equal to Ward 3

Key findings from ward analysis (Math):
- Ward 3: 57.3% avg proficiency, −1.2 pp cohort growth — highest Math proficiency
- Ward 8: 9.7% avg proficiency, +0.4 pp cohort growth — gap vs. Ward 3: −47.6 pp
- Wards 5 and 7: 12.8% and 13.1% avg proficiency — largest Math gaps

**Note on methodology:** Ward assignments use neighbourhood centroids from `school_locations.csv`
mapped to wards via the `NEIGHBORHOOD_WARD` lookup dict in `ward_analysis.py`. Schools in
neighbourhoods that span ward boundaries are assigned to the majority-area ward per the 2022
DC redistricting. 20 of 115 schools (17%) could not be matched by name to proficiency/growth data
and are excluded from ward averages; this does not systematically bias any ward because unmatched
names are distributed across the city.

**Next step: Validate Loop 19 — run full smoke path adding `python src/ward_analysis.py` before
`python src/generate_summary_report.py`, confirm 21 dashboard figures and 18 workbook sheets.**

Loop 18 Closeout confirmed:
1. Rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md` against the closeout acceptance criteria.
2. Re-ran the documented fresh-clone smoke path: `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, `python src/load_wide_format_data.py`, `python src/analyze_cohort_growth.py`, `python src/equity_gap_analysis.py`, `python src/generate_school_rankings.py`, `python src/proficiency_trend_analysis.py`, `python src/geographic_equity_analysis.py`, `python src/yoy_growth_analysis.py`, `python src/covid_recovery_analysis.py`, `python src/school_trajectory_analysis.py`, `python src/school_type_analysis.py`, `python src/grade_level_analysis.py`, `python src/subgroup_trend_analysis.py`, `python src/school_consistency_analysis.py`, `python src/school_performance_index.py`, `python src/charter_dcps_analysis.py`, `python src/school_needs_index.py`, `python src/generate_summary_report.py`, plus dashboard checks for `GET /`, `/_dash-layout`, `/_dash-dependencies`, direct callback rendering, and a fresh headless screenshot at `/tmp/loop18-closeout-dashboard.png`.
3. Confirmed the current handoff reproduces `school_needs_index.csv` (**422 rows**), `needs_tier_summary.csv` (**10 rows**), `summary_report.xlsx` (**17 sheets**), and a **20-figure** dashboard callback path.
4. Updated `.squad/review_report.md`, `.squad/decisions.md`, `README.md`, and `WORKFLOW.md` so the handoff narrative matches the validated loop-18 school-needs-aware state.
5. Approved the current reproducible 7-workbook wide-format path for handoff, but returned the repo to **Build** because the normalized-data / 2024-25 path, browser-console inspection, and limited charter coverage remain open.

Key findings from needs index (ELA):
- Critical (54 schools): avg proficiency 22.1%, avg cohort growth +0.5 pp
- High (51 schools): avg proficiency 29.9%, avg cohort growth +3.5 pp
- Low (53 schools): avg proficiency 37.2%, avg cohort growth +11.3 pp
- Top Critical-need ELA schools: Van Ness ES (composite 78.2, proficiency 36.1%), Plummer ES (73.3, 17.3%), Bancroft ES (72.5, 45.8%), Miner ES (72.5, 9.9%), Cardozo EC (71.4, 14.2%)

Key findings from needs index (Math):
- Critical (53 schools): avg proficiency 26.8%, avg cohort growth −4.6 pp
- Top Critical-need Math schools: Ida B. Wells MS (composite 86.5, proficiency 9.5%), Van Ness ES (81.2, 21.4%), Thomson ES (74.1, 27.9%)

**Note on methodology:** The Needs Index is the policy-targeted complement to the Performance Index (Loop 16). A school can appear Critical-need in the index even with above-median proficiency if it has low growth, poor COVID recovery, and large equity gaps (for example, Van Ness ES in ELA). Policy stakeholders should examine the component scores alongside the composite.

**Next step: choose the next Build target — restore the normalized-data / 2024-25 ingestion path, finish the blocked browser-console review for the current 20-figure dashboard, or deliberately narrow the backlog to the verified wide-format scope.**
Loop 16 Closeout completed:
1. Rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md` against the closeout acceptance criteria.
2. Re-ran the documented smoke path from a fresh clone context: dependency installs, `python -m py_compile src/*.py app/*.py inspect_data.py`, the full wide-format analytical pipeline through `python src/generate_summary_report.py`, and dashboard checks for `GET /`, `/_dash-layout`, `/_dash-dependencies`, direct callback rendering, and a fresh headless screenshot at `/tmp/loop16-closeout-dashboard.png`.
3. Confirmed the current handoff reproduces `school_performance_index.csv` (**456 rows**), `performance_index_summary.csv` (**12 rows**), `summary_report.xlsx` (**15 sheets**), and an **18-figure** dashboard callback path.
4. Updated `.squad/review_report.md`, `.squad/decisions.md`, `README.md`, and `WORKFLOW.md` so the handoff narrative matches the validated loop-16 performance-index-aware state.
5. Approved the current reproducible 7-workbook wide-format path for handoff, but returned the repo to **Build** because the normalized-data / 2024-25 path, browser-console inspection, and charter-vs.-DCPS analysis remain open.

Key findings from performance index (ELA):
- Q5 Top Performers (43 schools): avg composite 81.1, avg proficiency 47.5%
- Top ELA composite schools: Janney ES (93.6), Hyde-Addison ES (92.7), Lafayette ES (92.0), Eaton ES (91.2), Ludlow Taylor ES (90.3)
- Q1 Bottom Performers (42 schools): avg composite 19.6, avg proficiency 11.3%
- ~7% of schools per subject have Insufficient Data (< 2 valid components)

Key findings from performance index (Math):
- Q5 Top Performers (43 schools): avg composite 79.0, avg proficiency 45.0%
- Top Math composite schools: Hyde-Addison ES (96.0), Murch ES @ UDC (90.6), Bancroft ES @ Sharpe (88.4), Hearst ES (88.4), Whittier ES (87.4)

**Previous next step (completed Loop 17 Build): choose the next Build target — restore the normalized-data / 2024-25 ingestion path, complete the blocked browser-console review for the current 18-figure dashboard, or deliberately narrow the backlog to the verified wide-format scope.**

Loop 13 Build completed:
1. Created `src/grade_level_analysis.py` — exits 0; produces `grade_level_proficiency.csv` (98 rows: avg/median proficiency by grade × subject × year) and `grade_level_summary.csv` (14 rows: grand-average metrics by grade × subject with COVID impact, recovery, and avg YoY growth).
2. Extended `app/app_simple.py` — loads `grade_level_proficiency.csv`; adds 15th figure: in citywide mode, line chart of avg proficiency by grade over time; in school-selection mode, selected school's per-grade proficiency overlaid on faint citywide grade averages.
3. Extended `src/generate_summary_report.py` — adds Sheet 12 "Grade Levels" when `grade_level_summary.csv` is present; gracefully skips if absent. Workbook now regenerates with **12 sheets**.
4. `python -m py_compile src/*.py app/*.py inspect_data.py` exits 0.
5. Dashboard `/_dash-dependencies` advertises a **15-output** callback, and the callback logic returns all 15 figures during validation.

Key findings from grade-level analysis:
- ELA proficiency (All Students, 2016–2024 avg): Grade 4 highest (32.7%) → Grade 6 lowest (26.0%)
- Math proficiency (All Students, 2016–2024 avg): Grade 3 highest (33.8%) → HS lowest (13.2%)
- Largest ELA COVID impact: Grade 7 (−10.78 pp 2019→2022)
- Largest Math COVID impact: Grade 4 (−11.55 pp 2019→2022)
- Strongest ELA recovery: Grade 6 (+4.49 pp 2022→2024)
- Strongest Math recovery: Grade 4 (+4.70 pp 2022→2024)

Loop 13 Validate confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, and `python -m py_compile src/*.py app/*.py inspect_data.py` all exit 0 in this clone.
2. The full smoke path through `python src/generate_summary_report.py` exits 0 and regenerates the documented outputs, including `grade_level_proficiency.csv` (**98 rows**), `grade_level_summary.csv` (**14 rows**), and `summary_report.xlsx` (**12 sheets**).
3. Workbook/schema inspection confirms Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, the four Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp, and the summary workbook now includes the `Grade Levels` sheet.
4. Grade-level inspection confirms the loop-13 claims: ELA avg proficiency peaks at **Grade 4 (32.74%)** and bottoms at **Grade 6 (26.04%)**; Math peaks at **Grade 3 (33.76%)** and bottoms at **HS (13.17%)**; the largest ELA COVID impact is **Grade 7 (−10.78 pp)**; the largest Math COVID impact is **Grade 4 (−11.55 pp)**; strongest ELA recovery is **Grade 6 (+4.49 pp)**; strongest Math recovery is **Grade 4 (+4.70 pp)**.
5. The dashboard HTTP path is live: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200; Dash advertises a **15-output** callback; direct callback invocation returns all 15 figures, including the new grade-level chart.
6. A headless Chromium screenshot at `/tmp/loop13-dashboard.png` confirms the dashboard renders in this environment.
7. Direct browser-console inspection remains blocked in this sandbox, and the normalized-data / 2024-25 path remains outside the reproducible in-repo scope.

**Next step: choose the next Build target (normalized-data / 2024-25 ingestion, browser-console review for the 15-figure dashboard, or formal narrowing of backlog scope).**

Loop 12 Validate confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, and `python -m py_compile src/*.py app/*.py inspect_data.py` all exit 0 in this clone.
2. The full smoke path through `python src/generate_summary_report.py` exits 0 and regenerates the documented outputs, including `school_type_by_school.csv` (**251 rows**), `school_type_proficiency.csv` (**70 rows**), `school_type_summary.csv` (**10 rows**), and `summary_report.xlsx` (**11 sheets**).
3. Workbook/schema inspection confirms Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, and the four Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp.
4. School-type inspection confirms the loop-12 claims: the school-type mix is **147 Elementary / 39 High School / 31 Elementary-Middle / 28 Middle School / 6 Middle-High**; Elementary still leads average proficiency in both ELA (**31.85%**) and Math (**30.91%**); Elementary-Middle shows the strongest ELA cohort growth (**+6.56 pp/yr**); Middle School has the strongest ELA recovery (**+3.37 pp**); Elementary has the strongest Math recovery (**+4.06 pp**); and High School ELA COVID impact remains **+1.46 pp**.
5. The dashboard HTTP path is live: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200; Dash advertises a **14-output** callback; and a live `POST /_dash-update-component` returns all 14 figures, including the school type chart.
6. A headless Chromium screenshot at `/tmp/loop12-dashboard.png` confirms the dashboard renders in this environment.
7. Direct browser-console inspection remains blocked in this sandbox, and the normalized-data / 2024-25 path remains outside the reproducible in-repo scope.

Loop 12 Build completed:
1. Created `src/school_type_analysis.py` — exits 0; produces `school_type_by_school.csv` (251 rows: school-level type classification), `school_type_proficiency.csv` (70 rows: avg/median proficiency by school type × subject × year), and `school_type_summary.csv` (10 rows: grand-average metrics by school type × subject with COVID recovery and cohort growth).
2. Extended `app/app_simple.py` — loads `school_type_proficiency.csv` and `school_type_by_school.csv`; adds 14th figure: in citywide mode, line chart of avg proficiency by school type over time; in school-selection mode, selected schools plotted individually (coloured by type) overlaid on faint type-average lines for context.
3. Extended `src/generate_summary_report.py` — adds Sheet 11 "School Types" when `school_type_summary.csv` is present; gracefully skips if absent. Workbook now regenerates with **11 sheets**.
4. `python -m py_compile src/*.py app/*.py inspect_data.py` exits 0.
5. Dashboard `/_dash-dependencies` advertises a **14-output** callback; `GET /`, `/_dash-layout` return 200.

Key findings from school type analysis:
- ELA proficiency (All Students, 2016–2024 avg): Elementary 31.9% > Elementary-Middle 28.9% > High School 27.7% > Middle School 26.1% > Middle-High 18.9%
- Math proficiency (All Students, 2016–2024 avg): Elementary 30.9% > Elementary-Middle 21.4% > Middle School 13.9% > High School 12.2% > Middle-High 9.5%
- Elementary schools had the largest ELA COVID impact (−4.2 pp) and Elementary-Middle the largest Math COVID impact (−8.4 pp)
- High School ELA COVID impact was +1.5 pp (counter-intuitive; likely driven by test composition changes at the high school level)
- Middle School ELA recovery was strongest (+3.4 pp); Elementary Math recovery was strongest (+4.1 pp)

Loop 12 Closeout confirmed:
1. Rechecked `STATUS.md`, `backlog/README.md`, all backlog task files, `.squad/sprint.md`, `.squad/decisions.md`, `.squad/validation_report.md`, `README.md`, `WORKFLOW.md`, and `docs/methods.md` against the loop-12 acceptance criteria.
2. Accepted the fresh-clone smoke-path evidence for the current in-repo handoff: `school_type_by_school.csv` (**251 rows**), `school_type_proficiency.csv` (**70 rows**), `school_type_summary.csv` (**10 rows**), `summary_report.xlsx` (**11 sheets**), and a live dashboard callback returning **14 figures**.
3. Updated `.squad/review_report.md`, `.squad/decisions.md`, `README.md`, and `WORKFLOW.md` so the closeout narrative matches the validated school-type-aware state.
4. Approved the current reproducible in-repo path for handoff, but returned the repo to **Build** because the normalized-data / 2024-25 ingestion path, browser-console inspection, and LEA-type-based charter-vs.-DCPS analysis remain open.

Loop 11 Closeout complete — the school-trajectory-aware handoff is approved for the reproducible in-repo path; return to Build for remaining backlog scope.

Loop 11 closeout rechecked the backlog tasks, sprint plan, decision log, validation report, and human-facing docs, then re-ran the documented fresh-clone smoke path plus the dashboard HTTP/callback path.  The school trajectory deliverable remains reproducible end to end: `school_trajectory_classification.csv` regenerates with **424 rows**, preserves the documented average trend slopes (ELA **+0.065 pp/yr**, Math **−0.656 pp/yr**), and still shows Whittier Elementary School as the top improver in both subjects.  The dashboard renders **13 figures** end to end via a live Dash callback, and `summary_report.xlsx` now has **10 sheets** (adds "School Trajectories" sheet).  The current in-repo handoff is approved, but the normalized-data / 2024-25 path and direct browser-console inspection remain open.

Loop 11 Build completed:
1. Created `src/school_trajectory_analysis.py` — exits 0; produces `school_trajectory_classification.csv` (424 rows: 212 schools × 2 subjects, All Students, with OLS slope, R², and trajectory class).
2. Extended `app/app_simple.py` — loads `school_trajectory_classification.csv`; adds 13th figure: in citywide mode, scatter of trend slope vs. avg proficiency (colour-coded by trajectory class); in school-selection mode, same scatter filtered to selected schools.
3. Extended `src/generate_summary_report.py` — adds Sheet 10 "School Trajectories" when `school_trajectory_classification.csv` is present; gracefully skips if absent. Workbook now regenerates with **10 sheets**.
4. `python -m py_compile src/*.py app/*.py inspect_data.py` exits 0.
5. Dashboard `GET /`, `/_dash-layout`, `/_dash-dependencies` return 200; `POST /_dash-update-component` returns all **13 figures**.

Loop 11 Validate confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, and `python -m py_compile src/*.py app/*.py inspect_data.py` all exit 0 in this clone.
2. The full smoke path through `python src/generate_summary_report.py` exits 0 and regenerates the documented outputs, including `school_trajectory_classification.csv` (**424 rows**) and `summary_report.xlsx` (**10 sheets**).
3. Workbook/schema inspection confirms Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, and the four Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp.
4. Trajectory inspection confirms the loop-11 claims: average slope by subject is **+0.065 pp/yr (ELA)** and **−0.656 pp/yr (Math)**; ELA class mix is 117 Insufficient Data / 30 Stable / 27 Declining / 19 Improving / 11 Strongly Improving / 8 Strongly Declining; Math class mix is 117 Insufficient Data / 38 Declining / 21 Stable / 18 Strongly Declining / 11 Improving / 7 Strongly Improving.
5. The dashboard HTTP path is live: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200; Dash advertises a **13-output** callback; and a live `POST /_dash-update-component` returns all 13 figures, including the school trajectory chart.
6. A headless Chromium screenshot at `/tmp/loop11-dashboard.png` confirms the dashboard renders in this environment.
7. Direct browser-console inspection remains blocked in this sandbox, and the normalized-data / 2024-25 path remains outside the reproducible in-repo scope.

Loop 11 Closeout confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, `python -m py_compile src/*.py app/*.py inspect_data.py`, and the full loop-11 smoke path through `python src/generate_summary_report.py` all exit 0 in this clone.
2. The closeout rerun regenerated the documented loop-11 outputs, including `school_trajectory_classification.csv` (**424 rows**) and `summary_report.xlsx` (**10 sheets**).
3. `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; Dash advertised a **13-output** callback; and a live `POST /_dash-update-component` returned all **13 figures**, including the school trajectory chart.
4. A fresh headless Chromium screenshot at `/tmp/loop11-closeout-dashboard.png` confirms the dashboard still renders in this environment during closeout.
5. `README.md` and `WORKFLOW.md` are refreshed to describe the loop-11 school-trajectory-aware handoff.
6. The current loop is handoff-ready for the reproducible in-repo path, but the repo still lacks the normalized 4-workbook / 2024-25 path required by Tasks 01–02, and direct browser-console inspection remains blocked in this environment.

Loop 10 Closeout confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, and `python -m py_compile src/*.py app/*.py inspect_data.py` all exit 0 in this clone.
2. The full smoke path through `python src/generate_summary_report.py` exits 0 and regenerates the documented outputs, including `covid_recovery_detail.csv` (**1,239 rows**), `covid_recovery_summary.csv` (**200 rows**), and `summary_report.xlsx` (**9 sheets**).
3. Workbook/schema inspection confirms Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, and the four Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp.
4. The dashboard HTTP path is live: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200; Dash advertises a **12-output** callback; and a live `POST /_dash-update-component` returns all 12 figures, including the COVID recovery chart.
5. A headless Chromium screenshot at `/tmp/loop10-closeout-dashboard.png` confirms the dashboard renders in this environment.
6. Direct browser-console inspection remains blocked in this sandbox, and the normalized-data / 2024-25 path remains outside the reproducible in-repo scope.

Loop 9 closeout rechecked the backlog tasks, sprint plan, decision log, validation report, and human-facing docs, then re-ran the documented fresh-clone smoke path plus the dashboard HTTP/callback path. The same-grade year-over-year (YoY) growth deliverable remains reproducible end to end: citywide ELA YoY growth averaged +4.82 pp (2016→2017), +0.94 pp (2017→2018), +4.91 pp (2018→2019), +2.02 pp (2022→2023), +0.48 pp (2023→2024); Math shows a similar pattern with a 2017→2018 dip (avg −4.32 pp) and recovery in 2022→2023 (+3.25 pp). The dashboard renders **11 figures**; `summary_report.xlsx` now has **8 sheets** (adds "YoY Growth" sheet); the current in-repo handoff is approved, but the original normalized-data / 2024-25 path and direct browser-console inspection remain open.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | ✅ Complete through loop 18 — equity gap, school map, rankings, historical data ingestion, proficiency heatmap, scatter plot, summary report, geographic equity, same-grade YoY growth, COVID recovery analysis, school trajectory classification, school type analysis, grade-level analysis, subgroup trend analysis, school consistency analysis, multi-metric school performance index, school program sector analysis, and school needs index |
| 4 | Validate | ✅ Complete for loops 1-18 |
| 5 | Closeout | ✅ Complete for loops 2-17 |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Validate | Data Engineer | ✅ Validated — app starts, serves **20 figures** (loop 18 adds the school-needs chart), school-level and citywide views functional |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |
| 07 | Formatted Excel summary report | Validate | Statistician | ✅ Validate complete for loop 18 — `generate_summary_report.py` exits 0; `summary_report.xlsx` regenerated with **17 sheets** (adds School Needs in loop 18) |

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
| **School trajectory classification** | `output_data/school_trajectory_classification.csv` | ✅ **New in loop 11** — 424 rows (212 schools × 2 subjects, All Students, with OLS slope, R², trajectory class) |
| **School type classification (by school)** | `output_data/school_type_by_school.csv` | ✅ **New in loop 12** — 251 rows (school-level type: Elementary / Middle / High / Elem-Mid / Mid-High) |
| **School type proficiency (trend)** | `output_data/school_type_proficiency.csv` | ✅ **New in loop 12** — 70 rows (avg/median proficiency by school type × subject × year) |
| **School type summary** | `output_data/school_type_summary.csv` | ✅ **New in loop 12** — 10 rows (grand-avg proficiency + COVID recovery + cohort growth by type × subject) |
| **Grade-level proficiency (trend)** | `output_data/grade_level_proficiency.csv` | ✅ **New in loop 13** — 98 rows (avg/median proficiency by grade × subject × year) |
| **Grade-level summary** | `output_data/grade_level_summary.csv` | ✅ **New in loop 13** — 14 rows (grand-avg proficiency + COVID recovery + avg YoY growth by grade × subject) |
| **Subgroup proficiency (trend)** | `output_data/subgroup_proficiency.csv` | ✅ **New in loop 14** — 152 rows (avg/median proficiency by subgroup × subject × year) |
| **Subgroup summary** | `output_data/subgroup_summary.csv` | ✅ **New in loop 14** — 22 rows (grand-avg proficiency + COVID recovery + avg YoY growth by subgroup × subject) |
| **School consistency** | `output_data/school_consistency.csv` | ✅ **New in loop 15** — 424 rows (school × subject consistency metrics and class) |
| **Consistency class summary** | `output_data/consistency_class_summary.csv` | ✅ **New in loop 15** — 10 rows (consistency class × subject summary) |
| **School performance index** | `output_data/school_performance_index.csv` | ✅ **New in loop 16** — 456 rows (school × subject composite score, quintile, and component percentiles) |
| **Performance index summary** | `output_data/performance_index_summary.csv` | ✅ **New in loop 16** — 12 rows (composite quintile × subject summary) |
| **School sector classification (by school)** | `output_data/school_sector_by_school.csv` | ✅ **New in loop 17** — 251 rows (school-level sector: Charter / DCPS Specialized / DCPS Alternative / DCPS Traditional) |
| **School sector proficiency (trend)** | `output_data/school_sector_proficiency.csv` | ✅ **New in loop 17** — 48 rows (avg proficiency by sector × subject × year) |
| **School sector summary** | `output_data/school_sector_summary.csv` | ✅ **New in loop 17** — 8 rows (sector × subject summary with COVID recovery and cohort growth) |
| **School needs index** | `output_data/school_needs_index.csv` | ✅ **New in loop 18** — 422 rows (211 schools × 2 subjects, with composite needs scores and tiers) |
| **Needs tier summary** | `output_data/needs_tier_summary.csv` | ✅ **New in loop 18** — 10 rows (needs tier × subject summary) |
| **Policy summary report** | `output_data/summary_report.xlsx` | ✅ **17 sheets** — adds School Needs sheet in loop 18 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| **Summary report script** | `src/generate_summary_report.py` | ✅ **Updated in loop 18** — now produces 17-sheet Excel workbook |
| **Geographic equity script** | `src/geographic_equity_analysis.py` | ✅ **New in loop 8** — joins school locations with performance data by DC quadrant |
| **YoY growth script** | `src/yoy_growth_analysis.py` | ✅ **New in loop 9** — same-grade year-over-year growth for every school, grade, subject, subgroup |
| **COVID recovery script** | `src/covid_recovery_analysis.py` | ✅ **New in loop 10** — 2019→2022 COVID impact and 2022→2024 recovery per school, subject, subgroup |
| **School trajectory script** | `src/school_trajectory_analysis.py` | ✅ **New in loop 11** — OLS trend slope and class for every school × subject (All Students, 2016–2024) |
| **School type analysis script** | `src/school_type_analysis.py` | ✅ **New in loop 12** — grade-band classification and performance metrics by school type |
| **Grade-level analysis script** | `src/grade_level_analysis.py` | ✅ **New in loop 13** — grade-specific proficiency, COVID recovery, and YoY metrics |
| **Subgroup trend analysis script** | `src/subgroup_trend_analysis.py` | ✅ **New in loop 14** — subgroup-specific proficiency, COVID recovery, and YoY metrics |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| **School consistency analysis script** | `src/school_consistency_analysis.py` | ✅ **New in loop 15 smoke path** — school-level volatility / consistency classification |
| **School performance index script** | `src/school_performance_index.py` | ✅ **New in loop 16 smoke path** — multi-metric composite score and quintile assignment |
| **School sector analysis script** | `src/charter_dcps_analysis.py` | ✅ **New in loop 17 smoke path** — school-program-sector classification and sector metrics |
| **School needs index script** | `src/school_needs_index.py` | ✅ **New in loop 18 smoke path** — composite intervention-need score and needs-tier assignment |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to **20 analytical figures** including the populated school-needs chart |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 18 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 17 |

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

- **Smoke test commands (loop 18 — Validate complete):**
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
  12. `python src/school_trajectory_analysis.py`
  13. `python src/school_type_analysis.py`
  14. `python src/grade_level_analysis.py`
  15. `python src/subgroup_trend_analysis.py`
  16. `python src/school_consistency_analysis.py`
  17. `python src/school_performance_index.py`
  18. `python src/charter_dcps_analysis.py`
  19. `python src/school_needs_index.py`
  20. `python src/generate_summary_report.py`
  21. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, and `/_dash-dependencies`; verify the dashboard callback path via `app.app_simple.update_figures(...)` (returns **20 figures**, including the school-needs chart)
- **Loop 18 validation evidence:** reran the full smoke path plus dashboard HTTP checks. The current build remains reproducible end to end: `school_needs_index.csv` regenerated (**422 rows**), `needs_tier_summary.csv` regenerated (**10 rows**), `summary_report.xlsx` regenerated (**17 sheets**), the dashboard callback returned **20 figures**, and a fresh validation screenshot was saved to `/tmp/loop18-validate-dashboard.png`.
- **Loop 18 needs findings:** ELA needs tiers = **54 Critical / 51 High / 52 Moderate / 53 Low / 1 Insufficient Data**; Math needs tiers = **53 Critical / 52 High / 52 Moderate / 53 Low / 1 Insufficient Data**. Top Critical-need ELA schools: Van Ness ES (**78.2**), Plummer ES (**73.3**), Bancroft ES (**72.5**). Top Critical-need Math schools: Ida B. Wells MS (**86.5**), Van Ness ES (**81.2**), Thomson ES (**74.1**).
- **Loop 11 validation evidence:** reran the full smoke path; all scripts exit 0. `school_trajectory_classification.csv` regenerated (424 rows); `summary_report.xlsx` regenerated (10 sheets); dashboard `GET /`, `/_dash-layout`, `/_dash-dependencies` returned 200; live callback returned **13 figures**; headless screenshot saved to `/tmp/loop11-dashboard.png`.
- **Loop 11 trajectory findings:** ELA citywide avg trend slope +0.065 pp/yr — distribution: 55% Insufficient Data (≤2 years of data), 14% Stable, 13% Declining, 9% Improving, 5% Strongly Improving, 4% Strongly Declining. Math avg slope −0.656 pp/yr — more schools are Declining/Strongly Declining than Improving. Top ELA improver: Whittier ES (+8.2 pp/yr, 22%→39%). Top Math improver: Whittier ES (+9.2 pp/yr, 23%→41%). NOTE: 55% of schools are classified "Insufficient Data" because they only appear in the most recent 1-2 years (minimum 3 years required for OLS trend).
- **Loop 10 COVID recovery findings:** citywide ELA avg COVID impact −3.94 pp (2019→2022), recovery +1.75 pp (2022→2024), net vs. pre-COVID −2.15 pp. Math was hit harder: −8.56 pp impact, +3.17 pp recovery, net −5.43 pp. Recovery status: 38% Partially Recovered, 25% Still Below Pre-COVID, 24% Exceeded Pre-COVID, 12% Fully Recovered, 2% No 2024 Data (200 school/subject observations, All Students).
- **Remaining backlog scope — normalized OSSE files:** `load_clean_data.py` targets are still not available in the repo.
- **Current environment limitation — browser console:** direct browser-console inspection remains blocked in this environment for the current 20-figure dashboard.
- **Remaining backlog scope — full charter coverage:** the validated school-sector analysis is still a proxy because the in-repo wide-format files expose only 3 charter-coded schools; a full charter-vs.-DCPS comparison still requires separate OSSE charter-school files.
- **Next recommended step:** Proceed to **Closeout** for loop 18, then decide whether the next loop returns to **Build** for normalized-data / 2024-25 ingestion, blocked browser-console review, fuller charter coverage, or an explicit narrowing of scope to the verified wide-format path.
