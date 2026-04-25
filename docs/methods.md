# Statistical Methods — DC Schools Test Score Analysis

## Cohort Growth Computation

For each school, subject, and student subgroup, cohort growth is defined as:

```
pp_growth = followup_pct − baseline_pct
```

where:

- **baseline**: the proficiency percentage for grade *G* in year *Y* (from OSSE school-level data)
- **followup**: the proficiency percentage for grade *G+1* in year *Y+1* (the same cohort one year later)

Grade matching uses the **Grade of Enrollment** column (not Tested Grade/Subject) so that middle-school students who take Algebra I or Pre-Algebra are kept together in a single cohort rather than split by test level (see Decision D-001).

Rows with fewer than 10 students in either the baseline or follow-up leg are excluded (Decision D-002). Suppressed OSSE cells (`DS`, `N<10`, `<5%`, `>95%`) are treated as missing and excluded (Decision D-003).

---

## Statistical Significance Testing (Task 05)

### Test selection

A **two-proportion z-test** (two-tailed) is applied to each cohort transition using a pooled-proportion z-statistic computed from `scipy.stats.norm`. This tests the null hypothesis that the proficiency rate did not change between baseline and follow-up:

```
H₀: p_baseline = p_followup
H₁: p_baseline ≠ p_followup
```

### Inputs

Because OSSE files contain both a percentage and a student count (Total Count), we reconstruct the number of proficient students as:

```
count_proficient = round(pct / 100 × total_count)
```

Both `count_proficient` and `total_count` are passed as the numerator and denominator for each proportion.

The pooled z-statistic is:

```
p_pool = (c1 + c2) / (n1 + n2)
z      = (p1 - p2) / sqrt(p_pool × (1 - p_pool) × (1/n1 + 1/n2))
p      = 2 × (1 - Φ(|z|))
```

where `Φ` is the standard normal CDF (`scipy.stats.norm.sf`).

### Output columns added to `cohort_growth_detail.csv`

| Column | Type | Description |
|--------|------|-------------|
| `p_value` | float | Two-tailed p-value from the proportion z-test (rounded to 4 decimal places). `NaN` if the test could not run (missing counts, zero denominators, scipy unavailable). |
| `significant` | bool | `True` if `p_value < 0.05`, `False` otherwise. |

### Output column added to `cohort_growth_summary.csv`

| Column | Type | Description |
|--------|------|-------------|
| `pct_significant_transitions` | float | Percentage of a school's cohort transitions that are statistically significant at p < 0.05 (e.g., 66.7 means 2 of 3 transitions were significant). |

### Multiple-comparison caveat

With thousands of school × subject × subgroup × transition combinations, applying a threshold of p < 0.05 without correction will yield false positives by chance. The `significant` flag is therefore intended as a **descriptive screening tool** — a first pass to surface transitions that may be real — not as a family-wise claim.

If formal inference is required (e.g., for publication), consider:
- **Bonferroni correction**: divide α by the number of tests
- **Benjamini–Hochberg FDR**: controls the expected fraction of false discoveries

### Interpretation guidance

- A **large pp_growth with significant = True** suggests a credible improvement (or decline).
- A **large pp_growth with significant = False** may reflect a small student cohort (low power) rather than a null effect.
- A **small pp_growth with significant = True** indicates statistical precision but may not be practically meaningful.

---

## Validation Benchmark

All pipeline changes are validated against four manually computed Stuart-Hobson transitions (ELA and Math, Gr6→Gr7 and Gr7→Gr8, 2022→2023). Values must match within ±0.1 percentage points of the manual spreadsheet (`StuartHobson_Manual_Growth_example.xlsx`). See Decision D-004.

---

## Equity Gap Analysis (src/equity_gap_analysis.py)

### Purpose

The equity gap analysis extends the cohort growth output to surface **achievement gaps** between individual student subgroups and the citywide "All Students" average, and to track whether those gaps are narrowing or widening as cohorts advance a grade.

### Input

`output_data/cohort_growth_detail.csv` (produced by `src/analyze_cohort_growth.py`).

### Method

For every matching school–subject–cohort-transition combination, the script joins subgroup rows against the "All Students" reference row and computes:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| `proficiency_gap` | subgroup `baseline_pct` − All Students `baseline_pct` | Negative = subgroup starts below average |
| `followup_gap` | subgroup `followup_pct` − All Students `followup_pct` | Negative = subgroup ends below average |
| `gap_change` | `followup_gap` − `proficiency_gap` | Positive = gap narrowed; negative = gap widened |
| `growth_gap` | subgroup `pp_growth` − All Students `pp_growth` | Positive = subgroup grew faster than average |

### Outputs

| File | Description |
|------|-------------|
| `equity_gap_detail.csv` | One row per school / subgroup / cohort transition. All columns from `cohort_growth_detail.csv` plus the four gap metrics above and an `is_disadvantaged` flag (True for: Black or African American, Hispanic/Latino of any race, EL Active, Econ Dis, Students with Disabilities). |
| `equity_gap_summary.csv` | Aggregated to school / subject / subgroup level. Includes `avg_proficiency_gap`, `avg_followup_gap`, `avg_gap_change`, `avg_growth_gap`, `n_transitions`, and `pct_narrowing` (% of transitions where `gap_change > 0`). |

### Limitations

- Gaps are computed against the school-level "All Students" row, not the citywide "All Students" average. This means a 0 proficiency gap does not imply equity with the city; it means the subgroup performs at the same level as all students *at that school*.
- Subgroups suppressed by OSSE (small N) have no rows in the detail file and are therefore absent from the equity analysis.
- The `is_disadvantaged` flag is based on conventional DC policy categories and is for screening purposes only.
