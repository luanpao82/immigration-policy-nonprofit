# Policy Signals: Immigration Policy & Nonprofit Stakeholders

Companion site and replication materials for:

> **Policy Signals: How Local Governments' Immigration Policies Are Perceived by Nonprofit Stakeholders**

The project examines how local immigration policies (carrot and stick) shape donor and stakeholder support for immigrant-serving nonprofits, using OLS with cluster-robust standard errors and two-part hurdle models on a sample of 1,287 nonprofits across 199 U.S. counties.

## Live site

**[https://luanpao82.github.io/immigration-policy-nonprofit](https://luanpao82.github.io/immigration-policy-nonprofit)** — interactive project page with the conceptual model, hypotheses, sample-construction pipeline, descriptive statistics, regression results (Tables 2–4), and downloadable replication materials.

## Repository contents

| Path | Description |
|---|---|
| `index.html` | Project site (deployed via GitHub Pages) |
| `map_county.html` | Plotly choropleth of the 224 ICMA-matched counties |
| `county_npo_counts.csv` | County-level NPO counts and population (data backing the map) |
| `replication/analytic_sample.csv` | Final analytic sample (1,287 NPOs × 34 columns) |
| `replication/replication.py` | Self-contained Python script reproducing Tables 2–4 |
| `replication/codebook.md` | Variable-by-variable codebook for the analytic sample |
| `replication/replication_output.csv` | Output of `replication.py` in long format |

## Reproducing Tables 2–4

```bash
cd replication
pip install pandas numpy statsmodels
python replication.py
```

Expected runtime: < 10 seconds. The script prints all coefficients and SEs to stdout and saves `replication_output.csv` for downstream table construction. See `replication/codebook.md` for variable definitions and `replication.py` for the model specifications.

## Data sources & attribution

- **IRS Form 990 e-filers (2019)** — outcomes and organizational controls. Public domain.
- **ICMA Local Government and Immigrant Communities Survey (2018)** — policy variables and the moderator (county-level derived measures only). Underlying respondent-level survey data is governed by the [ICMA Data Licensing Agreement](https://icma.org/); researchers seeking access to the raw survey must obtain it through ICMA.
- **American Community Survey 5-year estimates (2018)** — county demographic controls. Public domain.
- **2016 county-level presidential returns** — Democratic vote share. Public domain.

## Citation

If you use these materials, please cite the manuscript and acknowledge the data sources above.
