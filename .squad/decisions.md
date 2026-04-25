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


