# Work Routing

How to decide who handles what.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Data ingestion & schema normalization | Data Engineer | Load OSSE Excel files, fix column-name mapping, update `load_clean_data.py` |
| Pipeline orchestration & outputs | Data Engineer | `combined_all_years.csv`, `processing_report.txt`, output directory management |
| Dash dashboard & visualizations | Data Engineer | `app/app_simple.py`, chart updates, filter logic, map view |
| Cohort growth logic | Statistician | `analyze_cohort_growth.py`, pp_growth calculation, Stuart-Hobson validation |
| Statistical significance tests | Statistician | two-proportion z-test, p-values, multiple-comparison corrections |
| Subgroup / equity analysis | Statistician | Race/ethnicity breakdowns, charter vs. DCPS comparisons |
| Automated tests & smoke tests | Tester | `tests/`, pipeline smoke tests, dashboard headless launch test |
| Stuart-Hobson regression checks | Tester | Four-transition benchmark match within ±0.1 pp |
| Code review | Lead | Review PRs, check quality, suggest improvements |
| Scope & priorities | Lead | What to build next, trade-offs, architecture decisions |
| Risk identification | Ralph | Flag data quality risks, suppressed-value handling, edge cases |
| Documentation & history | Scribe | Update `README.md`, `WORKFLOW.md`, `STATUS.md`, decision log |
| Async issue work (bugs, tests, small features) | @copilot 🤖 | Well-defined tasks matching capability profile |
| Session logging | Scribe | Automatic — never needs routing |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, evaluate @copilot fit, assign `squad:{member}` label | Lead |
| `squad:data-engineer` | Data ingestion, pipeline, or dashboard work | Data Engineer |
| `squad:statistician` | Analysis, growth logic, or statistical tests | Statistician |
| `squad:tester` | Test writing, regression checks, or QA | Tester |
| `squad:lead` | Architecture, code review, or priority decisions | Lead |
| `squad:ralph` | Risk review, assumption checks, edge-case analysis | Ralph |
| `squad:scribe` | Documentation updates | Scribe |
| `squad:copilot` | Assign to @copilot for autonomous work (if enabled) | @copilot 🤖 |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, the **Lead** triages it — analyzing content, evaluating @copilot's capability profile, assigning the right `squad:{member}` label, and commenting with triage notes.
2. **@copilot evaluation:** The Lead checks if the issue matches @copilot's capability profile (🟢 good fit / 🟡 needs review / 🔴 not suitable). If it's a good fit, the Lead may route to `squad:copilot` instead of a squad member.
3. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
4. When `squad:copilot` is applied and auto-assign is enabled, `@copilot` is assigned on the issue and picks it up autonomously.
5. Members can reassign by removing their label and adding another member's label.
6. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

### Lead Triage Guidance for @copilot

When triaging, the Lead should ask:

1. **Is this well-defined?** Clear title, reproduction steps or acceptance criteria, bounded scope → likely 🟢
2. **Does it follow existing patterns?** Adding a test, fixing a known bug, updating a dependency → likely 🟢
3. **Does it need design judgment?** Architecture, API design, UX decisions → likely 🔴
4. **Is it security-sensitive?** Auth, encryption, access control → always 🔴
5. **Is it medium complexity with specs?** Feature with clear requirements, refactoring with tests → likely 🟡

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
8. **@copilot routing** — when evaluating issues, check @copilot's capability profile in `team.md`. Route 🟢 good-fit tasks to `squad:copilot`. Flag 🟡 needs-review tasks for PR review. Keep 🔴 not-suitable tasks with squad members.
