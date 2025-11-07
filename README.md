# DC Schools Test Score Analysis

Analyze and compare DC school test performance across years and student groups, with a focus on school-to-school comparisons and year-over-year growth.

## What this does
- Auto-ingests all files in `input_data/` (CSV, XLSX/XLS)
- Parses the school year from each filename (e.g., `2015-16` -> 2016, `2023-2024` -> 2024, `2024-25` -> 2025)
- Normalizes schema differences between files/years
- Filters to the “Meeting or Exceeding Expectations” metric where available
- Handles suppressed values (e.g., DS, n<10, <5%) as missing
- Computes multi-year growth (first-to-last and last-vs-prev) per school/subject/subgroup/content grain
- Produces comparison summaries by school and subject
- Exports CSVs and an optional Excel workbook in `output_data/`

## Outputs
- `output_data/filtered_data.csv` — rows for the configured subgroup(s) across all years (default White)
- `output_data/school_growth_full.csv` — detailed grain with percent/count columns for all years plus growth
- `output_data/school_growth_by_school_subject.csv` — summary by School x Subject x Subgroup with growth
- `output_data/school_growth_pivot.xlsx` — Excel with both views (requires `openpyxl`)

## Requirements
- Python 3.9+
- pandas
- openpyxl (only if you want the Excel export)

Install:
```bash
pip install pandas openpyxl
```

## Run
From the project root:
```bash
python src/test_score_growth.py
```

### Launch the Dash app
Install extras and run:
```bash
pip install dash plotly
python app/app.py
```

Optional mapping: add `input_data/school_locations.csv` with columns:
- School Name
- Latitude
- Longitude

## Customize
Open `src/test_score_growth.py` and modify these at the top:
- `SELECTED_SCHOOLS` — list of school names to limit analysis (leave empty for all)
- `SUBGROUP_VALUES_FOR_FILTER` — which subgroup(s) to export to `filtered_data.csv`

## Notes on data handling
- The script standardizes subgroup labels (e.g., `White/Caucasian` -> `White`).
- Values like `DS`, `n<10`, `<5%`, `<=10%` are treated as missing for growth calculations.
- Growth defaults to “last available year minus first available year” and “last minus previous year”.
- If multiple files exist for the same year, values are averaged within identical grains (School/Subject/Subgroup/etc.).
