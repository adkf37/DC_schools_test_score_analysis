# Data Sources

## Primary Data: OSSE School-Level Assessment Results

All files are published annually by the DC Office of the State Superintendent of Education (OSSE). They are **not** tracked in this repository (see `.gitignore`) and must be downloaded manually.

| File | School Year | Format | Download URL | Status |
|------|------------|--------|-------------|--------|
| `2021-22 School Level PARCC and MSAA Data.xlsx` | 2021–22 | Excel (.xlsx) | [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data) | ✅ Available (download manually) |
| `2022-23 School Level PARCC and MSAA Data_9_5.xlsx` | 2022–23 | Excel (.xlsx) | [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data) | ✅ Available (download manually) |
| `DC Cape Scores 2023-2024.xlsx` | 2023–24 | Excel (.xlsx) | [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data) | ✅ Available (download manually) |
| `2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx` | 2024–25 | Excel (.xlsx) | [OSSE Assessment Data](https://osse.dc.gov/page/assessment-data) | ✅ Available (download manually) |

Place downloaded files under `input_data/` (nested folders are accepted).

---

## Reference / Validation Data

| File | Purpose | Format | Location | Status |
|------|---------|--------|----------|--------|
| `StuartHobson_Manual_Growth_example.xlsx` | Manual cohort growth benchmark (4 transitions) | Excel (.xlsx) | Repo root | ✅ Present in repo |
| `filtered_data_w_SH_BASIS_LAT_pivot.xlsx` | Pre-computed pivot with Stuart-Hobson, BASIS, and Latin School data | Excel (.xlsx) | Repo root | ✅ Present in repo |
| `Field Differences 21-22 to 24-25.xlsx` | Column-name mapping across fiscal years | Excel (.xlsx) | Repo root | ✅ Present in repo |

---

## Optional Supplementary Data

| File | Purpose | Format | Location | Status |
|------|---------|--------|----------|--------|
| `input_data/school_locations.csv` | School geocoordinates for map view in Dash app | CSV | `input_data/` | ⚠️ Not present — must be created or sourced |

**`school_locations.csv` schema** (required columns):

| Column | Description |
|--------|-------------|
| `School Name` | Must match names in the OSSE files |
| `Latitude` | Decimal degrees |
| `Longitude` | Decimal degrees |

Possible sources for school coordinates:
- [DC Public Schools school list](https://dcps.dc.gov/page/dcps-school-profiles)
- [DC Public Charter School Board](https://www.dcpcsb.org/schools)
- Google Maps Geocoding API (for batch geocoding from school names/addresses)

---

## Data Licensing

OSSE assessment data is published as open government data. No API key is required. Files are subject to OSSE's standard data-use policies; suppressed values (cells marked `DS`, `N<10`, `<5%`, etc.) must not be used to re-identify individual students.
