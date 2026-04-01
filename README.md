# DC Schools Test Score Analysis

A lightweight pipeline for comparing DC school test performance across years, subjects, and student groups. The goal is simple: drop raw files in `input_data/`, run one script, and read clean growth tables from `output_data/`.

## Quick start

```bash
pip install pandas openpyxl  # openpyxl only needed for Excel export
python src/test_score_growth.py
```

Place any CSV/XLSX/XLS files under `input_data/` (nested folders are fine). Files are auto-detected and processed as long as the school year appears in the filename (e.g., `2021-22`, `2023_24`, `2025`).

## What the script does

1. **Ingest all source files** – walks the entire `input_data/` tree, ignoring temp files, and reads every CSV/Excel sheet that looks like school-level results.
2. **Standardize schemas** – aligns year-to-year header changes (e.g., `LEA Name` vs `lea_name`, or the 2024–25 `Enrolled Grade or Course` field) and treats suppressed values (`DS`, `<5%`, `n<10`, …) as missing data.
3. **Filter to the performance metric** – keeps “Meeting or Exceeding” metrics when a `Metric` column exists, while earlier files without that column are left untouched.
4. **Compute growth** – produces full-grain pivot tables plus school × subject summaries with both first-to-last and last-vs-previous year deltas.
5. **Write outputs** – saves tidy CSVs (and optionally an Excel workbook) under `output_data/` and a short processing report describing which files were loaded.

## Output files

- `output_data/filtered_data.csv` – rows for the configured subgroup(s) across every loaded year.
- `output_data/school_growth_full.csv` – the wide pivot by school/subject/subgroup with percent, count, and total count metrics plus growth columns.
- `output_data/school_growth_by_school_subject.csv` – school × subject × subgroup summary with growth metrics.
- `output_data/processing_report.txt` – a log-style recap of what was read and any issues encountered.
- (Optional) `output_data/school_growth_pivot.xlsx` – Excel workbook containing the two main tables; enable by uncommenting the block in `src/test_score_growth.py` and install `openpyxl`.

## Customization knobs

Open `src/test_score_growth.py` and adjust the constants near the top:

- `SELECTED_SCHOOLS` – limit the analysis to specific school names (leave empty for all schools).
- `SUBGROUP_VALUES_FOR_FILTER` – control which student groups appear in `filtered_data.csv`.

## Data cleaning notes

- Column aliases cover the shifting headers shown in recent public files (`LEA Name` ↔ `lea_name`, `Student Group Value` ↔ `Subgroup Value`, `Enrolled Grade or Course`, etc.).
- Subgroup labels are standardized (`White/Caucasian` → `White`, `Hispanic/Latino of any race` → `Hispanic/Latino`).
- Suppressed metrics (`DS`, `<5%`, `<=10%`, `N<10`) are stored as missing values so they do not distort growth calculations.
- If multiple files exist for the same year and grain, values are averaged.

## Dash app (optional)

Install Dash/Plotly and run the simple explorer:

```bash
pip install dash plotly
python app/app.py
```

Add `input_data/school_locations.csv` (columns: `School Name`, `Latitude`, `Longitude`) to unlock the map view.
