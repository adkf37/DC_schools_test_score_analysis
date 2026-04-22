# Project Phases

## Phase 0 — Planner ✅ COMPLETE
**Owner:** Lead/Planner  
**Goal:** Survey existing work, define research questions, and populate the backlog so the squad can hit the ground running.

**Deliverables:**
- `backlog/README.md` — background, goals, success criteria
- `backlog/data_sources.md` — data inventory with availability status
- `backlog/phases.md` — this file
- `backlog/tasks/*.md` — discrete task definitions
- `STATUS.md` — project status tracker
- `requirements.txt` — Python dependency list

---

## Phase 1 — Squad Init 🔲 NEXT
**Owner:** Data Engineer + Statistician  
**Goal:** Confirm all raw data files are present and the pipeline runs end-to-end in a clean environment.

**Deliverables:**
- All four OSSE Excel files verified in `input_data/`
- `python src/load_clean_data.py` runs without errors → `combined_all_years.csv`
- `python src/analyze_cohort_growth.py` runs → `cohort_growth_detail.csv`, `cohort_growth_summary.csv`, `cohort_growth_pivot.xlsx`
- Stuart-Hobson validation output confirms ±0.1 pp match on all four transitions
- `output_data/processing_report.txt` populated

---

## Phase 2 — Squad Review 🔲 PENDING
**Owner:** Statistician + Tester  
**Goal:** Review data quality, schema assumptions, and analysis logic before proceeding to deeper work.

**Deliverables:**
- Code review of `src/load_clean_data.py`, `src/analyze_cohort_growth.py`, `src/analyze_growth.py`
- Data quality audit: null rates, suppressed-value counts, school-count reconciliation
- Edge-case review: schools with only one year of data, grade-skipping students, combined vs. specific assessment rows
- Documented findings in `backlog/tasks/` as needed

---

## Phase 3 — Build 🔲 PENDING
**Owner:** Data Engineer + Statistician  
**Goal:** Extend the pipeline with statistical tests, additional visualizations, and export-ready outputs.

**Sub-tasks (see `backlog/tasks/`):**
- Add statistical significance tests for growth differences
- Add heatmap and scatter-plot visualizations to the dashboard
- Implement charter vs. traditional public school comparison
- Generate formatted Excel/PDF summary reports

---

## Phase 4 — Validate 🔲 PENDING
**Owner:** Tester + Statistician  
**Goal:** Confirm that all new features meet acceptance criteria and do not regress existing behavior.

**Deliverables:**
- Automated smoke tests for `load_clean_data.py` and `analyze_cohort_growth.py`
- Dashboard launch test (headless)
- Regression check: Stuart-Hobson four-transition match still holds
- Performance baseline: pipeline completes in < 3 minutes on reference hardware

---

## Phase 5 — Closeout 🔲 PENDING
**Owner:** Lead + Scribe  
**Goal:** Package and document final results for policy stakeholders.

**Deliverables:**
- Final `cohort_growth_pivot.xlsx` (curated sheets, formatted tables)
- Executive summary slide deck or PDF
- Updated `README.md` and `WORKFLOW.md` reflecting final pipeline
- `STATUS.md` marked **COMPLETE**
- Archived branch / tagged release
