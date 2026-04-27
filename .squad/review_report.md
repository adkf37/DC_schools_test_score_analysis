# Review Report

**Date:** 2026-04-27
**Reviewer:** Ralph
**Final Decision:** **CLOSEOUT SIGNOFF FOR THE CURRENT RANKINGS-AND-MAP WIDE-FORMAT LOOP — return to Build for remaining scope**

## Scope

Closeout review for loop 3 against the backlog tasks, sprint Definition of Done, current documentation, and the repository's reproducibility requirements from a fresh clone.

## Evidence Checked

### Planning / status artifacts

- `STATUS.md`
- `backlog/README.md`
- `backlog/tasks/01-ingest-data.md`
- `backlog/tasks/02-clean-data.md`
- `backlog/tasks/03-cohort-growth.md`
- `backlog/tasks/04-dashboard.md`
- `backlog/tasks/05-statistical-tests.md`
- `.squad/sprint.md`
- `.squad/decisions.md`
- `.squad/validation_report.md`

### Human-facing docs reviewed

- `README.md`
- `WORKFLOW.md`
- `docs/methods.md`

### Validation commands re-run during closeout

1. `python -m pip install -r requirements.txt` — ✅ passed
2. `python -m pip install dash plotly` — ✅ passed
3. `python -m py_compile src/*.py app/*.py inspect_data.py` — ✅ passed
4. `python src/load_wide_format_data.py` — ✅ passed
5. `python src/analyze_cohort_growth.py` — ✅ passed
6. `python src/equity_gap_analysis.py` — ✅ passed
7. `python src/generate_school_rankings.py` — ✅ passed
8. `python app/app_simple.py` plus `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` — ✅ passed

## Acceptance Criteria Review

- **Closeout outcome recorded in `STATUS.md`** — ✅ updated in this loop
- **`.squad/review_report.md` exists and includes an explicit final decision** — ✅
- **Final closeout notes written to `.squad/decisions.md`** — ✅
- **Human-facing docs current enough for handoff** — ✅ refreshed to match the validated wide-format loop and remaining limitations
- **Remaining blockers or follow-up work are explicit** — ✅

## Findings

1. **Fresh-clone reproducibility succeeds for the repo's documented wide-format path, now including the loop-3 outputs.**
   `src/load_wide_format_data.py` discovers and loads the three committed workbooks under `input_data/School and Demographic Group Aggregation/`, then `src/analyze_cohort_growth.py`, `src/equity_gap_analysis.py`, and `src/generate_school_rankings.py` regenerate the expected outputs without manual intervention.

2. **Tasks 03, 04, and 05 plus the loop-2 and loop-3 follow-on deliverables are validated for the current loop, but the backlog still has open scope.**
   The closeout re-run regenerated `output_data/combined_all_years.csv` (12,378 rows), `cohort_growth_detail.csv` (5,391 rows), `cohort_growth_summary.csv` (1,234 rows), `cohort_growth_pivot.xlsx` (6 sheets), `equity_gap_detail.csv` (5,977 rows), `equity_gap_summary.csv` (1,042 rows), `school_rankings.csv` (192 rows), and `school_equity_rankings.csv` (187 rows). Stuart-Hobson benchmark transitions stayed within ±0.1 pp, the significance columns remain present, and a live dashboard callback returned all seven figures including a real map when `input_data/school_locations.csv` is present. In the current 2024 All Students view, that map plots 113 schools; `DC Public Schools` is correctly omitted because it is a citywide aggregate with no physical location.

3. **Closeout can sign off this loop, but not declare the whole backlog complete.**
   The handoff artifacts now match the verified state of the rankings-and-map wide-format pipeline, yet the project still has explicit follow-up work: the missing 2024-25 / normalized-data path, the original Task 03 summary-row target that remains out of reach with only three years of in-repo data, and the environment-blocked browser-console dashboard check.

## Known Risks

- The repo currently proves only the wide-format, 3-year path. The original 4-workbook normalized-data path still depends on external OSSE downloads and is not reproducible from the repo alone.
- `cohort_growth_summary.csv` remains at 1,234 rows versus the original ≥ 1,700-row Task 03 target because the repo lacks 2024-25 data and OSSE suppresses many small subgroup cells.
- The dashboard startup, seven-figure callback path, and locations-file map rendering are validated, but direct browser-console inspection during manual interaction remains unverified in this environment.

## Recommendation

**Sign off the current rankings-and-map wide-format loop for handoff, then return the repository to Build for the remaining backlog scope.**

Required follow-up:

1. Decide the next Build target: the missing normalized-data / 2024-25 ingestion path **or** the remaining browser-console / manual dashboard checks.
2. If the normalized-data path is chosen, align `src/load_clean_data.py` with the actual input contract or add/document the required OSSE files.
3. If dashboard work is chosen, validate the browser console during manual interaction against the seven-figure dashboard and decide whether to tighten any map-data coverage mismatches.
4. Re-run Validate/Closeout after the next Build loop changes the project scope or evidence.

## Signoff

**Approved for closeout of the current rankings-and-map wide-format loop. Not approved as full project completion.**
The repository is handoff-ready for a human who needs the verified three-year wide-format analysis path, equity-gap outputs, rankings outputs, live map evidence, and current limitations, and it should now return to **Build** for the next backlog slice.
