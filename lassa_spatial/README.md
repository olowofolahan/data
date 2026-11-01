# Lassa fever spatial regression — Nigeria (2020–2026)

Exploratory **cross-sectional spatial regression** of Lassa fever burden across
Nigeria's 37 first-level units (36 states + FCT), using NCDC weekly
surveillance as the outcome and state-level socio-ecological covariates as
predictors.

## Status

| Phase | Scripts | Result |
|------|--------|--------|
| 1 — outcome + spatial structure | `build_outcome`, `build_boundaries`, `spatial_eda` | 37-state outcome; **Moran's I = 0.25, p = 0.007** (clustered) |
| 2 — detection baseline | `build_covariates_available`, `fit_models` | confirmed ∝ suspected (R²=0.94); clustering is largely a detection signal |
| 3 — full covariate models | `fetch_gbif_rodents`, `build_population`, `build_socioeconomic`, `assemble_master`, `fit_models_full` | incidence driven by **latitude ↓, density ↓, poverty ↑**; see `FINDINGS.md` |

**Headline:** confirmed cases cluster in a southern/central belt (Edo, Ondo,
Bauchi, Taraba, Ebonyi = 86% of cases). On incidence, the ecological model
shows strong **north–south and urban–rural gradients** plus a **positive
poverty effect** once geography is controlled — but detection geography and
true risk are entangled at state scale. Full detail and caveats in
[`FINDINGS.md`](FINDINGS.md).

Collected covariates: WorldPop population/density, OPHI subnational MPI
(poverty), HDX health-facility density, GBIF reservoir occurrences, geography,
surveillance proxies. **Pending:** climate (WorldClim/CHIRPS hosts still
blocked) and a proper *Mastomys* suitability surface.

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

## Reproduce

```bash
pip install -r requirements.txt
bash src/download_external.sh   # Natural Earth, WorldPop, HDX MPI + health
cd src
python build_outcome.py
python build_boundaries.py
python spatial_eda.py
python build_covariates_available.py
python fetch_gbif_rodents.py          # pulls GBIF directly
python build_population.py
python build_socioeconomic.py
python assemble_master.py
python fit_models.py
python fit_models_full.py
```

To add the pending climate covariates, allowlist `geodata.ucdavis.edu`
(WorldClim) and `data.chc.ucsb.edu` (CHIRPS) under **Allowed domains** in the
environment's Network settings:
https://code.claude.com/docs/en/cloud-environments#network-access

## Data provenance

- **Outcome:** NCDC weekly Lassa situation reports, compiled by
  [BioDivHealth/LF_Nigeria_Reports](https://github.com/BioDivHealth/LF_Nigeria_Reports)
  (CC0; AI-extracted from NCDC PDFs — values should be spot-checked).
- **Boundaries:** Natural Earth 10m Admin-1 (public domain).
