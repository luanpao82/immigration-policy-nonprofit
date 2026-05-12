"""
Replication script for:
    "Policy Signals: How Local Governments' Immigration Policies Are Perceived
     by Nonprofit Stakeholders"

Reproduces Tables 2 (Donations), 3 (Government Grants), and 4 (Program Service
Revenue) of the manuscript, including:
    - Model 1 Baseline (OLS-CR)
    - Model 2 Moderation (OLS-CR with policy x npoprovider interactions)
    - Model 3a Hurdle Part 1 (logistic, extensive margin)
    - Model 3b Hurdle Part 2 (OLS-CR on recipients, intensive margin)

Input:  analytic_sample.csv  (1,287 NPOs across 199 counties; the cleaned sample
        produced by the data-preparation pipeline described on the project site)
Output: prints coefficients to stdout; saves a CSV summary.

Requirements
------------
    Python >=3.10
    pandas >=2.0
    numpy
    statsmodels >=0.14

Run
---
    python replication.py
"""
from __future__ import annotations
import os, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "analytic_sample.csv")
OUT_CSV   = os.path.join(HERE, "replication_output.csv")

# ----------------------------------------------------------------------------
# Model specification (identical RHS across all three DVs and all four columns)
# ----------------------------------------------------------------------------
BASE_RHS = (
    "imgrnt_support + econ_support + enforce_binary + npoprovider_c + "
    "ln_employee + ln_assets + C(region) + "
    "ln_pop_z + pct_foreign_born_z + ses_index + dem_share_z"
)
MOD_RHS = (
    "imgrnt_support * npoprovider_c + econ_support * npoprovider_c + "
    "enforce_binary * npoprovider_c + "
    "ln_employee + ln_assets + C(region) + "
    "ln_pop_z + pct_foreign_born_z + ses_index + dem_share_z"
)

DVS = [
    ("Donations",   "ln_donations",  "DONATIONS",       True),   # no Hurdle (1.4% zeros)
    ("Gov Grants",  "ln_govgrants",  "GOVGRANTS",       False),
    ("Prog Rev",    "ln_progrev",    "PROGRAMREVENUE",  False),
]

POLICY_VARS = ["imgrnt_support", "econ_support", "enforce_binary", "npoprovider_c"]
INTERACTION_VARS = [
    "imgrnt_support:npoprovider_c",
    "econ_support:npoprovider_c",
    "enforce_binary:npoprovider_c",
]
CONTROL_VARS = [
    "ln_employee", "ln_assets",
    "ln_pop_z", "pct_foreign_born_z", "ses_index", "dem_share_z",
]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def sig_star(p: float) -> str:
    if pd.isna(p): return ""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.1 else ""


def print_table(model, label: str, vars_to_show: list[str]) -> None:
    print(f"\n  {label}  (N={int(model.nobs)}, "
          f"R²={getattr(model, 'rsquared', getattr(model, 'prsquared', float('nan'))):.4f}, "
          f"Clusters={model.cov_kwds.get('groups').nunique() if model.cov_kwds else 'n/a'})")
    print(f"  {'Variable':35s}  {'B':>9s}  {'SE':>8s}  {'p':>8s}  sig")
    print("  " + "-" * 70)
    for v in vars_to_show:
        if v not in model.params.index:
            continue
        b, se, p = model.params[v], model.bse[v], model.pvalues[v]
        print(f"  {v:35s}  {b:>9.4f}  {se:>8.4f}  {p:>8.4f}  {sig_star(p)}")


def fit_ols_cr(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["fips"]}
    )


def fit_logit_cr(formula: str, data: pd.DataFrame):
    return smf.logit(formula, data=data).fit(
        disp=0, maxiter=100,
        cov_type="cluster", cov_kwds={"groups": data["fips"]},
    )


# ----------------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)
# Region must be a string for C() to treat it as categorical (Northeast=1 is reference)
df["region"] = df["region"].astype(str)
n_clust = df["fips"].nunique()
print("=" * 72)
print(f"ANALYTIC SAMPLE: {len(df):,} nonprofits  |  {n_clust} county clusters")
print("=" * 72)


# ----------------------------------------------------------------------------
# Estimate
# ----------------------------------------------------------------------------
results = {}
for label, ln_dv, raw_dv, skip_hurdle in DVS:
    print("\n" + "═" * 72)
    print(f"TABLE: {label}  (DV: {ln_dv})")
    print("═" * 72)

    # ---- M1: Baseline OLS-CR ----
    m1 = fit_ols_cr(f"{ln_dv} ~ {BASE_RHS}", df)
    print_table(m1, "M1 Baseline (OLS-CR)", POLICY_VARS + CONTROL_VARS)

    # ---- M2: Moderation OLS-CR ----
    m2 = fit_ols_cr(f"{ln_dv} ~ {MOD_RHS}", df)
    print_table(m2, "M2 Moderation (OLS-CR)", POLICY_VARS + INTERACTION_VARS + CONTROL_VARS)

    # ---- M3a: Hurdle Part 1 (logit) ----
    # ---- M3b: Hurdle Part 2 (OLS-CR on recipients) ----
    m3a, m3b = None, None
    if not skip_hurdle:
        has = f"has_{raw_dv.lower()}"
        df[has] = (df[raw_dv] > 0).astype(int)
        try:
            m3a = fit_logit_cr(f"{has} ~ {MOD_RHS}", df)
            print_table(m3a, "M3a Hurdle Part 1 (logit-CR, extensive margin)",
                        POLICY_VARS + INTERACTION_VARS)
        except Exception as e:
            print(f"\n  M3a failed: {e}")
        recip = df[df[raw_dv] > 0].copy()
        try:
            m3b = fit_ols_cr(f"{ln_dv} ~ {MOD_RHS}", recip)
            print_table(m3b, f"M3b Hurdle Part 2 (OLS-CR on recipients, N={len(recip)})",
                        POLICY_VARS + INTERACTION_VARS)
        except Exception as e:
            print(f"\n  M3b failed: {e}")
    else:
        print("\n  [Hurdle skipped for Donations — 1.4% zeros; OLS-CR baseline is primary spec]")

    results[label] = {"m1": m1, "m2": m2, "m3a": m3a, "m3b": m3b}


# ----------------------------------------------------------------------------
# Tidy CSV output (long format)
# ----------------------------------------------------------------------------
rows = []
spec_names = [("m1","M1 Baseline"), ("m2","M2 Moderation"),
              ("m3a","M3a Hurdle P1"), ("m3b","M3b Hurdle P2")]
for dv_label, models in results.items():
    for key, spec_label in spec_names:
        mdl = models.get(key)
        if mdl is None: continue
        for var in POLICY_VARS + INTERACTION_VARS + CONTROL_VARS:
            if var in mdl.params.index:
                rows.append({
                    "DV":           dv_label,
                    "Model":        spec_label,
                    "Variable":     var,
                    "Coefficient":  mdl.params[var],
                    "SE":           mdl.bse[var],
                    "p_value":      mdl.pvalues[var],
                    "N":            int(mdl.nobs),
                })
out = pd.DataFrame(rows)
out.to_csv(OUT_CSV, index=False)
print("\n" + "=" * 72)
print(f"Saved {len(out)} rows to {OUT_CSV}")
print("=" * 72)
