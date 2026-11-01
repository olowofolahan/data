# Lassa fever spatial regression — Nigeria (2020–2026)

Exploratory **cross-sectional spatial regression** of Lassa fever burden across
Nigeria's 37 first-level units (36 states + FCT), using NCDC weekly
surveillance as the outcome and state-level socio-ecological covariates as
predictors.

## Status (phase 1 complete)

| Step | Script | Output | Result |
|------|--------|--------|--------|
| Outcome table | `src/build_outcome.py` | `data/processed/outcome_state.csv` | 37 states, cumulative + per-year cases |
| Boundaries + weights | `src/build_boundaries.py` | `data/processed/states.geojson`, `queen_weights.gal` | 37 polygons, queen contiguity (4.7 nbrs avg, 0 islands) |
| Spatial autocorrelation | `src/spatial_eda.py` | `outputs/spatial_eda_maps.png`, `lisa_results.csv` | **Moran's I = 0.25, p = 0.007** |

**Headline so far:** confirmed cases are significantly spatially clustered
(not random), with a High–High hotspot belt (Edo, Taraba, Benue, Plateau,
Nasarawa, Delta). This justifies a spatial model over OLS. Five states
(Ondo, Edo, Bauchi, Taraba, Ebonyi) hold 86% of all confirmed cases.

## Outcome definition

Primary response: **cumulative confirmed cases 2020–2026** per state (and
`conf_mean_annual_2021_2025` for complete seasons). The count is
**zero-inflated and overdispersed** → model with negative binomial / an
incidence rate (population offset), not Gaussian OLS.

⚠️ **Detection confound:** "cases" are *detected* cases. Edo (Irrua/ISTH) and
Ondo (FMC Owo) host the national treatment + diagnostic centres, so proximity
to a lab inflates counts. A surveillance-intensity proxy (lab access, tests
performed, `pct_confirmed_of_suspected`) must be a covariate.

## Candidate predictors & data sources

See [`VARIABLES.md`](VARIABLES.md) for the full mechanism-based catalogue and
the data-source / acquisition status for each.

## Network constraint (action needed)

This cloud session's egress policy currently reaches only GitHub and Natural
Earth. The covariate hosts (WorldPop, CHIRPS/WorldClim, NBS, DHS, HDX, GBIF,
Wikipedia) are blocked, so automated covariate collection is paused. To
continue, add these under **Allowed domains** in the environment's Network
settings (keep "Allow package managers" ticked):
`data.humdata.org`, `api.gbif.org`, `en.wikipedia.org`, `data.worldpop.org`,
`dhsprogram.com`. Steps: https://code.claude.com/docs/en/cloud-environments#network-access

## Reproduce

```bash
pip install -r requirements.txt
# one-time: fetch Natural Earth admin-1 into data/external/ (see VARIABLES.md)
cd src
python build_outcome.py
python build_boundaries.py
python spatial_eda.py
```

## Data provenance

- **Outcome:** NCDC weekly Lassa situation reports, compiled by
  [BioDivHealth/LF_Nigeria_Reports](https://github.com/BioDivHealth/LF_Nigeria_Reports)
  (CC0; AI-extracted from NCDC PDFs — values should be spot-checked).
- **Boundaries:** Natural Earth 10m Admin-1 (public domain).
