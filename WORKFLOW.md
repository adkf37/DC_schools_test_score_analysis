# Project Workflow - DC Schools Test Score Analysis

## ✅ Current Status: Ready to Analyze!

You now have a **clean, streamlined workflow** with 3 simple scripts.

---

## 📊 Where You Are in the Project

### 1. Data Preparation ✅ COMPLETE
**File**: `src/load_clean_data.py`

**What it does:**
- Reads the 4 XLSX files (2021-22, 2022-23, 2023-24, 2024-25)
- Handles different schemas across years
- Normalizes column names
- Combines into a single clean dataset

**Output**: `output_data/combined_all_years.csv` (398,809 rows)
- 4 years of data (2022-2025)
- 236 schools
- 2 subjects (ELA, Math)
- All student groups

**Run it:**
```bash
python src/load_clean_data.py
```

---

### 2. Growth Analysis ✅ READY
**File**: `src/analyze_growth.py`

**What it does:**
- Reads the combined CSV
- Parses percent values (handles suppressed data like "DS", "n<10")
- Computes year-over-year growth by school/subject/subgroup
- Creates summary tables

**Outputs:**
- `school_growth_full.csv` - Detailed growth metrics (209,617 rows)
- `school_growth_by_school_subject.csv` - School-level summary (8,034 rows)

**Run it:**
```bash
python src/analyze_growth.py
```

**Key Features:**
- First-to-last growth (2022 → 2025)
- Year-over-year growth (2024 → 2025)
- Aggregated by school, subject, and student group

---

### 3. Interactive Dashboard ✅ READY
**File**: `app/app_simple.py`

**What it does:**
- Interactive Dash web app for exploring the data
- Filter by subject, student group, schools
- Visualizations:
  - Time series trends
  - Bar charts of top schools
  - Map view (if you add school_locations.csv)

**Run it:**
```bash
python app/app_simple.py
```

Then open: http://127.0.0.1:8050/

---

## 🎯 What's Working

### Data Loading:
✅ All 4 Excel files successfully loaded
✅ 398,809 records combined
✅ Column schemas normalized
✅ Years: 2022, 2023, 2024, 2025

### Growth Analysis:
✅ Percent values parsed correctly
✅ Suppressed data handled (DS, n<10, etc.)
✅ Growth metrics calculated
✅ School-level summaries created

### Visualization:
✅ Dash app loads the combined CSV
✅ Filters work (subject, student group, schools, years)
✅ Three interactive charts

---

## 📁 Key Files

### Input Files (in `input_data/`):
- `2021-22 School Level PARCC and MSAA Data.xlsx`
- `2022-23 School Level PARCC and MSAA Data_9_5.xlsx`
- `DC Cape Scores 2023-2024.xlsx`
- `2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx`

### Scripts (in `src/`):
1. **`load_clean_data.py`** - Combine raw Excel files → CSV
2. **`analyze_growth.py`** - Calculate growth metrics
3. **`app_simple.py`** (in `app/`) - Interactive dashboard

### Output Files (in `output_data/`):
- **`combined_all_years.csv`** - Clean combined dataset (all years)
- **`school_growth_full.csv`** - Detailed growth analysis
- **`school_growth_by_school_subject.csv`** - School-level summary

---

## 🚀 Quick Start Guide

### To analyze the data:
```bash
# 1. Combine the Excel files (if not done already)
python src/load_clean_data.py

# 2. Calculate growth metrics
python src/analyze_growth.py

# 3. Launch the interactive dashboard
python app/app_simple.py
```

### To explore specific questions:
- **View the combined data**: Open `output_data/combined_all_years.csv`
- **See growth trends**: Open `output_data/school_growth_by_school_subject.csv`
- **Interactive exploration**: Run `python app/app_simple.py`

---

## 📈 Example Analysis Questions You Can Answer

With the current setup, you can:

1. **Track school performance over time**
   - Which schools improved the most from 2022 to 2025?
   - Which schools declined?

2. **Compare subjects**
   - How does Math performance compare to ELA?
   - Which schools excel in one but not the other?

3. **Analyze student groups**
   - How do different demographic groups perform?
   - Which schools have the smallest achievement gaps?

4. **Year-over-year changes**
   - What was the impact of the most recent year?
   - Which schools had the biggest jumps?

---

## 💡 Next Steps

### If you want to dive deeper:

1. **Add statistical tests**
   - Test if growth differences are statistically significant
   - Identify outliers

2. **More visualizations**
   - Heatmaps of growth by school
   - Distribution plots
   - Scatter plots comparing subjects

3. **Export for presentation**
   - Generate summary reports
   - Create PowerPoint-ready charts
   - Excel workbooks with formatted tables

4. **Filter and focus**
   - Analyze specific schools of interest
   - Compare charter vs. traditional public schools
   - Look at specific grades

---

## 🔧 Troubleshooting

### "Permission denied" error when saving:
- Close the CSV file if it's open in Excel
- OneDrive sometimes locks files - save to a local folder if needed

### "File not found" error:
- Make sure you run `load_clean_data.py` first
- Check that the Excel files are in `input_data/`

### Dash app won't start:
- Install required packages: `pip install dash plotly`
- Make sure `combined_all_years.csv` exists

---

## 📊 Your Data at a Glance

- **Total Records**: 398,809
- **Years**: 2022, 2023, 2024, 2025 (4 years)
- **Schools**: 236 unique schools
- **Subjects**: ELA, Math
- **Student Groups**: Multiple demographic and program groups
- **Metrics**: Percent Meeting/Exceeding expectations

**You're all set to start analyzing! 🎉**
