"""
Equity Progress (Gap Closure) Analysis — DC Schools Test Score Analysis.

This script answers the policy question: "Are DC's achievement gaps between
student demographic groups getting smaller or larger over time?"

For every pair of student subgroups (reference vs. comparison), subject, and
year, it computes the average proficiency gap across schools that have valid
data for both subgroups in that year.  Comparing the gap in the earliest
available year to the gap in the most recent year yields a "gap change"
metric:

    gap_first_pp    — average proficiency gap in the earliest year with
                      valid data for both subgroups (across schools)
    gap_last_pp     — average proficiency gap in the most recent year with
                      valid data for both subgroups (across schools)
    gap_change_pp   — gap_last_pp − gap_first_pp
                      negative → gap narrowed (equity improved)
                      positive → gap widened (equity worsened)
    gap_pct_change  — 100 × gap_change_pp / |gap_first_pp|
                      (percentage change in the gap size)

Subgroup pairs analysed (reference subgroup listed first):
    • White vs. Black or African American
    • White vs. Hispanic/Latino of any race
    • White vs. Econ Dis
    • All Students vs. Econ Dis
    • All Students vs. EL Active
    • All Students vs. Students with Disabilities

Outputs:
    equity_progress_citywide.csv  — gap per subgroup pair × subject × year
                                    (avg gap across schools in that year,
                                     n_schools with valid data for both)
    equity_progress_summary.csv   — per subgroup pair × subject aggregate:
                                    first_year, last_year, gap_first_pp,
                                    gap_last_pp, gap_change_pp, gap_pct_change,
                                    n_schools_first, n_schools_last

Inputs:
    output_data/combined_all_years.csv   — produced by load_wide_format_data.py

Usage:
    python src/equity_progress_analysis.py

Dependencies:
    Run after the full pipeline (at least after load_wide_format_data.py).
"""
import os
import sys
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

COMBINED_FILE = os.path.join(OUTPUT_PATH, "combined_all_years.csv")
OUT_CITYWIDE = os.path.join(OUTPUT_PATH, "equity_progress_citywide.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "equity_progress_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
# Subgroup pairs: (reference_subgroup, comparison_subgroup, pair_label)
# Gap = proficiency(reference) − proficiency(comparison)
SUBGROUP_PAIRS = [
    ("White", "Black or African American", "White − Black"),
    ("White", "Hispanic/Latino of any race", "White − Hispanic"),
    ("White", "Econ Dis", "White − Econ Dis"),
    ("All Students", "Econ Dis", "All − Econ Dis"),
    ("All Students", "EL Active", "All − EL Active"),
    ("All Students", "Students with Disabilities", "All − SWD"),
]

# Minimum schools with valid data for both subgroups in a year
MIN_SCHOOLS = 5


# ── Helper ────────────────────────────────────────────────────────────────────

def _parse_percent(series: pd.Series) -> pd.Series:
    """Convert percent strings to float; return NaN for suppressed values."""
    suppress = {"DS", "N<10", "<5%", "<=10%", "N/A", "NA", ""}

    def _parse(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in suppress:
            return np.nan
        if any(s.startswith(m) for m in ("<", "<=", ">", ">=")):
            return np.nan
        try:
            return float(s.replace("%", "").strip())
        except ValueError:
            return np.nan

    return series.apply(_parse)


# ═════════════════════════════════════════════════════════════════════════════
# Core computation
# ═════════════════════════════════════════════════════════════════════════════

def load_and_prepare() -> pd.DataFrame:
    """Load combined data and return one row per school × subject × subgroup × year."""
    if not os.path.isfile(COMBINED_FILE):
        print(f"ERROR: {COMBINED_FILE} not found.")
        print("Run python src/load_wide_format_data.py first.")
        sys.exit(1)

    df = pd.read_csv(COMBINED_FILE, dtype=str)
    print(f"Loaded combined data: {len(df):,} rows")

    # School-level only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Parse numeric columns
    df["proficiency_pct"] = _parse_percent(df["Percent"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Standardise subgroup label
    df["subgroup"] = df["Student Group Value"].str.strip()

    # Collect all subgroups referenced in pairs
    needed_subgroups = set()
    for ref, comp, _ in SUBGROUP_PAIRS:
        needed_subgroups.add(ref)
        needed_subgroups.add(comp)

    df = df[df["subgroup"].isin(needed_subgroups)]
    df = df.dropna(subset=["School Name", "Subject", "subgroup", "year", "proficiency_pct"])

    # Use "All Grades" / "All" rows where available, else average across grades
    all_mask = df["Tested Grade/Subject"].str.upper().isin({"ALL", "ALL GRADES"})
    df_all = df[all_mask].copy()
    df_other = df[~all_mask].copy()

    all_keys = set(
        zip(df_all["School Name"], df_all["Subject"], df_all["subgroup"], df_all["year"])
    )

    other_not_covered = df_other[
        ~df_other.apply(
            lambda r: (r["School Name"], r["Subject"], r["subgroup"], r["year"])
            in all_keys,
            axis=1,
        )
    ]

    if not other_not_covered.empty:
        other_agg = (
            other_not_covered
            .groupby(["School Name", "Subject", "subgroup", "year"], as_index=False)
            .agg(proficiency_pct=("proficiency_pct", "mean"))
        )
        df_combined = pd.concat([df_all, other_agg], ignore_index=True)
    else:
        df_combined = df_all.copy()

    # Dedup: one row per school × subject × subgroup × year
    df_combined = (
        df_combined
        .groupby(["School Name", "Subject", "subgroup", "year"], as_index=False)
        .agg(proficiency_pct=("proficiency_pct", "mean"))
    )

    print(
        f"Prepared {len(df_combined):,} school × subject × subgroup × year rows"
        f" ({df_combined['subgroup'].nunique()} subgroups, "
        f"{df_combined['year'].nunique()} years)"
    )
    return df_combined


def compute_citywide_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the average gap per subgroup pair × subject × year.

    For each year, a school is included only if it has valid proficiency for
    both the reference and comparison subgroup in that year.
    """
    print("\n" + "=" * 70)
    print("COMPUTING CITYWIDE GAP SERIES")
    print("=" * 70)

    records = []
    subjects = sorted(df["Subject"].unique())

    for subject in subjects:
        subj_df = df[df["Subject"] == subject]

        for ref_sg, comp_sg, pair_label in SUBGROUP_PAIRS:
            ref_data = (
                subj_df[subj_df["subgroup"] == ref_sg]
                .set_index(["School Name", "year"])["proficiency_pct"]
                .rename("ref_pct")
            )
            comp_data = (
                subj_df[subj_df["subgroup"] == comp_sg]
                .set_index(["School Name", "year"])["proficiency_pct"]
                .rename("comp_pct")
            )

            if ref_data.empty or comp_data.empty:
                continue

            merged = pd.concat([ref_data, comp_data], axis=1).dropna()

            if merged.empty:
                continue

            merged = merged.reset_index()
            merged["gap_pp"] = merged["ref_pct"] - merged["comp_pct"]

            year_agg = (
                merged.groupby("year")
                .agg(
                    avg_gap_pp=("gap_pp", "mean"),
                    n_schools=("School Name", "nunique"),
                )
                .reset_index()
            )
            year_agg = year_agg[year_agg["n_schools"] >= MIN_SCHOOLS]
            year_agg["Subject"] = subject
            year_agg["pair_label"] = pair_label
            year_agg["reference_subgroup"] = ref_sg
            year_agg["comparison_subgroup"] = comp_sg
            year_agg["avg_gap_pp"] = year_agg["avg_gap_pp"].round(2)

            records.append(year_agg)

    if not records:
        print("WARNING: No valid gap data found.")
        return pd.DataFrame()

    citywide = pd.concat(records, ignore_index=True)
    citywide = citywide.sort_values(["Subject", "pair_label", "year"])

    print(f"Citywide gap series: {len(citywide):,} rows")
    return citywide.reset_index(drop=True)


def compute_progress_summary(citywide: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise gap change from first to last available year for each
    subgroup pair × subject.
    """
    print("\n" + "=" * 70)
    print("COMPUTING GAP PROGRESS SUMMARY")
    print("=" * 70)

    records = []

    for (pair_label, subject), grp in citywide.groupby(["pair_label", "Subject"]):
        grp_sorted = grp.sort_values("year")

        if len(grp_sorted) < 2:
            continue

        first_row = grp_sorted.iloc[0]
        last_row = grp_sorted.iloc[-1]

        gap_first = first_row["avg_gap_pp"]
        gap_last = last_row["avg_gap_pp"]
        gap_change = round(gap_last - gap_first, 2)

        if abs(gap_first) >= 0.1:
            gap_pct_change = round(100 * gap_change / abs(gap_first), 1)
        else:
            gap_pct_change = np.nan

        # Reference and comparison subgroups
        ref_sg = first_row["reference_subgroup"]
        comp_sg = first_row["comparison_subgroup"]

        # Progress direction
        if gap_change < -0.5:
            direction = "Narrowing"
        elif gap_change > 0.5:
            direction = "Widening"
        else:
            direction = "Stable"

        records.append({
            "pair_label": pair_label,
            "reference_subgroup": ref_sg,
            "comparison_subgroup": comp_sg,
            "Subject": subject,
            "first_year": int(first_row["year"]),
            "last_year": int(last_row["year"]),
            "gap_first_pp": round(gap_first, 2),
            "gap_last_pp": round(gap_last, 2),
            "gap_change_pp": gap_change,
            "gap_pct_change": gap_pct_change,
            "direction": direction,
            "n_schools_first": int(first_row["n_schools"]),
            "n_schools_last": int(last_row["n_schools"]),
        })

    summary = pd.DataFrame(records)
    summary = summary.sort_values(["Subject", "pair_label"]).reset_index(drop=True)
    print(f"Progress summary: {len(summary):,} rows")
    return summary


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 70)
    print("Equity Progress (Gap Closure) Analysis")
    print("=" * 70)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    df = load_and_prepare()
    citywide = compute_citywide_gaps(df)
    summary = compute_progress_summary(citywide)

    citywide.to_csv(OUT_CITYWIDE, index=False)
    print(f"\n✓ {OUT_CITYWIDE}  ({len(citywide):,} rows)")

    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"✓ {OUT_SUMMARY}  ({len(summary):,} rows)")

    # ── Key findings ──────────────────────────────────────────────────────
    print("\n── Key findings ──────────────────────────────────────────────────")
    for subject in ["ELA", "Math"]:
        sub = summary[summary["Subject"] == subject]
        if sub.empty:
            continue
        print(f"\n{subject}:")
        for _, row in sub.sort_values("gap_change_pp").iterrows():
            dir_symbol = "▼" if row["direction"] == "Narrowing" else ("▲" if row["direction"] == "Widening" else "→")
            print(
                f"  {dir_symbol} {row['pair_label']:28s}  "
                f"gap: {row['gap_first_pp']:+.1f} pp ({row['first_year']}) → "
                f"{row['gap_last_pp']:+.1f} pp ({row['last_year']})  "
                f"change: {row['gap_change_pp']:+.2f} pp  [{row['direction']}]"
            )

    print("\n" + "=" * 70)
    print("COMPLETE — equity_progress_analysis.py done")
    print("=" * 70)


if __name__ == "__main__":
    main()
