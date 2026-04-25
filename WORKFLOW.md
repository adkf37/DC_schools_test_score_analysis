# Project Workflow - DC Schools Test Score Analysis

## ⚠️ Current Status: Return to Build (not ready for final handoff)

As of the 2026-04-25 closeout review, a fresh-clone smoke test does **not** complete successfully:

- `python -m pip install -r requirements.txt` ✅
- `python -m py_compile src/*.py app/*.py inspect_data.py` ✅
- `python src/load_clean_data.py` ❌
- `python src/analyze_cohort_growth.py` ❌ (blocked on missing `output_data/combined_all_years.csv`)

The current blocker is an input-file contract mismatch: `src/load_clean_data.py` expects four exact workbook names in top-level `input_data/`, while the repo snapshot contains differently named files under `input_data/School and Demographic Group Aggregation/` and no exact 2024-25 workbook match. Treat the workflow below as the **intended** pipeline once that blocker is fixed, not as a claim that the current repository snapshot is handoff-ready.

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

### 1. Data Preparation ✅ COMPLETE
**File**: `src/load_clean_data.py`

**What it does:**
- Reads the 4 XLSX files (2021-22, 2022-23, 2023-24, 2024-25)
- Handles different schemas across years
- **Normalizes grade names** (e.g., "Grade 6-All" → "Grade 6", "HS-Algebra I" → "Algebra I")
- **Deduplicates** rows (prefers specific assessment over "All" aggregates)
- Adds numeric `Grade Number` column for cohort tracking

**Output**: `output_data/combined_all_years.csv`
- 4 years of data (2022-2025)
- 236 schools
- 2 subjects (ELA, Math)
- All student groups

```bash
python src/load_clean_data.py
```

---

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

### 3. Same-Grade Growth Analysis ✅ READY
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

### 4. Interactive Dashboard ✅ ENHANCED
**File**: `app/app_simple.py`

**Features:**
- **Same-grade time series** – school performance over time
- **Cohort growth charts** – bar charts and box plots of cohort growth
- Filter by subject, student group, schools, year range
- Map view (if school_locations.csv available)

```bash
python app/app_simple.py
```
Then open: http://127.0.0.1:8050/

---

## 🚀 Quick Start Guide

```bash
# 1. Combine the Excel files (if not done already)
python src/load_clean_data.py

# 2. Run cohort growth analysis (the main analysis!)
python src/analyze_cohort_growth.py

# 3. (Optional) Run same-grade year-over-year analysis
python src/analyze_growth.py

# 4. Launch the interactive dashboard
python app/app_simple.py
```

### Key Files

| File | Purpose |
|------|---------|
| `src/load_clean_data.py` | Combine raw Excel → `combined_all_years.csv` |
| `src/analyze_cohort_growth.py` | **Cohort growth** (Grade N→N+1) — main analysis |
| `src/analyze_growth.py` | Same-grade YoY growth |
| `app/app_simple.py` | Interactive dashboard |
| `output_data/cohort_growth_detail.csv` | Every cohort transition |
| `output_data/cohort_growth_summary.csv` | School-level cohort summary |
| `output_data/cohort_growth_pivot.xlsx` | Excel workbook with pivots |
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

2. **Which schools improved the most from 2022 to 2025?**
   → Sort `school_growth_by_school_subject.csv` by `growth_first_to_last`

---

## 💡 Next Steps

### Required before another validation / closeout pass:

1. **Fix the input-data contract**
   - Update `src/load_clean_data.py` to recognize the repo's actual workbook layout/names, or
   - Place/rename the OSSE files so the documented loader command succeeds

2. **Resolve the 2024-25 source file**
   - Add the required workbook or document the accepted replacement filename

3. **Regenerate core outputs**
   - Run `python src/load_clean_data.py`
   - Run `python src/analyze_cohort_growth.py`

4. **Re-run evidence checks**
   - Verify Stuart-Hobson benchmark values
   - Verify Task 05 significance columns in generated outputs
   - Only then proceed to dashboard validation / final handoff

---

## 🔧 Troubleshooting

### "Permission denied" error when saving:
- Close the CSV file if it's open in Excel
- OneDrive sometimes locks files - save to a local folder if needed

### "File not found" error:
- Make sure you run `load_clean_data.py` first
- Check that the Excel files are in `input_data/`

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

- **Total Records**: 398,809
- **Years**: 2022, 2023, 2024, 2025 (4 years)
- **Schools**: 236 unique schools
- **Subjects**: ELA, Math
- **Student Groups**: Multiple demographic and program groups
- **Metrics**: Percent Meeting/Exceeding expectations

**You're all set to start analyzing! 🎉**
