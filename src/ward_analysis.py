"""
Ward-Level Performance Analysis — DC Schools Test Score Analysis.

Maps every school to one of DC's eight political wards using the
neighbourhood metadata in ``input_data/school_locations.csv``, then
aggregates proficiency, cohort growth, and COVID-recovery metrics by
ward × subject to surface intra-city geographic disparities at the
ward level.

DC wards (1-8) are the primary political/administrative units used by
the DC Council and by DCPS planning.  Ward-level analysis is finer-
grained than the four-quadrant analysis already in
``geographic_equity_analysis.py`` and is more actionable for policy
stakeholders.

Inputs:
    input_data/school_locations.csv           — school coordinates +
                                                Neighborhood + Quadrant
    output_data/proficiency_trends.csv        — school × year × subject
                                                × grade × subgroup
    output_data/cohort_growth_summary.csv     — per-school avg cohort
                                                growth (All Students)
    output_data/covid_recovery_summary.csv    — pre-COVID baseline and
                                                recovery metrics (optional)

Outputs:
    output_data/ward_proficiency.csv   — ward × subject × year averages
                                         (avg proficiency, n_schools)
    output_data/ward_summary.csv       — ward × subject aggregate stats
                                         (avg proficiency, growth,
                                          COVID impact/recovery, n_schools,
                                          gap vs. Ward 3)

Usage:
    python src/ward_analysis.py

Dependencies:
    Run after the full pipeline (at least through
    proficiency_trend_analysis.py and geographic_equity_analysis.py).
"""
import os
import re
import sys
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
INPUT_PATH = os.path.join(REPO_ROOT, "input_data")
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

LOCATIONS_FILE = os.path.join(INPUT_PATH, "school_locations.csv")
TRENDS_FILE = os.path.join(OUTPUT_PATH, "proficiency_trends.csv")
GROWTH_SUMMARY_FILE = os.path.join(OUTPUT_PATH, "cohort_growth_summary.csv")
COVID_RECOVERY_FILE = os.path.join(OUTPUT_PATH, "covid_recovery_summary.csv")

OUT_WARD_PROFICIENCY = os.path.join(OUTPUT_PATH, "ward_proficiency.csv")
OUT_WARD_SUMMARY = os.path.join(OUTPUT_PATH, "ward_summary.csv")

# ── Neighbourhood → Ward mapping ──────────────────────────────────────────────
#
# Each DC neighbourhood is assigned to the ward whose council
# representative covers that neighbourhood.  Assignments follow the
# official DC Ward boundaries set in the 2022 redistricting.
#
# Source reference: DC Office of Planning ward boundary maps.
# Approximate assignments are used for neighbourhoods that sit on ward
# boundaries; the label reflects the majority-area ward.

NEIGHBORHOOD_WARD: dict[str, int] = {
    "Adams Morgan": 1,
    "Anacostia": 8,
    "Barry Farm": 8,
    "Brightwood": 4,
    "Brookland": 5,
    "Burrville": 5,
    "Capitol Hill": 6,
    "Chevy Chase DC": 3,
    "Cleveland Park": 3,
    "Columbia Heights": 1,
    "Congress Heights": 8,
    "Deanwood": 7,
    "Dupont Circle": 2,
    "Foggy Bottom": 2,
    "Fort Lincoln": 5,
    "Friendship Heights": 3,
    "Garfield Heights": 8,
    "Georgetown": 2,
    "H Street NE": 6,
    "Langdon": 5,
    "LeDroit Park": 5,
    "Logan Circle": 2,
    "Manor Park": 4,
    "Marshall Heights": 7,
    "McLean Gardens": 3,
    "Mount Pleasant": 1,
    "NoMa": 6,
    "Palisades": 3,
    "Park View": 1,
    "Petworth": 4,
    "Randle Highlands": 7,
    "Shaw": 2,
    "Southwest Waterfront": 6,
    "Takoma": 4,
    "Tenleytown": 3,
    "Trinidad": 5,
    "U Street Corridor": 1,
    "Woodridge": 5,
}

# Ward display labels used in charts
WARD_LABELS: dict[int, str] = {i: f"Ward {i}" for i in range(1, 9)}

# Ward 3 (Tenleytown / Cleveland Park / Chevy Chase / Palisades) is used as the
# reference benchmark for gap calculations because it consistently has the highest
# proficiency in both ELA and Math across all years in the dataset.
REFERENCE_WARD: int = 3


# ── Name-normalisation helpers (reused from geographic_equity_analysis.py) ────

def _normalize_name(name: str) -> str:
    """Return a simplified key for fuzzy school-name matching."""
    if not isinstance(name, str):
        return ""
    s = name.lower()
    abbrev = {
        r"\bes\b": "elementary school",
        r"\bms\b": "middle school",
        r"\bhs\b": "high school",
        r"\bec\b": "education campus",
        r"\bpcs\b": "",
    }
    for pat, repl in abbrev.items():
        s = re.sub(pat, repl, s)
    s = re.sub(r"['\-–@]", " ", s)
    s = re.sub(r"\(.*?\)", "", s)
    for word in [
        "elementary school", "middle school", "high school",
        "education campus", "school", "academy",
    ]:
        s = s.replace(word, " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _build_name_map(source_names: pd.Series, target_names: pd.Series) -> dict:
    """Build {source → target} using exact then normalised-key match."""
    target_norm = {_normalize_name(n): n for n in sorted(target_names.unique())}
    mapping: dict = {}
    for src in source_names.unique():
        for tgt in target_names.unique():
            if src.lower() == tgt.lower():
                mapping[src] = tgt
                break
        if src in mapping:
            continue
        key = _normalize_name(src)
        if key and key in target_norm:
            mapping[src] = target_norm[key]
    return mapping


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("WARD-LEVEL PERFORMANCE ANALYSIS")
    print("=" * 70)

    # ── Validate required inputs ───────────────────────────────────────────
    for fpath, label in [
        (LOCATIONS_FILE, "school_locations.csv"),
        (TRENDS_FILE, "proficiency_trends.csv"),
        (GROWTH_SUMMARY_FILE, "cohort_growth_summary.csv"),
    ]:
        if not os.path.isfile(fpath):
            print(f"ERROR: Required file not found: {fpath}")
            print("       Run the upstream pipeline scripts first.")
            sys.exit(1)

    # ── Load inputs ───────────────────────────────────────────────────────
    locs = pd.read_csv(LOCATIONS_FILE)
    trends = pd.read_csv(TRENDS_FILE)
    growth = pd.read_csv(GROWTH_SUMMARY_FILE)

    print(f"\n  Locations      : {len(locs):,} schools")
    print(f"  Proficiency    : {len(trends):,} rows, {trends['School Name'].nunique()} schools")
    print(f"  Cohort growth  : {len(growth):,} rows, {growth['School Name'].nunique()} schools")

    # COVID recovery is optional
    covid = pd.DataFrame()
    if os.path.isfile(COVID_RECOVERY_FILE):
        covid = pd.read_csv(COVID_RECOVERY_FILE)
        print(f"  COVID recovery : {len(covid):,} rows")
    else:
        print("  NOTE: covid_recovery_summary.csv not found — COVID columns omitted.")

    # ── Assign wards ──────────────────────────────────────────────────────
    locs["Ward"] = locs["Neighborhood"].map(NEIGHBORHOOD_WARD)
    n_assigned = locs["Ward"].notna().sum()
    n_total = len(locs)
    print(f"\n  Ward assignments: {n_assigned}/{n_total} schools assigned "
          f"({n_total - n_assigned} unmapped neighbourhoods skipped)")

    if n_assigned == 0:
        print("ERROR: No schools could be assigned to a ward.")
        sys.exit(1)

    locs_with_ward = locs.dropna(subset=["Ward"]).copy()
    locs_with_ward["Ward"] = locs_with_ward["Ward"].astype(int)

    # ── Map location names → trend / growth names ─────────────────────────
    loc_to_trends = _build_name_map(locs_with_ward["School Name"], trends["School Name"])
    loc_to_growth = _build_name_map(locs_with_ward["School Name"], growth["School Name"])

    locs_with_ward["trends_key"] = locs_with_ward["School Name"].map(loc_to_trends)
    locs_with_ward["growth_key"] = locs_with_ward["School Name"].map(loc_to_growth)

    print(f"  Name mapping: {locs_with_ward['trends_key'].notna().sum()}/{n_assigned} "
          f"mapped to proficiency trends")
    print(f"  Name mapping: {locs_with_ward['growth_key'].notna().sum()}/{n_assigned} "
          f"mapped to growth data")

    # ── Build all-years mean proficiency per school (All Students) ────────
    trends_all = (
        trends[trends["Student Group Value"].isin({"All Students", "All", "Total"})]
        .groupby(["School Name", "Subject"], as_index=False)
        .agg(mean_proficiency_pct=("proficiency_pct", "mean"))
    )

    # ── Build ward × subject × year proficiency (citywide trend) ─────────
    # Join locs → trends via trends_key
    ward_school = locs_with_ward[["School Name", "Ward", "trends_key"]].copy()
    ward_school = ward_school.dropna(subset=["trends_key"])

    trends_filt = trends[
        trends["Student Group Value"].isin({"All Students", "All", "Total"})
    ].copy()

    trends_merged = ward_school.merge(
        trends_filt.rename(columns={"School Name": "trends_key"}),
        on="trends_key",
        how="inner",
    )

    ward_by_year = (
        trends_merged.groupby(["Ward", "Subject", "year"], as_index=False)
        .agg(
            avg_proficiency_pct=("proficiency_pct", "mean"),
            median_proficiency_pct=("proficiency_pct", "median"),
            n_schools=("trends_key", "nunique"),
        )
        .round(2)
    )
    ward_by_year = ward_by_year.sort_values(
        ["Subject", "Ward", "year"]
    ).reset_index(drop=True)

    # ── Build ward × subject summary (all-years averages) ─────────────────
    # All-years mean proficiency per school, then aggregate by ward
    school_mean_prof = (
        trends_filt.groupby(["School Name", "Subject"], as_index=False)
        .agg(mean_proficiency_pct=("proficiency_pct", "mean"))
    )

    # Map school → ward via trends_key
    key_to_ward = locs_with_ward.set_index("trends_key")["Ward"].to_dict()
    school_mean_prof["Ward"] = school_mean_prof["School Name"].map(key_to_ward)
    school_mean_prof = school_mean_prof.dropna(subset=["Ward"])
    school_mean_prof["Ward"] = school_mean_prof["Ward"].astype(int)

    ward_prof_agg = (
        school_mean_prof.groupby(["Ward", "Subject"], as_index=False)
        .agg(
            n_schools_proficiency=("School Name", "nunique"),
            avg_proficiency_pct=("mean_proficiency_pct", "mean"),
            median_proficiency_pct=("mean_proficiency_pct", "median"),
        )
        .round(2)
    )

    # Merge cohort growth (All Students)
    growth_all = growth[
        growth["Student Group Value"].isin({"All Students", "All", "Total"})
    ].copy()

    growth_school_agg = (
        growth_all.groupby(["School Name", "Subject"], as_index=False)
        .agg(avg_pp_growth=("avg_pp_growth", "mean"))
    )

    key_to_ward_growth = locs_with_ward.set_index("growth_key")["Ward"].to_dict()
    growth_school_agg["Ward"] = growth_school_agg["School Name"].map(key_to_ward_growth)
    growth_school_agg = growth_school_agg.dropna(subset=["Ward"])
    growth_school_agg["Ward"] = growth_school_agg["Ward"].astype(int)

    growth_ward_agg = (
        growth_school_agg.groupby(["Ward", "Subject"], as_index=False)
        .agg(
            n_schools_growth=("School Name", "nunique"),
            avg_pp_growth=("avg_pp_growth", "mean"),
        )
        .round(2)
    )

    ward_summary = ward_prof_agg.merge(
        growth_ward_agg, on=["Ward", "Subject"], how="outer"
    )

    # Merge COVID recovery (optional, All Students only)
    if not covid.empty:
        # covid_recovery_summary.csv is already All Students only
        covid_school = (
            covid.groupby(["School Name", "Subject"], as_index=False)
            .agg(
                covid_impact_pp=("covid_impact_pp", "mean"),
                recovery_pp=("recovery_pp", "mean"),
                net_vs_precovid_pp=("net_vs_precovid_pp", "mean"),
            )
        )
        covid_school["Ward"] = covid_school["School Name"].map(key_to_ward)
        covid_school = covid_school.dropna(subset=["Ward"])
        covid_school["Ward"] = covid_school["Ward"].astype(int)

        covid_ward = (
            covid_school.groupby(["Ward", "Subject"], as_index=False)
            .agg(
                covid_impact_pp=("covid_impact_pp", "mean"),
                recovery_pp=("recovery_pp", "mean"),
                net_vs_precovid_pp=("net_vs_precovid_pp", "mean"),
            )
            .round(2)
        )
        ward_summary = ward_summary.merge(
            covid_ward, on=["Ward", "Subject"], how="left"
        )

    # Gap vs. reference ward (historically highest-proficiency ward in DC)
    for subj in ward_summary["Subject"].unique():
        mask = ward_summary["Subject"] == subj
        ref_row = ward_summary[(ward_summary["Subject"] == subj) &
                               (ward_summary["Ward"] == REFERENCE_WARD)]
        if ref_row.empty:
            continue
        ref_prof = ref_row["avg_proficiency_pct"].values[0]
        ward_summary.loc[mask, f"gap_vs_ward{REFERENCE_WARD}_pp"] = (
            ward_summary.loc[mask, "avg_proficiency_pct"] - ref_prof
        ).round(2)

    # Add Ward label column for readability
    ward_summary["Ward Label"] = ward_summary["Ward"].map(WARD_LABELS)

    # Determine n_schools as max of proficiency / growth coverage
    ward_summary["n_schools"] = (
        ward_summary[["n_schools_proficiency", "n_schools_growth"]]
        .max(axis=1)
        .fillna(0)
        .astype(int)
    )

    col_order = [
        "Ward", "Ward Label", "Subject", "n_schools",
        "avg_proficiency_pct", "median_proficiency_pct",
        "avg_pp_growth",
    ]
    if "covid_impact_pp" in ward_summary.columns:
        col_order += ["covid_impact_pp", "recovery_pp", "net_vs_precovid_pp"]
    col_order.append(f"gap_vs_ward{REFERENCE_WARD}_pp")
    col_order = [c for c in col_order if c in ward_summary.columns]

    ward_summary = (
        ward_summary[col_order]
        .sort_values(["Subject", "Ward"])
        .reset_index(drop=True)
    )

    # ── Print key findings ─────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("WARD SUMMARY")
    print("─" * 70)

    gap_col = f"gap_vs_ward{REFERENCE_WARD}_pp"
    for subj in sorted(ward_summary["Subject"].unique()):
        print(f"\n  {subj}")
        sub = ward_summary[ward_summary["Subject"] == subj]
        for _, row in sub.iterrows():
            gap_str = ""
            if gap_col in row and pd.notna(row[gap_col]):
                gap_str = f"  (gap vs Ward {REFERENCE_WARD}: {row[gap_col]:+.1f} pp)"
            g_str = ""
            if "avg_pp_growth" in row and pd.notna(row["avg_pp_growth"]):
                g_str = f"  avg growth: {row['avg_pp_growth']:+.2f} pp"
            print(
                f"    Ward {int(row['Ward']):d}  "
                f"{int(row.get('n_schools', 0)):3d} schools  "
                f"avg prof: {row['avg_proficiency_pct']:5.1f}%"
                f"{g_str}{gap_str}"
            )

    # ── Save outputs ──────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    ward_by_year.to_csv(OUT_WARD_PROFICIENCY, index=False)
    ward_summary.to_csv(OUT_WARD_SUMMARY, index=False)

    print(f"\n✓ Saved {len(ward_by_year):,} rows → {OUT_WARD_PROFICIENCY}")
    print(f"✓ Saved {len(ward_summary):,} rows → {OUT_WARD_SUMMARY}")
    print()
    print("=" * 70)
    print("WARD-LEVEL PERFORMANCE ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
