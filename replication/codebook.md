# Codebook — `analytic_sample.csv`

**Project.** *Policy Signals: How Local Governments' Immigration Policies Are Perceived by Nonprofit Stakeholders*

**Unit of observation.** One row per immigrant-serving nonprofit organization (NPO).

**Sample.** N = 1,287 NPOs nested within 199 U.S. county-level jurisdictions, after applying:
1. Two-stage manual review of 5,250 keyword-search candidates (Form 990 e-filers, 2019) → 2,365 reviewed
2. FIPS validation → 2,348
3. Inner join with ICMA Local Government and Immigrant Communities Survey (2018) → 1,542 NPOs · 224 counties
4. Listwise deletion on all analysis variables → 1,506
5. Cook's distance influence trimming (union across 3 OLS baseline models, 4/n threshold) → 1,287

See the project site (§4 Data Collection & Sample Construction) for the full pipeline diagram.

---

## Variable index

### Identifiers and geography

| Variable | Type | Description |
|---|---|---|
| `EIN` | int | IRS Employer Identification Number (public; from Form 990) |
| `fips` | string (5-digit) | County FIPS code (state + county). Used as cluster ID for cluster-robust SEs |
| `CENSUS_STATE_NAME` | string | State name |
| `CENSUS_COUNTY_NAME` | string | County name |
| `icma_picked_level` | string | Which ICMA respondent level was used for this county's policy profile (`County` if a county-government response exists; otherwise the largest jurisdiction within the county by underage-18 population) |
| `icma_picked_local_gov` | string | Name of the picked local-government respondent |
| `UREGN` | int (1–4) | U.S. Census region code: 1 = Northeast, 2 = Midwest, 3 = South, 4 = West |
| `region` | string (1–4) | Same as UREGN, stored as string for categorical use in formulas |

### Dependent variables (Form 990, 2019)

| Variable | Type | Description |
|---|---|---|
| `DONATIONS` | float ($) | Private donations. Computed as `TOTALCONTRIBUTION − GOVGRANTS`, clipped at 0. Captures community/donor support |
| `GOVGRANTS` | float ($) | Government grant revenue (Form 990 GOVGRANTS field, Line 1e). Captures public-sector partnership |
| `PROGRAMREVENUE` | float ($) | Program service revenue (Line 2g). Fees, service contracts, and earned income from mission-related activities |
| `ln_donations` | float | `ln(DONATIONS + 1)` |
| `ln_govgrants` | float | `ln(GOVGRANTS + 1)` |
| `ln_progrev` | float | `ln(PROGRAMREVENUE + 1)` |

### Policy variables (ICMA, 2018)

| Variable | Type | Description |
|---|---|---|
| `imgrnt_support` | int (0–8) | **Carrot.** Additive index of 8 binary items (Q5a–Q5h) covering immigrant-supporting services (multilingual access, immigrant affairs commission, ID cards, cultural-competency training, etc.). Items binarized: 1 = Yes, 0 = No or Don't Know, NaN = missing. Computed only when ≥ 4 of 8 items are non-missing |
| `econ_support` | int (0–4) | **Carrot.** Additive index of 4 binary items (Q10a–Q10d) on immigrant-targeted economic programs (entrepreneurship, micro-financing, etc.). Computed only when ≥ 2 of 4 items are non-missing |
| `enforce` | int (0–5) | **Stick.** Count of enforcement items (Q14a–Q14e_enct): hiring restrictions, federal collaboration, service restrictions, status verification, landlord penalties |
| `enforce_binary` | int (0/1) | **Stick (used in models).** `1` if `enforce > 0`, else `0`. Recoded from the count because of near-zero variance in the original distribution |

### Moderator (ICMA, 2018)

| Variable | Type | Description |
|---|---|---|
| `npoprovider` | int (0–5) | **Perceived NPO's role.** Additive index of 5 ICMA items (Q6a3–Q6e3) coded 1 if nonprofits are reported as the primary provider in each of five service categories (language assistance, legal counseling, health/social services, education/workforce, housing). Used as both direct predictor (H3) and moderator (H4) |
| `npoprovider_c` | float | `npoprovider` mean-centered on the analytic sample. Used for the interaction terms in moderation models |

### Organization-level controls (Form 990)

| Variable | Type | Description |
|---|---|---|
| `EMPLOYEE` | int | Total employees (raw) |
| `TOTALASSETS` | float ($) | Total assets (raw); a small number of negative values |
| `ln_employee` | float | `ln(EMPLOYEE + 1)` |
| `ln_assets` | float | `ln(max(TOTALASSETS, 1))` (bottom-coded at 1 to handle non-positive values) |

### County-level controls (ACS 2018; 2016 election)

#### Raw (untransformed)

| Variable | Type | Description |
|---|---|---|
| `total_pop` | int | Total population (ACS) |
| `pct_foreign_born` | float (0–100) | Percent foreign-born |
| `median_income` | float ($) | Median household income |
| `pct_college` | float (0–100) | Percent of adults with a bachelor's degree or higher |
| `pct_poverty` | float (0–100) | Percent of population in poverty |
| `dem_vote_share` | float (0–100) | Democratic share of the two-party vote, 2016 presidential election |

#### Transformed (entered in regression models)

| Variable | Type | Description |
|---|---|---|
| `ln_pop_z` | float | `ln(total_pop + 1)`, then *z*-score standardized on the analytic sample |
| `pct_foreign_born_z` | float | `pct_foreign_born` *z*-score standardized on the analytic sample |
| `ses_index` | float | Composite: mean of three *z*-scores — standardized median income + standardized pct_college − standardized pct_poverty, divided by 3. Captures county SES; reverse-coding poverty makes higher values indicate higher SES |
| `dem_share_z` | float | `dem_vote_share` *z*-score standardized on the analytic sample |

> **Coefficient interpretation.** Because the four county-level controls enter the regression as *z*-scores, their coefficients reflect the change in the (logged) outcome per **one-standard-deviation** increase in the predictor — not per one percentage point.

---

## Data sources and licensing

| Source | Year | Variables | License |
|---|---|---|---|
| **IRS Form 990 e-filers** | 2019 | All DVs, `EMPLOYEE`, `TOTALASSETS`, `EIN`, `CENSUS_*`, NTEE | Public domain |
| **ICMA Local Government and Immigrant Communities Survey** | 2018 | All policy variables, moderator, region (`UREGN`) | ICMA Data Licensing Agreement — derived county-level measures are reproduced here for replication purposes. Researchers seeking the underlying respondent-level survey data must obtain access through ICMA |
| **American Community Survey (ACS) 5-year estimates** | 2018 | Raw county controls (`total_pop`, `pct_foreign_born`, `median_income`, `pct_college`, `pct_poverty`) | Public domain |
| **Federal Election Commission (via county-level 2016 returns)** | 2016 | `dem_vote_share` | Public domain |

---

## Notes

- Models use **OLS with cluster-robust (CR1) standard errors** clustered on `fips`. See `replication.py`.
- Hurdle Part 1 (extensive margin) and Hurdle Part 2 (intensive margin) are estimated only for `Gov Grants` and `Prog Rev`. For `Donations`, the post-trim zero rate is 1.4%, which leaves the Part 1 logistic under-identified; OLS-CR baseline serves as the primary specification.
- Cook's distance trimming was applied **before** standardization (z-scores and `ses_index`) so the *z*-scores reported here are computed on the analytic sample (N = 1,287), not the larger pre-trim sample.
- Region fixed effects are included in all models via `C(region)`, with Northeast (`region == "1"`) as the reference category.

## Citation

If you use these materials, please cite the manuscript and acknowledge the data sources above.
