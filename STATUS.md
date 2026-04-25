# Project Status — DC Schools Test Score Analysis

## Current Objective

**Build loop 2 — Equity Gap Analysis implemented; ready for Validate.**

A new equity gap analysis script (`src/equity_gap_analysis.py`) and two output files (`equity_gap_detail.csv`, `equity_gap_summary.csv`) were added to advance the stated project goal of surfacing achievement gaps by student subgroup. The dashboard (`app/app_simple.py`) was extended with two additional equity charts (proficiency gap and gap-change bar charts), raising the total figure count to 7. The `docs/methods.md` documents the new gap metrics. All existing smoke tests still pass.

---

## Phase Tracker

| Phase | Name | Status |
|-------|------|--------|
| 0 | Planner | ✅ Complete |
| 1 | Squad Init | ✅ Complete |
| 2 | Squad Review | ✅ Complete |
| 3 | Build | 🔄 In progress — equity gap analysis added (loop 2) |
| 4 | Validate | ⏳ Pending — validate equity analysis outputs |
| 5 | Closeout | ⏳ Pending |

---

## Task Status

| ID | Task | Phase | Owner | Status |
|----|------|-------|-------|--------|
| 01 | Ingest raw data | Squad Init | Data Engineer | ✅ Wide-format path validated for the 3 in-repo source files; normalized 4-workbook path still pending external data |
| 02 | Clean & standardize data | Squad Review | Data Engineer | ✅ `combined_all_years.csv` regenerated (12,378 rows, 3 years, 116 raw schools / 96 cohort-analysis schools) |
| 03 | Cohort growth analysis | Build | Statistician | ✅ Smoke-tested end to end; all 4 Stuart-Hobson benchmarks pass; 5,391 detail rows, 1,234 summary rows |
| 04 | Interactive dashboard | Build | Data Engineer | ✅ Validated — app starts, serves 7 figures (5 original + 2 new equity charts), map degrades gracefully |
| 05 | Statistical significance tests | Build | Statistician | ✅ p_value and significant columns present in detail; pct_significant_transitions in summary |
| 06 | Equity gap analysis | Build | Statistician | ✅ equity_gap_detail.csv (5,977 rows) and equity_gap_summary.csv (1,042 rows) added; dashboard extended |

---

## Key Outputs

| Output | Location | Status |
|--------|----------|--------|
| Combined dataset (all years) | `output_data/combined_all_years.csv` | ✅ 12,378 rows (3 years) |
| Cohort growth detail | `output_data/cohort_growth_detail.csv` | ✅ 5,391 rows |
| Cohort growth summary | `output_data/cohort_growth_summary.csv` | ✅ 1,234 rows |
| Cohort growth Excel workbook | `output_data/cohort_growth_pivot.xlsx` | ✅ 6 sheets |
| Equity gap detail | `output_data/equity_gap_detail.csv` | ✅ 5,977 rows — new in loop 2 |
| Equity gap summary | `output_data/equity_gap_summary.csv` | ✅ 1,042 rows — new in loop 2 |
| Processing report | `output_data/processing_report.txt` | ✅ Created |
| Wide-format loader | `src/load_wide_format_data.py` | ✅ New — alternative to load_clean_data.py |
| Equity gap analysis script | `src/equity_gap_analysis.py` | ✅ New — computes proficiency and growth gaps by subgroup |
| Statistical methods note | `docs/methods.md` | ✅ Updated with equity gap section |
| Interactive dashboard | `app/app_simple.py` | ✅ Extended to 7 figures (2 equity gap charts added) |
| Validation report | `.squad/validation_report.md` | ✅ Loop 1 — needs update for loop 2 |
| Review report | `.squad/review_report.md` | ✅ Loop 1 — needs update for loop 2 |

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

- **Validated smoke test commands:**
  1. `python -m pip install -r requirements.txt`
  2. `python -m pip install dash plotly`
  3. `python -m py_compile src/*.py app/*.py inspect_data.py`
  4. `python src/load_wide_format_data.py`
  5. `python src/analyze_cohort_growth.py`
  6. `python src/equity_gap_analysis.py`
  7. Start `python app/app_simple.py`, then hit `GET /`, `/_dash-layout`, `/_dash-dependencies`, and `POST /_dash-update-component` (now returns 7 figures)
- **Wide-format validation passed for the current loop.** Required outputs regenerate from a fresh clone, significance columns remain present, equity gap outputs added, and the dashboard serves all seven figure payloads for a live callback request.
- **Summary row count:** 1,234 rows vs Task 03 target of ≥ 1,700. The shortfall is because (a) we have only 3 years of data (no 2024-25 file), and (b) small demographic groups are suppressed by OSSE in many schools. This remains an explicit limitation.
- **Normalized OSSE files** (`load_clean_data.py` targets) are still not available in the repo. These must be downloaded manually from OSSE. The wide-format alternative covers the available data already committed here.
- **Browser-console inspection:** direct manual console checking was blocked in this environment. Dashboard startup plus live callback requests showed no server-side exceptions.
- **Next recommended step:** Run Validate on the equity gap outputs, then Closeout loop 2.
