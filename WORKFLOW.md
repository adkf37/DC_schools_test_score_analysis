# Project Workflow - DC Schools Test Score Analysis

## ✅ Current Status: Loop 15 Build Complete — School Consistency Analysis Added to Smoke Path

As of 2026-04-30, Loop 15 Build is complete. `src/school_consistency_analysis.py`, the consistency dashboard figure, and the 14-sheet `summary_report.xlsx` are now part of the documented smoke path:

- `python -m pip install -r requirements.txt` ✅
- `python -m pip install dash plotly` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_wide_format_data.py` ✅ ← use this when normalized OSSE files are unavailable
- `python src/analyze_cohort_growth.py` ✅
- `python src/equity_gap_analysis.py` ✅
- `python src/generate_school_rankings.py` ✅
- `python src/proficiency_trend_analysis.py` ✅
- `python src/geographic_equity_analysis.py` ✅
- `python src/yoy_growth_analysis.py` ✅
- `python src/covid_recovery_analysis.py` ✅ ← **new in loop 10**
- `python src/school_trajectory_analysis.py` ✅ ← **new in loop 11**
- `python src/school_type_analysis.py` ✅ ← **new in loop 12**
- `python src/grade_level_analysis.py` ✅ ← **new in loop 13**
- `python src/subgroup_trend_analysis.py` ✅ ← **new in loop 14**
- `python src/school_consistency_analysis.py` ✅ ← **new in loop 15**
- `python src/generate_summary_report.py` ✅ ← updated to 14 sheets in loop 15
- `python app/app_simple.py` + `GET /`, `/_dash-layout`, `/_dash-dependencies`, `POST /_dash-update-component` ✅

**Two data pipeline options:**

| Script | Input files | Use when |
|--------|------------|---------|
| `src/load_clean_data.py` | Normalized OSSE files (4 exact workbook names in `input_data/`) | You have downloaded the normalized school-level PARCC/DCCAPE files from OSSE |
| `src/load_wide_format_data.py` | Wide-format demographic files in `input_data/School and Demographic Group Aggregation/` | Using files already in the repository (2015-16 through 2018-19, plus 2021-22 through 2023-24) |

> **Note:** `src/load_clean_data.py` still expects the four normalized OSSE filenames (see Task 01). The wide-format loader (`src/load_wide_format_data.py`) works with the files already committed to the repo.

---

## 📊 Two Types of Growth Analysis

### Cohort Growth (NEW – replicates the manual Stuart-Hobson example)
Tracks the **same group of students** as they advance from Grade N to Grade N+1:

```
Grade 6 in 2022 → Grade 7 in 2023  (same students, one year later)
Grade 7 in 2022 → Grade 8 in 2023
```

This answers: **"Are students at this school making progress?"**

### Same-Grade Year-over-Year
Compares performance at the **same grade level** across years:

```
Grade 6 in 2022 vs Grade 6 in 2023  (different students, same grade)
```

This answers: **"Is this grade getting stronger over time?"**

---

## 📁 Pipeline Steps

### 1. Data Preparation
**File**: `src/load_clean_data.py` (normalized OSSE) or `src/load_wide_format_data.py` (wide-format)

#### Option A — Normalized OSSE Files (`src/load_clean_data.py`)

**What it does:**
- Reads the 4 XLSX files (2021-22, 2022-23, 2023-24, 2024-25) — must be downloaded from OSSE
- Handles different schemas across years
- **Normalizes grade names** (e.g., "Grade 6-All" → "Grade 6", "HS-Algebra I" → "Algebra I")
- **Deduplicates** rows (prefers specific assessment over "All" aggregates)
- Adds numeric `Grade Number` column for cohort tracking

```bash
python src/load_clean_data.py
```

#### Option B — Wide-Format Demographic Files (`src/load_wide_format_data.py`) ✅ Operational

**What it does:**
- Discovers XLSX files automatically under `input_data/` (searches all subdirectories)
- Reads the "School and Demographic Group Aggregation" workbooks (already in the repo)
- Converts wide format (ELA + Math side-by-side, separate sheets per demographic) to long format
- Uses dynamic column-name detection to handle the extra "Subgroup" column in demographic sheets
- Produces the same `combined_all_years.csv` format as Option A

**Available data:**
- 2015-16 PARCC (grades 3-8, older descriptive demographic sheet names)
- 2016-17 PARCC (grades 3-8, older descriptive demographic sheet names)
- 2017-18 PARCC (grades 3-8, no MSAA columns in source workbook)
- 2018-19 PARCC (grades 3-8)
- 2021-22 PARCC (grades 3-8, 13 demographic sheets)
- 2022-23 PARCC (grades 3-8, 13 demographic sheets)
- 2023-24 DCCAPE (grades 3-8, 13 demographic sheets)

```bash
python src/load_wide_format_data.py
```

**Output**: `output_data/combined_all_years.csv`
- 7 years of data (2016, 2017, 2018, 2019, 2022, 2023, 2024, using the wide-format option)
- 211 schools with cohort-trackable grade transitions (212 school names in the filtered cohort input)
- 2 subjects (ELA, Math)
- 12 student groups (All Students + demographic/program breakdowns)

### 2. Cohort Growth Analysis ✅ NEW
**File**: `src/analyze_cohort_growth.py`

**What it does:**
- Reads the combined CSV
- Matches Grade N / Year Y with Grade N+1 / Year Y+1 for each school
- Computes percentage-point change in proficiency for each cohort transition
- Creates summary tables and an Excel workbook with pivots
- Validates results against the Stuart-Hobson manual example

**Outputs:**
- `cohort_growth_detail.csv` – One row per school/subject/subgroup/transition
- `cohort_growth_summary.csv` – Aggregated school-level metrics
- `cohort_growth_pivot.xlsx` – Excel workbook with 6 sheets:
  - All Students Summary (sorted by growth)
  - Full Summary (all subgroups)
  - All Students Detail (every transition)
  - ELA Cohort Pivot (schools × transitions)
  - Math Cohort Pivot (schools × transitions)
  - Full Detail

```bash
python src/analyze_cohort_growth.py
```

**Key Columns in Detail Output:**
| Column | Description |
|--------|-------------|
| `baseline_grade` | Starting grade (e.g., 6) |
| `baseline_year` | Starting year (e.g., 2022) |
| `baseline_pct` | % Meeting/Exceeding at start |
| `followup_grade` | Next grade (e.g., 7) |
| `followup_year` | Next year (e.g., 2023) |
| `followup_pct` | % Meeting/Exceeding at follow-up |
| `pp_growth` | Percentage-point change |
| `transition_label` | e.g., "Gr6→Gr7 (2022→2023)" |

---

### 3. Equity Gap Analysis ✅ VALIDATED FOR LOOP 2
**File**: `src/equity_gap_analysis.py`

**What it does:**
- Reads `cohort_growth_detail.csv`
- Compares subgroup cohort performance against each school's "All Students" row
- Computes proficiency-gap and growth-gap metrics
- Produces summary tables used by the dashboard's two additional equity charts

**Outputs:**
- `equity_gap_detail.csv`
- `equity_gap_summary.csv`

```bash
python src/equity_gap_analysis.py
```

---

### 3b. School Rankings ✅ VALIDATED IN LOOP 3
**File**: `src/generate_school_rankings.py`

**What it does:**
- Reads `cohort_growth_summary.csv` and `equity_gap_summary.csv`
- Ranks all schools by average cohort growth for the "All Students" subgroup
- Ranks schools by effectiveness at narrowing equity gaps for disadvantaged subgroups
  (Black or African American, Hispanic/Latino, EL Active, Econ Dis, Students with Disabilities)
- Prints top-10 / bottom-10 tables for both ELA and Math

**Outputs:**
- `school_rankings.csv` – Schools ranked by avg cohort PP growth (All Students)
- `school_equity_rankings.csv` – Schools ranked by avg gap-change for disadvantaged subgroups

```bash
python src/generate_school_rankings.py
```

---

### 4. Same-Grade YoY Growth Analysis ✅ VALIDATED IN LOOP 9
**File**: `src/yoy_growth_analysis.py`

**What it does:**
- Computes year-over-year change at the same grade level for every school / grade / subject / subgroup
- Uses only consecutive year pairs (2016→2017, 2017→2018, 2018→2019, 2022→2023, 2023→2024) and excludes the COVID gap
- Writes standalone outputs without re-running the cohort pipeline internally

**Outputs:**
- `yoy_growth_detail.csv` – Detailed same-grade YoY metrics
- `yoy_growth_summary.csv` – School-level summary

```bash
python src/yoy_growth_analysis.py
```

---

### 4b. COVID Recovery Analysis ✅ VALIDATED IN LOOP 10
**File**: `src/covid_recovery_analysis.py`

**What it does:**
- Compares pre-COVID 2019 proficiency with 2022 post-disruption results and 2024 recovery levels
- Computes COVID impact, recovery progress, and net change vs. pre-COVID for every school / subject / subgroup meeting the minimum-N rules
- Produces a school-level recovery-status summary used by both the dashboard and the policy workbook

**Outputs:**
- `covid_recovery_detail.csv` – Detailed 2019/2022/2024 comparison rows
- `covid_recovery_summary.csv` – School-level All Students recovery-status summary

```bash
python src/covid_recovery_analysis.py
```

**Current handoff finding:**
- Citywide ELA averages show a −3.94 pp COVID impact, +1.75 pp recovery, and −2.15 pp net gap vs. pre-COVID; Math shows −8.56 pp impact, +3.17 pp recovery, and −5.43 pp net gap.

---

### 4c. School Trajectory Analysis ✅ VALIDATED IN LOOP 11
**File**: `src/school_trajectory_analysis.py`

**What it does:**
- Fits a simple OLS line to each school's All Students proficiency history across the available wide-format years
- Computes years with data, first/last proficiency, average proficiency, total change, slope, and R²
- Assigns each school / subject pair to a trajectory class used by both the dashboard and policy workbook

**Output:**
- `school_trajectory_classification.csv` – 424 school × subject rows with trajectory metrics and classes

```bash
python src/school_trajectory_analysis.py
```

**Current handoff finding:**
- Citywide average trend slopes are +0.065 pp/yr in ELA and −0.656 pp/yr in Math; Whittier Elementary School is the strongest improver in both subjects.

---

### 4d. School Type Analysis ✅ VALIDATED IN LOOP 12
**File**: `src/school_type_analysis.py`

**What it does:**
- Classifies each school into a grade-band type using the grades it serves across the available wide-format years
- Computes average proficiency-by-year trends for each school type by subject
- Summarizes school-type COVID impact, recovery, and average cohort growth for both dashboard and workbook handoff

**Outputs:**
- `school_type_by_school.csv` – 251 school × type rows
- `school_type_proficiency.csv` – 70 school-type × subject × year proficiency rows
- `school_type_summary.csv` – 10 school-type × subject summary rows

```bash
python src/school_type_analysis.py
```

**Current handoff finding:**
- Elementary schools lead average proficiency in both ELA (31.85%) and Math (30.91%); Elementary-Middle schools have the strongest ELA cohort growth (+6.56 pp/yr).

---

### 4e. Grade-Level Analysis ✅ VALIDATED IN LOOP 13
**File**: `src/grade_level_analysis.py`

**What it does:**
- Computes average and median proficiency-by-year for each grade of enrollment (Grade 3–Grade 8 and High School) by subject
- Summarizes grade-level COVID impact, recovery, and average same-grade YoY growth for workbook and dashboard handoff
- Supports a citywide grade trend figure plus selected-school overlays against citywide grade averages

**Outputs:**
- `grade_level_proficiency.csv` – 98 grade × subject × year rows
- `grade_level_summary.csv` – 14 grade × subject summary rows

```bash
python src/grade_level_analysis.py
```

**Current handoff finding:**
- ELA average proficiency peaks at Grade 4 (32.74%) and bottoms at Grade 6 (26.04%); Math peaks at Grade 3 (33.76%) and bottoms at High School (13.17%).

---

### 4f. Subgroup Trend Analysis ✅ VALIDATED IN LOOP 14
**File**: `src/subgroup_trend_analysis.py`

**What it does:**
- Computes average and median proficiency-by-year for each student subgroup by subject
- Summarizes subgroup COVID impact, recovery, and average same-grade YoY growth for workbook and dashboard handoff
- Supports a citywide subgroup trend figure plus selected-school overlays against citywide subgroup averages

**Outputs:**
- `subgroup_proficiency.csv` – 152 subgroup × subject × year rows
- `subgroup_summary.csv` – 22 subgroup × subject summary rows

```bash
python src/subgroup_trend_analysis.py
```

**Current handoff finding:**
- ELA average proficiency peaks at White (83.82%) and bottoms at Students with Disabilities (7.92%); Math peaks at White (77.06%) and bottoms at Students with Disabilities (6.46%).

---

### 5. Interactive Dashboard ✅ VALIDATED FOR THE CURRENT LOOP
**File**: `app/app_simple.py`

**Features:**
- **Same-grade time series** – school performance over time
- **Cohort growth charts** – bar charts and box plots of cohort growth
- **Equity gap charts** – proficiency gap vs All Students, gap-change analysis
- **Grade × Year heatmap** – school-specific or citywide proficiency grid across years
- **Baseline Proficiency vs. Cohort Growth scatter** – school-level baseline-vs-growth view with significance/transition context
- **COVID recovery chart** – citywide impact-vs-recovery scatter or selected-school milestone bar chart
- **School trajectory chart** – school-level slope-vs-average-proficiency scatter coloured by trajectory class
- **School type chart** – school-type proficiency trends citywide or selected-school overlays coloured by type
- **Grade-level chart** – citywide average proficiency by grade over time or selected-school grade overlays
- **Subgroup trend chart** – citywide average proficiency by student subgroup over time or selected-school subgroup overlays
- Filter by subject, student group, schools, year range
- Map view (requires `input_data/school_locations.csv` — included in Loop 3 and still validated in Loop 5)

```bash
python app/app_simple.py
```
Then open: http://127.0.0.1:8050/

**Validated closeout evidence (Loop 14, example callback filters = Subject: Math; Student Group: All Students):**
- App startup succeeds against regenerated CSVs
- `GET /`, `/_dash-layout`, and `/_dash-dependencies` return successfully
- A live `POST /_dash-update-component` request returns all sixteen figures, including the Grade × Year heatmap, Baseline Proficiency vs. Cohort Growth scatter plot, Geographic Equity chart, YoY growth chart, COVID recovery chart, school trajectory chart, school type chart, grade-level chart, and subgroup trend chart
- `input_data/school_locations.csv` is now present, and the map returns a real `School Performance Map` with 113 plotted schools in the current 2024 Math / All Students view (`DC Public Schools` is intentionally omitted because it is an aggregate row)

---

### 5b. Proficiency Trend Analysis ✅ VALIDATED IN LOOP 5
**File**: `src/proficiency_trend_analysis.py`

**What it does:**
- Reads `combined_all_years.csv`
- Filters to school-level proficiency rows
- Produces a long-format grade × year dataset for dashboard heatmaps
- Supports either school-specific or citywide average views in the dashboard

**Output:**
- `proficiency_trends.csv` – 25,629 school × year × subject × grade × subgroup rows

```bash
python src/proficiency_trend_analysis.py
```

---

### 5c. Policy Summary Report ✅ VALIDATED IN LOOP 14
**File**: `src/generate_summary_report.py`

**What it does:**
- Reads all analytical output CSVs (`cohort_growth_summary.csv`, `school_rankings.csv`, `school_equity_rankings.csv`, `equity_gap_summary.csv`, `proficiency_trends.csv`, `geographic_equity_by_quadrant.csv`, `yoy_growth_summary.csv`, `covid_recovery_summary.csv`, `school_trajectory_classification.csv`, `school_type_summary.csv`, `grade_level_summary.csv`, `subgroup_summary.csv`, `school_consistency.csv`)
- Produces a formatted 14-sheet Excel workbook for policy stakeholders
- Applies header formatting, alternating row shading, and colour-coded growth values

**Output:**
- `summary_report.xlsx` — 14 sheets: Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory, Geographic Equity, YoY Growth, COVID Recovery, School Trajectories, School Types, Grade Levels, Subgroups, Consistency

```bash
python src/generate_summary_report.py
```

---

### 5d. Geographic Equity Analysis ✅ VALIDATED IN LOOP 8
**File**: `src/geographic_equity_analysis.py`

**What it does:**
- Joins `input_data/school_locations.csv` to the proficiency-trend and cohort-growth outputs
- Produces school-level and quadrant-level geographic equity comparisons for NE / NW / SE / SW
- Computes gap-vs-NW metrics and feeds both the dashboard and the summary workbook

**Outputs:**
- `geographic_equity_by_school.csv` – 210 school × subject rows with Quadrant and Neighborhood
- `geographic_equity_by_quadrant.csv` – 8 quadrant × subject rows with proficiency and cohort-growth summaries

```bash
python src/geographic_equity_analysis.py
```

**Current handoff finding:**
- NW average ELA proficiency is 42.71% versus 24.09% in NE and 20.15% in SE.

---

## 🚀 Quick Start Guide

```bash
# 1. Combine the in-repo Excel files
python src/load_wide_format_data.py

# 2. Run cohort growth analysis (the main analysis!)
python src/analyze_cohort_growth.py

# 3. Generate equity-gap outputs
python src/equity_gap_analysis.py

# 4. Generate school rankings
python src/generate_school_rankings.py

# 5. Generate proficiency trends for the dashboard heatmap
python src/proficiency_trend_analysis.py

# 6. Generate geographic equity outputs
python src/geographic_equity_analysis.py

# 7. Generate same-grade YoY outputs
python src/yoy_growth_analysis.py

# 8. Generate COVID recovery outputs
python src/covid_recovery_analysis.py

# 9. Generate school trajectory outputs
python src/school_trajectory_analysis.py

# 10. Generate school type outputs
python src/school_type_analysis.py

# 11. Generate grade-level outputs
python src/grade_level_analysis.py

# 12. Generate subgroup-trend outputs
python src/subgroup_trend_analysis.py

# 13. Generate school performance consistency outputs
python src/school_consistency_analysis.py

# 14. Generate formatted Excel policy summary report
python src/generate_summary_report.py

# 15. (Optional) Launch the interactive dashboard
python app/app_simple.py
```

### Key Files

| File | Purpose |
|------|---------|
| `src/load_wide_format_data.py` | Combine in-repo wide-format Excel files → `combined_all_years.csv` |
| `src/load_clean_data.py` | Combine normalized OSSE Excel files → `combined_all_years.csv` |
| `src/analyze_cohort_growth.py` | **Cohort growth** (Grade N→N+1) — main analysis |
| `src/equity_gap_analysis.py` | Equity-gap metrics derived from cohort-growth output |
| `src/generate_school_rankings.py` | School rankings by cohort growth and equity-gap change |
| `src/proficiency_trend_analysis.py` | Grade × year proficiency grid used by the dashboard heatmap |
| `src/geographic_equity_analysis.py` | Geographic equity outputs and quadrant comparisons |
| `src/school_trajectory_analysis.py` | Multi-year OLS trend slopes and trajectory classes |
| `src/school_type_analysis.py` | Grade-band school type analysis and type-level performance summaries |
| `src/grade_level_analysis.py` | Grade-level proficiency, COVID impact, recovery, and YoY summaries |
| `src/subgroup_trend_analysis.py` | Student subgroup proficiency, COVID impact, recovery, and YoY summaries |
| `src/school_consistency_analysis.py` | School performance consistency: std deviation, CV, and consistency class per school × subject |
| `src/generate_summary_report.py` | **Formatted Excel policy-summary report** (14-sheet workbook) |
| `src/yoy_growth_analysis.py` | Same-grade YoY growth |
| `src/covid_recovery_analysis.py` | COVID impact and recovery analysis |
| `app/app_simple.py` | Interactive dashboard |
| `input_data/school_locations.csv` | Geocoordinates for 115 DC public schools (enables map) |
| `output_data/cohort_growth_detail.csv` | Every cohort transition |
| `output_data/cohort_growth_summary.csv` | School-level cohort summary |
| `output_data/cohort_growth_pivot.xlsx` | Excel workbook with pivots |
| `output_data/equity_gap_detail.csv` | School / subgroup / transition gap metrics |
| `output_data/equity_gap_summary.csv` | Aggregated equity-gap metrics |
| `output_data/school_rankings.csv` | Schools ranked by avg PP growth (All Students) |
| `output_data/school_equity_rankings.csv` | Schools ranked by equity-gap narrowing |
| `output_data/proficiency_trends.csv` | Grade × year proficiency trends for the heatmap |
| `output_data/geographic_equity_by_school.csv` | School × subject geographic equity output |
| `output_data/geographic_equity_by_quadrant.csv` | Quadrant × subject geographic equity summary |
| `output_data/yoy_growth_detail.csv` | Same-grade YoY growth detail |
| `output_data/yoy_growth_summary.csv` | Same-grade YoY growth summary |
| `output_data/covid_recovery_detail.csv` | COVID impact and recovery detail |
| `output_data/covid_recovery_summary.csv` | COVID recovery status summary |
| `output_data/school_trajectory_classification.csv` | School-level trend slopes and trajectory classes |
| `output_data/school_type_by_school.csv` | School-level type assignments |
| `output_data/school_type_proficiency.csv` | School-type proficiency trends |
| `output_data/school_type_summary.csv` | School-type summary metrics |
| `output_data/grade_level_proficiency.csv` | Grade-level proficiency trends |
| `output_data/grade_level_summary.csv` | Grade-level summary metrics |
| `output_data/subgroup_proficiency.csv` | Subgroup proficiency trends |
| `output_data/subgroup_summary.csv` | Subgroup summary metrics |
| `output_data/summary_report.xlsx` | **Policy summary workbook — 13 formatted sheets** |
| `output_data/combined_all_years.csv` | Clean combined source data |

---

## 📈 Example Analysis Questions

### Cohort Growth Questions (NEW):
1. **Which schools had the biggest cohort growth?**
   → Open `cohort_growth_summary.csv`, sort by `avg_pp_growth`

2. **How did Stuart-Hobson's 6th graders do when they became 7th graders?**
   → Filter `cohort_growth_detail.csv` for Stuart-Hobson, Gr6→Gr7

3. **Which schools are accelerating student learning?**
   → Look at schools where `avg_pp_growth > 0` across multiple transitions

4. **Are there racial achievement gaps in growth?**
   → Compare cohort growth by `Student Group Value` within a school

5. **Which grade transitions show the most/least growth?**
   → Pivot the detail data by `transition_label`

### Same-Grade Questions:
1. **Is Grade 6 ELA citywide improving?**
   → Filter `yoy_growth_detail.csv` for `grade == "Grade 6"` and `Subject == "ELA"`

2. **Which schools improved the most from 2022 to 2024 in the in-repo data?**
   → Filter `yoy_growth_summary.csv` to the desired subject/subgroup and sort by `avg_pp_growth`

### COVID Recovery Questions:
1. **Which schools are still below pre-COVID performance?**
   → Filter `covid_recovery_summary.csv` for `recovery_status == "Still Below Pre-COVID"`

2. **Which schools recovered the fastest after 2022?**
   → Sort `covid_recovery_detail.csv` or `covid_recovery_summary.csv` by recovery gain within the desired subject

---

## 💡 Next Steps

### Required before the next Build / Validate cycle:

1. **Choose the next Build target**
    - Restore the full normalized-data / 2024-25 ingestion path, or
    - Finish the still-blocked browser-console / manual dashboard checks for the current 16-figure dashboard, or
    - Deliberately narrow the backlog to the verified wide-format scope

2. **If pursuing the normalized-data path**
    - Update `src/load_clean_data.py` to recognize the repo's actual workbook layout/names, or
    - Place/rename the OSSE files so the documented loader command succeeds

3. **If pursuing the dashboard path**
     - Run `python app/app_simple.py`
     - Confirm the browser console remains clean during manual interaction with the regenerated CSV, equity, rankings, map, heatmap, scatter, YoY, COVID recovery, school trajectory, school type, grade-level, and subgroup-trend outputs

4. **Re-run evidence checks**
   - Verify Stuart-Hobson benchmark values
   - Verify Task 05 significance columns in generated outputs
   - Only then proceed to the next validation / closeout pass

---

## 🔧 Troubleshooting

### "Permission denied" error when saving:
- Close the CSV file if it's open in Excel
- OneDrive sometimes locks files - save to a local folder if needed

### "File not found" error:
- For the in-repo data path, run `load_wide_format_data.py` first
- For the normalized-data path, make sure the OSSE Excel files are in `input_data/`

### Cohort growth shows 0 transitions:
- Ensure `combined_all_years.csv` has at least 2 consecutive years of data
- Check that grade names are consistent (script normalizes them automatically)
- 2025 data uses "Grade 6-All" format – the loader now normalizes this

### Dash app won't start:
- Install required packages: `pip install dash plotly`
- Make sure `combined_all_years.csv` exists
- For cohort charts, run `analyze_cohort_growth.py` first

---

## 📊 Your Data at a Glance

- **Total Records**: 28,069
- **Years**: 2016, 2017, 2018, 2019, 2022, 2023, 2024 (7 in-repo years)
- **Schools**: 251 unique raw schools / 211 cohort-analysis schools
- **Subjects**: ELA, Math
- **Student Groups**: Multiple demographic and program groups
- **Metrics**: Percent Meeting/Exceeding expectations

**You can reproduce the current wide-format analysis loop from a fresh clone; full-project completion still requires another Build cycle.**
