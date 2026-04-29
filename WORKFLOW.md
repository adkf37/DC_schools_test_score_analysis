# Project Workflow - DC Schools Test Score Analysis

## ✅ Current Status: Closeout Loop 8 Complete — Geographic Equity Added, Repo Returns to Build

As of 2026-04-29, loop 8 has passed Validate and Closeout for the reproducible in-repo path. `src/geographic_equity_analysis.py` and the 7-sheet `summary_report.xlsx` are now part of the documented smoke path:

- `python -m pip install -r requirements.txt` ✅
- `python -m pip install dash plotly` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_wide_format_data.py` ✅ ← use this when normalized OSSE files are unavailable
- `python src/analyze_cohort_growth.py` ✅
- `python src/equity_gap_analysis.py` ✅
- `python src/generate_school_rankings.py` ✅
- `python src/proficiency_trend_analysis.py` ✅
- `python src/geographic_equity_analysis.py` ✅ ← **new in loop 8**
- `python src/generate_summary_report.py` ✅ ← updated to 7 sheets in loop 8
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

### 4. Same-Grade Growth Analysis ✅ READY
**File**: `src/analyze_growth.py`

**What it does:**
- Computes year-over-year change at the same grade level
- Also calls `analyze_cohort_growth.py` automatically

**Outputs:**
- `school_growth_full.csv` – Detailed same-grade growth metrics
- `school_growth_by_school_subject.csv` – School-level summary

```bash
python src/analyze_growth.py
```

---

### 5. Interactive Dashboard ✅ VALIDATED FOR THE CURRENT LOOP
**File**: `app/app_simple.py`

**Features:**
- **Same-grade time series** – school performance over time
- **Cohort growth charts** – bar charts and box plots of cohort growth
- **Equity gap charts** – proficiency gap vs All Students, gap-change analysis
- **Grade × Year heatmap** – school-specific or citywide proficiency grid across years
- **Baseline Proficiency vs. Cohort Growth scatter** – school-level baseline-vs-growth view with significance/transition context
- Filter by subject, student group, schools, year range
- Map view (requires `input_data/school_locations.csv` — included in Loop 3 and still validated in Loop 5)

```bash
python app/app_simple.py
```
Then open: http://127.0.0.1:8050/

**Validated closeout evidence (Loop 8, example callback filters = Subject: Math; Student Group: All Students):**
- App startup succeeds against regenerated CSVs
- `GET /`, `/_dash-layout`, and `/_dash-dependencies` return successfully
- A live `POST /_dash-update-component` request returns all ten figures, including the Grade × Year heatmap, Baseline Proficiency vs. Cohort Growth scatter plot, and Geographic Equity chart
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

### 5c. Policy Summary Report ✅ VALIDATED IN LOOP 8
**File**: `src/generate_summary_report.py`

**What it does:**
- Reads all analytical output CSVs (`cohort_growth_summary.csv`, `school_rankings.csv`, `school_equity_rankings.csv`, `equity_gap_summary.csv`, `proficiency_trends.csv`, `geographic_equity_by_quadrant.csv`)
- Produces a formatted 7-sheet Excel workbook for policy stakeholders
- Applies header formatting, alternating row shading, and colour-coded growth values

**Output:**
- `summary_report.xlsx` — 7 sheets: Executive Summary, Top Growth (ELA), Top Growth (Math), Top Equity Schools, Proficiency Trends, School Directory, Geographic Equity

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

# 7. Generate formatted Excel policy summary report
python src/generate_summary_report.py

# 8. (Optional) Run same-grade year-over-year analysis
python src/analyze_growth.py

# 9. (Optional) Launch the interactive dashboard
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
| `src/generate_summary_report.py` | **Formatted Excel policy-summary report** (7-sheet workbook) |
| `src/analyze_growth.py` | Same-grade YoY growth |
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
| `output_data/summary_report.xlsx` | **Policy summary workbook — 7 formatted sheets** |
| `output_data/school_growth_full.csv` | Same-grade growth detail |
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
   → Filter `school_growth_full.csv` for Grade 6, ELA

2. **Which schools improved the most from 2022 to 2024 in the in-repo data?**
   → Sort `school_growth_by_school_subject.csv` by `growth_first_to_last`

---

## 💡 Next Steps

### Required before the next Build / Validate cycle:

1. **Choose the next Build target**
      - Restore the full normalized-data / 2024-25 ingestion path, or
       - Finish the still-blocked browser-console / manual dashboard checks for the current 10-figure dashboard

2. **If pursuing the normalized-data path**
   - Update `src/load_clean_data.py` to recognize the repo's actual workbook layout/names, or
   - Place/rename the OSSE files so the documented loader command succeeds

3. **If pursuing the dashboard path**
       - Run `python app/app_simple.py`
       - Confirm the browser console remains clean during manual interaction with the regenerated CSV, equity, rankings, map, heatmap, and scatter outputs

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
