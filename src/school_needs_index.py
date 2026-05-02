"""
School Needs Index — DC Schools Test Score Analysis.

This script is the policy-targeted complement to `school_performance_index.py`.
While the Performance Index identifies top performers, the Needs Index surfaces
which schools most require intervention support by inverting the same analytical
dimensions:

    1. Proficiency Need Score   — 100 − percentile_rank(avg_proficiency_pct)
                                  (source: school_consistency.csv)
    2. Growth Need Score        — 100 − percentile_rank(avg_pp_growth)
                                  (source: school_rankings.csv)
    3. Recovery Need Score      — 100 − percentile_rank(net_vs_precovid_pp)
                                  (source: covid_recovery_summary.csv)
    4. Equity Need Score        — percentile_rank(mean absolute gap across
                                  disadvantaged groups)
                                  (source: equity_gap_summary.csv)

Each component is percentile-ranked within its subject so scores are always
0–100 regardless of scale.  The composite is the simple mean of available
component scores.  Schools with fewer than 2 valid components receive a tier
of "Insufficient Data".

Tier labels (based on the composite needs score distribution):
    Critical          ≥ 75th percentile of composite across schools
    High              50th – 75th percentile
    Moderate          25th – 50th percentile
    Low               < 25th percentile
    Insufficient Data fewer than 2 valid component scores

Note: "DC Public Schools" (citywide aggregate row) is excluded because it
has no physical school to target for intervention.

Key outputs:
    school_needs_index.csv   — one row per school × subject; includes all
                               component scores, composite score, tier, and
                               source metrics
    needs_tier_summary.csv   — per tier × subject: n_schools, mean composite,
                               mean proficiency, mean cohort growth

Inputs (all optional — missing components are silently omitted):
    output_data/school_consistency.csv
    output_data/school_rankings.csv
    output_data/covid_recovery_summary.csv
    output_data/equity_gap_summary.csv

Usage:
    python src/school_needs_index.py

Dependencies:
    Run after the full pipeline (ideally after charter_dcps_analysis.py).
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

CONSISTENCY_FILE = os.path.join(OUTPUT_PATH, "school_consistency.csv")
RANKINGS_FILE = os.path.join(OUTPUT_PATH, "school_rankings.csv")
COVID_RECOVERY_FILE = os.path.join(OUTPUT_PATH, "covid_recovery_summary.csv")
EQUITY_GAP_FILE = os.path.join(OUTPUT_PATH, "equity_gap_summary.csv")

OUT_INDEX = os.path.join(OUTPUT_PATH, "school_needs_index.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "needs_tier_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_COMPONENTS = 2  # minimum valid component scores for a composite rating

# Citywide aggregate — not a physical school; excluded from needs ranking
AGGREGATE_NAMES = {"DC Public Schools"}

TIER_LABELS = ["Critical", "High", "Moderate", "Low"]

TIER_COLORS = {
    "Critical": "#d32f2f",
    "High": "#f57c00",
    "Moderate": "#fbc02d",
    "Low": "#388e3c",
    "Insufficient Data": "#9e9e9e",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pctile_rank(series: pd.Series, score) -> float:
    """Return the percentile rank (0–100) of *score* in *series* (ignoring NaN)."""
    valid = series.dropna().values
    if len(valid) == 0 or np.isnan(score):
        return np.nan
    return percentileofscore(valid, score, kind="mean")


def _add_percentile_component(
    df: pd.DataFrame,
    src_col: str,
    out_col: str,
    invert: bool,
) -> pd.DataFrame:
    """
    For each Subject group, compute a percentile-rank component score (0–100)
    from *src_col* and write it to *out_col*.

    If *invert* is True the score is (100 − pctile) so that lower values of
    *src_col* produce higher need scores.
    """
    results = []
    for subj, grp in df.groupby("Subject"):
        scores = grp[src_col].dropna()
        pctiles = grp[src_col].apply(
            lambda v: _pctile_rank(scores, v) if not pd.isna(v) else np.nan
        )
        if invert:
            pctiles = 100.0 - pctiles
        results.append(pctiles)
    df[out_col] = pd.concat(results).reindex(df.index)
    return df


def _assign_tier(composite: float, thresholds: dict) -> str:
    """Assign a tier label given pre-computed percentile thresholds."""
    if np.isnan(composite):
        return "Insufficient Data"
    if composite >= thresholds[75]:
        return "Critical"
    if composite >= thresholds[50]:
        return "High"
    if composite >= thresholds[25]:
        return "Moderate"
    return "Low"


def _load(path: str, label: str) -> pd.DataFrame:
    if os.path.isfile(path):
        df = pd.read_csv(path)
        print(f"  Loaded {label}: {len(df):,} rows")
        return df
    print(f"  Skipping {label} (file not found — component will be omitted)")
    return pd.DataFrame()


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SCHOOL NEEDS INDEX")
    print("=" * 70)

    # ── Load component source files ────────────────────────────────────────
    print("\nLoading source files …")
    consistency = _load(CONSISTENCY_FILE, "school_consistency.csv")
    rankings = _load(RANKINGS_FILE, "school_rankings.csv")
    covid = _load(COVID_RECOVERY_FILE, "covid_recovery_summary.csv")
    equity = _load(EQUITY_GAP_FILE, "equity_gap_summary.csv")

    # ── Build the base table: one row per school × subject ────────────────
    # Start from consistency (broadest school coverage); fall back to rankings
    if not consistency.empty:
        base = consistency[["School Name", "Subject", "avg_proficiency_pct"]].copy()
    elif not rankings.empty:
        base = rankings[["School Name", "Subject"]].copy()
        base["avg_proficiency_pct"] = np.nan
    else:
        print("\nERROR: Neither school_consistency.csv nor school_rankings.csv is present.")
        print("       Run the full pipeline first.")
        sys.exit(1)

    # Exclude citywide aggregate row
    base = base[~base["School Name"].isin(AGGREGATE_NAMES)].copy()
    base = base.reset_index(drop=True)

    # ── Component 1: Proficiency Need ──────────────────────────────────────
    # Low proficiency → high need (inverted percentile)
    if "avg_proficiency_pct" in base.columns and base["avg_proficiency_pct"].notna().any():
        base = _add_percentile_component(
            base, "avg_proficiency_pct", "proficiency_need_score", invert=True
        )
    else:
        base["proficiency_need_score"] = np.nan

    # ── Component 2: Growth Need ───────────────────────────────────────────
    # Low cohort growth → high need (inverted percentile)
    if not rankings.empty:
        rk = rankings[["School Name", "Subject", "avg_pp_growth"]].copy()
        rk = rk[~rk["School Name"].isin(AGGREGATE_NAMES)]
        base = base.merge(rk, on=["School Name", "Subject"], how="left")
        base = _add_percentile_component(
            base, "avg_pp_growth", "growth_need_score", invert=True
        )
    else:
        base["avg_pp_growth"] = np.nan
        base["growth_need_score"] = np.nan

    # ── Component 3: COVID Recovery Need ──────────────────────────────────
    # More negative net_vs_precovid_pp → high need (inverted percentile)
    if not covid.empty:
        cv = covid[["School Name", "Subject", "net_vs_precovid_pp", "recovery_status"]].copy()
        cv = cv[~cv["School Name"].isin(AGGREGATE_NAMES)]
        base = base.merge(cv, on=["School Name", "Subject"], how="left")
        base = _add_percentile_component(
            base, "net_vs_precovid_pp", "recovery_need_score", invert=True
        )
    else:
        base["net_vs_precovid_pp"] = np.nan
        base["recovery_status"] = np.nan
        base["recovery_need_score"] = np.nan

    # ── Component 4: Equity Gap Need ──────────────────────────────────────
    # Larger mean absolute gap across disadvantaged groups → high need
    equity_need = pd.DataFrame()
    if not equity.empty and "is_disadvantaged" in equity.columns:
        # Use disadvantaged groups only; take mean of |avg_proficiency_gap|
        eq_dis = equity[equity["is_disadvantaged"]].copy()
        eq_dis["abs_gap"] = eq_dis["avg_proficiency_gap"].abs()
        equity_school = (
            eq_dis.groupby(["School Name", "Subject"], as_index=False)
            .agg(mean_abs_equity_gap=("abs_gap", "mean"))
        )
        equity_school = equity_school[~equity_school["School Name"].isin(AGGREGATE_NAMES)]
        equity_need = equity_school
        base = base.merge(equity_school, on=["School Name", "Subject"], how="left")
        base = _add_percentile_component(
            base, "mean_abs_equity_gap", "equity_need_score", invert=False
        )
    else:
        base["mean_abs_equity_gap"] = np.nan
        base["equity_need_score"] = np.nan

    # ── Composite needs score ──────────────────────────────────────────────
    component_cols = [
        "proficiency_need_score",
        "growth_need_score",
        "recovery_need_score",
        "equity_need_score",
    ]

    base["n_components"] = base[component_cols].notna().sum(axis=1)
    base["composite_needs_score"] = base.apply(
        lambda row: (
            row[component_cols].dropna().mean()
            if row["n_components"] >= MIN_COMPONENTS
            else np.nan
        ),
        axis=1,
    )

    # Round component and composite columns
    for col in component_cols + ["composite_needs_score"]:
        if col in base.columns:
            base[col] = base[col].round(1)

    # ── Assign tier labels ─────────────────────────────────────────────────
    def _compute_thresholds(subj_df: pd.DataFrame) -> dict:
        valid = subj_df["composite_needs_score"].dropna()
        if valid.empty:
            return {25: np.nan, 50: np.nan, 75: np.nan}
        return {p: float(np.percentile(valid, p)) for p in [25, 50, 75]}

    tier_col = []
    for subj, grp in base.groupby("Subject"):
        thresholds = _compute_thresholds(grp)
        tiers = grp["composite_needs_score"].apply(
            lambda v: _assign_tier(v, thresholds)
        )
        tier_col.append(tiers)

    base["needs_tier"] = pd.concat(tier_col).reindex(base.index)

    # ── Build tier summary ─────────────────────────────────────────────────
    summary_rows = []
    tier_order = TIER_LABELS + ["Insufficient Data"]
    tier_rank = {t: i for i, t in enumerate(tier_order)}

    for subj, grp in base.groupby("Subject"):
        for tier in tier_order:
            tdf = grp[grp["needs_tier"] == tier]
            n = len(tdf)
            if n == 0:
                continue
            summary_rows.append(
                dict(
                    Subject=subj,
                    needs_tier=tier,
                    n_schools=n,
                    mean_composite=round(tdf["composite_needs_score"].mean(), 1)
                    if tdf["composite_needs_score"].notna().any() else np.nan,
                    mean_proficiency_pct=round(tdf["avg_proficiency_pct"].mean(), 1)
                    if tdf["avg_proficiency_pct"].notna().any() else np.nan,
                    mean_cohort_growth_pp=round(tdf["avg_pp_growth"].mean(), 2)
                    if tdf["avg_pp_growth"].notna().any() else np.nan,
                    mean_abs_equity_gap=round(tdf["mean_abs_equity_gap"].mean(), 1)
                    if tdf["mean_abs_equity_gap"].notna().any() else np.nan,
                )
            )

    summary = pd.DataFrame(summary_rows)
    summary["_tier_rank"] = summary["needs_tier"].map(tier_rank).fillna(99)
    summary = summary.sort_values(["Subject", "_tier_rank"]).drop(
        columns=["_tier_rank"]
    ).reset_index(drop=True)

    # ── Final column ordering ──────────────────────────────────────────────
    col_order = [
        "School Name", "Subject",
        "composite_needs_score", "needs_tier", "n_components",
        "proficiency_need_score", "growth_need_score",
        "recovery_need_score", "equity_need_score",
        "avg_proficiency_pct", "avg_pp_growth",
        "net_vs_precovid_pp", "recovery_status",
        "mean_abs_equity_gap",
    ]
    col_order = [c for c in col_order if c in base.columns]
    base = base[col_order].sort_values(["Subject", "composite_needs_score"],
                                        ascending=[True, False]).reset_index(drop=True)

    # ── Save outputs ───────────────────────────────────────────────────────
    base.to_csv(OUT_INDEX, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(base)} rows → {OUT_INDEX}")
    print(f"✓ Saved {len(summary)} rows → {OUT_SUMMARY}")

    # ── Print key findings ─────────────────────────────────────────────────
    print("\n── Key Findings ──")
    for subj in sorted(base["Subject"].unique()):
        sub = base[base["Subject"] == subj]
        print(f"\n  {subj} — needs tier breakdown:")
        for tier in TIER_LABELS + ["Insufficient Data"]:
            tdf = sub[sub["needs_tier"] == tier]
            if tdf.empty:
                continue
            avg_p = tdf["avg_proficiency_pct"].mean()
            avg_g = tdf["avg_pp_growth"].mean()
            p_str = f"avg proficiency {avg_p:.1f}%" if not np.isnan(avg_p) else ""
            g_str = f"avg cohort growth {avg_g:+.1f} pp" if not np.isnan(avg_g) else ""
            extras = ", ".join(x for x in [p_str, g_str] if x)
            print(f"    {tier}: {len(tdf)} schools" + (f" — {extras}" if extras else ""))

        critical = sub[sub["needs_tier"] == "Critical"].nlargest(5, "composite_needs_score")
        if not critical.empty:
            print(f"  Top Critical-need {subj} schools (by composite):")
            for _, row in critical.iterrows():
                p = row.get("avg_proficiency_pct", np.nan)
                cs = row.get("composite_needs_score", np.nan)
                p_str = f"{p:.1f}%" if not np.isnan(p) else "N/A"
                cs_str = f"{cs:.1f}" if not np.isnan(cs) else "N/A"
                print(f"    {row['School Name']}: composite {cs_str}, proficiency {p_str}")

    print()
    print("=" * 70)
    print("SCHOOL NEEDS INDEX COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run()
