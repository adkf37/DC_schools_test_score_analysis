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

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
