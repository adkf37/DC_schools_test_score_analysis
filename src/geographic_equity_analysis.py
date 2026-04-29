"""
Geographic equity analysis for DC schools.

Joins school location data (Neighborhood, Quadrant) with cohort growth and
proficiency trend outputs to surface geographic disparities across DC's four
quadrants (NE / NW / SE / SW).

Inputs:
  input_data/school_locations.csv       – school coordinates + Neighborhood + Quadrant
  output_data/cohort_growth_summary.csv – per-school average cohort growth
  output_data/proficiency_trends.csv    – per-school × year × subject proficiency

Outputs:
  output_data/geographic_equity_by_school.csv  – school-level data with quadrant tag
  output_data/geographic_equity_by_quadrant.csv – quadrant-level aggregated stats

Usage:
    python src/geographic_equity_analysis.py
"""
import os
import re
import sys
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
INPUT_PATH = os.path.join(REPO_ROOT, "input_data")
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

LOCATIONS_FILE = os.path.join(INPUT_PATH, "school_locations.csv")
GROWTH_SUMMARY_FILE = os.path.join(OUTPUT_PATH, "cohort_growth_summary.csv")
PROFICIENCY_TRENDS_FILE = os.path.join(OUTPUT_PATH, "proficiency_trends.csv")
OUT_SCHOOL_FILE = os.path.join(OUTPUT_PATH, "geographic_equity_by_school.csv")
OUT_QUADRANT_FILE = os.path.join(OUTPUT_PATH, "geographic_equity_by_quadrant.csv")


# ── Name normalization helpers ─────────────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """
    Return a simplified key for fuzzy school-name matching.

    Removes common suffixes (ES, MS, HS, EC, etc.), punctuation, and
    extra whitespace, then lowercases.  This lets names like
    "Anacostia HS" and "Anacostia High School" map to the same key.
    """
    if not isinstance(name, str):
        return ""
    s = name.lower()
    # Expand common abbreviations before stripping
    abbrev = {
        r"\bes\b": "elementary school",
        r"\bms\b": "middle school",
        r"\bhs\b": "high school",
        r"\bec\b": "education campus",
        r"\bpcs\b": "",
    }
    for pat, repl in abbrev.items():
        s = re.sub(pat, repl, s)
    # Remove possessives and extra punctuation
    s = re.sub(r"['\-–@]", " ", s)
    # Strip parenthesised suffixes like "(Capitol Hill Cluster)"
    s = re.sub(r"\(.*?\)", "", s)
    # Remove common filler words
    for word in [
        "elementary school", "middle school", "high school",
        "education campus", "school", "academy",
    ]:
        s = s.replace(word, " ")
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_name_map(
    source_names: pd.Series, target_names: pd.Series
) -> dict:
    """
    Build {source_name → target_name} using exact match then normalized-key match.

    Exact matches (case-insensitive) are preferred; normalized-key matches are
    used as fallback.  If a source name matches multiple targets, the first
    (alphabetically sorted) match is used.
    """
    target_norm = {_normalize_name(n): n for n in sorted(target_names.unique())}
    mapping: dict = {}
    for src in source_names.unique():
        # 1. exact match (case-insensitive)
        for tgt in target_names.unique():
            if src.lower() == tgt.lower():
                mapping[src] = tgt
                break
        if src in mapping:
            continue
        # 2. normalized-key match
        key = _normalize_name(src)
        if key and key in target_norm:
            mapping[src] = target_norm[key]
    return mapping


# ── Main ───────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("GEOGRAPHIC EQUITY ANALYSIS")
    print("=" * 70)

    # ── Load inputs ───────────────────────────────────────────────────────────
    for fpath, label in [
        (LOCATIONS_FILE, "school_locations.csv"),
        (GROWTH_SUMMARY_FILE, "cohort_growth_summary.csv"),
        (PROFICIENCY_TRENDS_FILE, "proficiency_trends.csv"),
    ]:
        if not os.path.isfile(fpath):
            print(f"ERROR: Required file not found: {fpath}")
            print(f"       Run the upstream pipeline scripts first.")
            sys.exit(1)

    locs = pd.read_csv(LOCATIONS_FILE)
    growth = pd.read_csv(GROWTH_SUMMARY_FILE)
    trends = pd.read_csv(PROFICIENCY_TRENDS_FILE)

    print(f"  Locations loaded  : {len(locs):,} schools")
    print(f"  Growth summary    : {len(growth):,} rows, {growth['School Name'].nunique()} schools")
    print(f"  Proficiency trends: {len(trends):,} rows, {trends['School Name'].nunique()} schools")

    # ── Map location names → growth / trends names ────────────────────────────
    loc_to_growth = build_name_map(locs["School Name"], growth["School Name"])
    loc_to_trends = build_name_map(locs["School Name"], trends["School Name"])

    # Apply mapping: add a canonical "growth_school_name" column to locs
    locs["growth_key"] = locs["School Name"].map(loc_to_growth)
    locs["trends_key"] = locs["School Name"].map(loc_to_trends)

    matched_growth = locs["growth_key"].notna().sum()
    matched_trends = locs["trends_key"].notna().sum()
    print(f"\n  Name mapping: {matched_growth}/{len(locs)} locations matched to growth data")
    print(f"  Name mapping: {matched_trends}/{len(locs)} locations matched to trends data")

    # ── Build school-level table ───────────────────────────────────────────────
    # Pivot: one row per school × subject, using All Students subgroup
    growth_all = (
        growth[growth["Student Group Value"] == "All Students"]
        .groupby(["School Name", "Subject"], as_index=False)
        .agg(
            avg_pp_growth=("avg_pp_growth", "mean"),
            avg_baseline_pct=("avg_baseline_pct", "mean"),
            n_transitions=("n_transitions", "sum"),
        )
    )

    # Latest year proficiency from trends (All Students, all grades)
    # Step 1: identify the max year per school × subject group
    trends_all_students = trends[trends["Student Group Value"] == "All Students"].copy()
    max_year_per_group = (
        trends_all_students.groupby(["School Name", "Subject"])["year"]
        .max()
        .reset_index()
        .rename(columns={"year": "max_year"})
    )
    trends_latest = trends_all_students.merge(max_year_per_group, on=["School Name", "Subject"])
    trends_latest = trends_latest[trends_latest["year"] == trends_latest["max_year"]]

    # Step 2: aggregate over all grades in the latest year and over all years
    trends_all = (
        trends_all_students.groupby(["School Name", "Subject"], as_index=False)
        .agg(mean_proficiency_pct=("proficiency_pct", "mean"))
    )
    latest_pct = (
        trends_latest.groupby(["School Name", "Subject"], as_index=False)
        .agg(latest_proficiency_pct=("proficiency_pct", "mean"))
    )
    trends_all = trends_all.merge(latest_pct, on=["School Name", "Subject"], how="left")

    # Build a base locations table with both mapping keys
    locs_base = locs[
        ["School Name", "Latitude", "Longitude", "Neighborhood", "Quadrant",
         "growth_key", "trends_key"]
    ].copy()

    # Merge locations → growth (one row per location × subject after merge)
    # Keep trends_key by not renaming until needed
    school_growth = locs_base.merge(
        growth_all.rename(columns={"School Name": "growth_key"}),
        on="growth_key",
        how="left",
    )

    # Merge in proficiency trend data via trends_key + Subject
    school_growth = school_growth.merge(
        trends_all.rename(columns={"School Name": "trends_key"}),
        on=["trends_key", "Subject"],
        how="left",
    )

    # Keep only rows that have a Quadrant assignment
    school_geo = school_growth.dropna(subset=["Quadrant"]).copy()
    school_geo = school_geo.drop(columns=["growth_key", "trends_key"], errors="ignore")

    print(f"\n  School-level table: {len(school_geo):,} rows ({school_geo['School Name'].nunique()} unique schools)")

    # ── Quadrant-level aggregation ─────────────────────────────────────────────
    quad_agg = (
        school_geo.groupby(["Quadrant", "Subject"], as_index=False)
        .agg(
            n_schools=("School Name", "nunique"),
            avg_pp_growth=("avg_pp_growth", "mean"),
            median_pp_growth=("avg_pp_growth", "median"),
            avg_baseline_proficiency=("avg_baseline_pct", "mean"),
            avg_mean_proficiency=("mean_proficiency_pct", "mean"),
        )
        .round(2)
    )
    quad_agg = quad_agg.sort_values(["Subject", "Quadrant"]).reset_index(drop=True)

    # ── Equity gap: NW vs. other quadrants (all-years mean proficiency) ────────
    # NW schools historically have highest proficiency in DC; compare others.
    for subj in quad_agg["Subject"].unique():
        subj_df = quad_agg[quad_agg["Subject"] == subj]
        nw_row = subj_df[subj_df["Quadrant"] == "NW"]
        if nw_row.empty:
            continue
        nw_prof = nw_row["avg_mean_proficiency"].values[0]
        mask = (quad_agg["Subject"] == subj)
        quad_agg.loc[mask, "gap_vs_nw_pp"] = (
            quad_agg.loc[mask, "avg_mean_proficiency"] - nw_prof
        ).round(2)

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("QUADRANT SUMMARY")
    print("─" * 70)
    for subj in sorted(quad_agg["Subject"].unique()):
        print(f"\n  {subj}")
        subj_rows = quad_agg[quad_agg["Subject"] == subj]
        for _, row in subj_rows.iterrows():
            gap_str = (
                f"  (gap vs NW: {row['gap_vs_nw_pp']:+.1f} pp)"
                if pd.notna(row.get("gap_vs_nw_pp"))
                else ""
            )
            print(
                f"    {row['Quadrant']:3s}  "
                f"{row['n_schools']:3.0f} schools  "
                f"avg prof: {row['avg_mean_proficiency']:5.1f}%  "
                f"avg growth: {row['avg_pp_growth']:+.2f} pp"
                f"{gap_str}"
            )

    # ── Save outputs ──────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    school_geo.to_csv(OUT_SCHOOL_FILE, index=False)
    quad_agg.to_csv(OUT_QUADRANT_FILE, index=False)

    print(f"\n✓ Saved {len(school_geo):,} rows → {OUT_SCHOOL_FILE}")
    print(f"✓ Saved {len(quad_agg):,} rows → {OUT_QUADRANT_FILE}")
    print()
    print("=" * 70)
    print("GEOGRAPHIC EQUITY ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
