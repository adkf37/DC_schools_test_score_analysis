# Project Status — DC Schools Test Score Analysis

## Current Objective

**Loop 14 Validate complete — subgroup proficiency trend analysis reproduces cleanly, extends the dashboard to 16 figures, and advances to Closeout next.**

Loop 14 Validate confirmed the full 7-workbook wide-format smoke path from a fresh clone, including the new subgroup trend analysis outputs and dashboard/reporting extensions. The repo now has reproducible evidence for the subgroup-aware analytical path: `subgroup_proficiency.csv` regenerates with **152 rows**, `subgroup_summary.csv` regenerates with **22 rows**, the dashboard callback returns **16 figures**, and `summary_report.xlsx` regenerates with **13 sheets** (adds "Subgroups").

Loop 14 Validate confirmed:
1. `python -m pip install -r requirements.txt`, `python -m pip install dash plotly`, and `python -m py_compile src/*.py app/*.py inspect_data.py` all exit 0 in this clone.
2. The full smoke path through `python src/generate_summary_report.py` exits 0 and regenerates the documented outputs, including `subgroup_proficiency.csv` (**152 rows**), `subgroup_summary.csv` (**22 rows**), and `summary_report.xlsx` (**13 sheets**).
3. Workbook/schema inspection confirms Task 03 and Task 05 still pass: `cohort_growth_detail.csv` retains `p_value` and `significant`, `cohort_growth_summary.csv` retains `pct_significant_transitions`, the four Stuart-Hobson 2022→2023 benchmark rows remain within ±0.1 pp, and the summary workbook now includes the `Subgroups` sheet.
4. Subgroup inspection confirms the loop-14 claims: ELA avg proficiency peaks at **White (83.82%)** and bottoms at **Students with Disabilities (7.92%)** for a **75.90 pp** gap; Math peaks at **White (77.06%)** and bottoms at **Students with Disabilities (6.46%)** for a **70.60 pp** gap; the largest COVID hit is **Hispanic/Latino of any race** in both subjects (**−9.70 pp ELA**, **−14.54 pp Math**); and the strongest recovery is **Asian** in both subjects (**+10.31 pp ELA**, **+8.65 pp Math**).
5. The dashboard HTTP path is live: `GET /`, `/_dash-layout`, and `/_dash-dependencies` return 200; dependency metadata now includes `subgroup-trend.figure`; direct callback invocation returns all **16 figures**, including the new subgroup chart.
6. A headless Chromium screenshot at `/tmp/loop14-dashboard.png` confirms the dashboard renders in this environment.
7. Direct browser-console inspection remains blocked in this sandbox, and the normalized-data / 2024-25 path plus charter-vs.-DCPS analysis remain outside the reproducible in-repo scope.

**Next step: run Closeout for loop 14.**


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
| 3 | Build | ✅ Complete through loop 14 — equity gap, school map, rankings, historical data ingestion, proficiency heatmap, scatter plot, summary report, geographic equity, same-grade YoY growth, COVID recovery analysis, school trajectory classification, school type analysis, grade-level analysis, subgroup trend analysis |
| 4 | Validate | ✅ Complete for loops 1-14 |
| 5 | Closeout | ✅ Complete for loops 2-13 |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path now covers 7 in-repo files (2016–2024); normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (28,069 rows, 7 years, 251 raw schools / 211 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Task 03 target now met — 12,956 detail rows, **2,560 summary rows** (target ≥ 1,700); all 4 Stuart-Hobson benchmarks pass |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves **16 figures** (loop 14 adds subgroup trend), school-level and citywide views functional |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (13,008 rows) and equity_gap_summary.csv (2,138 rows) — expanded with historical data |
| 07 | Formatted Excel summary report | Closeout | Statistician | ✅ Validate complete for loop 14 — `generate_summary_report.py` exits 0; `summary_report.xlsx` regenerated with **13 sheets** (adds Subgroups in loop 14) |

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
| **Policy summary report** | `output_data/summary_report.xlsx` | ✅ **13 sheets** — adds Subgroups sheet in loop 14 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ Extended — now handles all 7 in-repo workbooks across 6 naming schemes |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| School rankings script | `src/generate_school_rankings.py` | ✅ New — ranks schools by cohort growth and equity-gap narrowing |
| **Proficiency trend script** | `src/proficiency_trend_analysis.py` | ✅ **New in loop 5** — grade × year proficiency grid |
| **Summary report script** | `src/generate_summary_report.py` | ✅ **Updated in loop 14** — now produces 13-sheet Excel workbook |
| **Geographic equity script** | `src/geographic_equity_analysis.py` | ✅ **New in loop 8** — joins school locations with performance data by DC quadrant |
| **YoY growth script** | `src/yoy_growth_analysis.py` | ✅ **New in loop 9** — same-grade year-over-year growth for every school, grade, subject, subgroup |
| **COVID recovery script** | `src/covid_recovery_analysis.py` | ✅ **New in loop 10** — 2019→2022 COVID impact and 2022→2024 recovery per school, subject, subgroup |
| **School trajectory script** | `src/school_trajectory_analysis.py` | ✅ **New in loop 11** — OLS trend slope and class for every school × subject (All Students, 2016–2024) |
| **School type analysis script** | `src/school_type_analysis.py` | ✅ **New in loop 12** — grade-band classification and performance metrics by school type |
| **Grade-level analysis script** | `src/grade_level_analysis.py` | ✅ **New in loop 13** — grade-specific proficiency, COVID recovery, and YoY metrics |
| **Subgroup trend analysis script** | `src/subgroup_trend_analysis.py` | ✅ **New in loop 14** — subgroup-specific proficiency, COVID recovery, and YoY metrics |
| School locations | `input_data/school_locations.csv` | ✅ 115 DC public school geocoordinates |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap and rankings sections |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to **16 figures**; 16th figure is the subgroup proficiency trend |
| Validation report | `.squad/validation_report.md` | ✅ Updated for loop 14 |
| Review report | `.squad/review_report.md` | ✅ Updated for loop 13 |

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

- **Smoke test commands (loop 14 — validate complete):**
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
  16. `python src/generate_summary_report.py`
  17. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, and `/_dash-dependencies`; verify the dashboard callback path via `app.app_simple.update_figures(...)` (returns **16 figures**, including the subgroup proficiency trend chart)
- **Loop 14 validation evidence:** reran the full smoke path; all scripts exit 0. `subgroup_proficiency.csv` regenerated (**152 rows**), `subgroup_summary.csv` regenerated (**22 rows**), and `summary_report.xlsx` regenerated (**13 sheets**). Dashboard `GET /`, `/_dash-layout`, and `/_dash-dependencies` returned 200; dependency metadata included `subgroup-trend.figure`; direct callback invocation returned **16 figures**; headless screenshot saved to `/tmp/loop14-dashboard.png`.
- **Loop 14 subgroup findings:** ELA proficiency (All Students, 2016–2024 avg): White **83.82%** > Students with Disabilities **7.92%** (gap **75.90 pp**). Math proficiency: White **77.06%** > Students with Disabilities **6.46%** (gap **70.60 pp**). Largest COVID impact: Hispanic/Latino of any race (**−9.70 pp ELA**, **−14.54 pp Math**). Strongest recovery: Asian (**+10.31 pp ELA**, **+8.65 pp Math**).
- **Loop 11 validation evidence:** reran the full smoke path; all scripts exit 0. `school_trajectory_classification.csv` regenerated (424 rows); `summary_report.xlsx` regenerated (10 sheets); dashboard `GET /`, `/_dash-layout`, `/_dash-dependencies` returned 200; live callback returned **13 figures**; headless screenshot saved to `/tmp/loop11-dashboard.png`.
- **Loop 11 trajectory findings:** ELA citywide avg trend slope +0.065 pp/yr — distribution: 55% Insufficient Data (≤2 years of data), 14% Stable, 13% Declining, 9% Improving, 5% Strongly Improving, 4% Strongly Declining. Math avg slope −0.656 pp/yr — more schools are Declining/Strongly Declining than Improving. Top ELA improver: Whittier ES (+8.2 pp/yr, 22%→39%). Top Math improver: Whittier ES (+9.2 pp/yr, 23%→41%). NOTE: 55% of schools are classified "Insufficient Data" because they only appear in the most recent 1-2 years (minimum 3 years required for OLS trend).
- **Loop 10 COVID recovery findings:** citywide ELA avg COVID impact −3.94 pp (2019→2022), recovery +1.75 pp (2022→2024), net vs. pre-COVID −2.15 pp. Math was hit harder: −8.56 pp impact, +3.17 pp recovery, net −5.43 pp. Recovery status: 38% Partially Recovered, 25% Still Below Pre-COVID, 24% Exceeded Pre-COVID, 12% Fully Recovered, 2% No 2024 Data (200 school/subject observations, All Students).
- **Remaining backlog scope — normalized OSSE files:** `load_clean_data.py` targets are still not available in the repo.
- **Current environment limitation — browser console:** direct browser-console inspection remains blocked in this environment.
- **Remaining backlog scope — charter vs. DCPS comparison:** the wide-format OSSE files do not include an LEA-type column distinguishing DCPS from charter schools.
- **Next recommended step:** Run **Closeout** for loop 14, then decide whether to return to **Build** for the normalized-data / 2024-25 ingestion path, the blocked browser-console review, or a deliberate narrowing of the backlog to the verified wide-format scope.
