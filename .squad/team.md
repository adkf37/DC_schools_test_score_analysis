# Squad Team

> DC_schools_test_score_analysis

## Coordinator

| Name | Role | Notes |
|------|------|-------|
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name | Role | Charter | Status |
|------|------|---------|--------|
| Lead | Project Lead & Architect | [charter](.squad/agents/lead/charter.md) | 🟢 Active |
| Data Engineer | Data Ingestion & Pipeline | [charter](.squad/agents/data-engineer/charter.md) | 🟢 Active |
| Statistician | Analysis & Statistical Tests | [charter](.squad/agents/statistician/charter.md) | 🟢 Active |
| Tester | Quality Assurance & Validation | [charter](.squad/agents/tester/charter.md) | 🟢 Active |
| Scribe | Documentation & History | [charter](.squad/agents/scribe/charter.md) | 🟢 Active |
| Ralph | Risk, Assumptions & Review | [charter](.squad/agents/ralph/charter.md) | 🟢 Active |

## @copilot Capability Profile

| Capability | Fit | Notes |
|------------|-----|-------|
| Data ingestion fixes | 🟢 | Well-defined, file-based, testable |
| Schema normalization | 🟢 | Clear patterns, existing examples |
| Statistical test implementation | 🟡 | Needs careful review of methodology |
| Dashboard updates | 🟡 | Requires UI judgment |
| Architecture decisions | 🔴 | Needs human/Lead judgment |
| Security/auth changes | 🔴 | Not applicable to this project |

## Project Context

- **Project:** DC_schools_test_score_analysis
- **Domain:** Education policy — DC public/charter school PARCC/DCCAPE/MSAA analysis
- **Stack:** Python 3.9+, pandas, openpyxl, Dash, scipy
- **Data:** OSSE annual school-level Excel files (4 years: 2021-22 → 2024-25)
- **Created:** 2026-04-25
