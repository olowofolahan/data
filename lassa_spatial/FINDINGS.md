# Findings — phase 2 (models on available covariates)

Exploratory cross-sectional spatial regression of cumulative confirmed Lassa
fever cases across Nigeria's 37 states (2020–2026). **Only detection and
geography covariates are available so far** (climate, reservoir, poverty,
literacy, WASH, housing, population are pending data access — see
`VARIABLES.md`). Read these as a *detection-adjusted geographic baseline*, not
a causal ecological model.

## 1. The outcome is spatially clustered
Global Moran's I on log(confirmed) = **0.25, p = 0.007** (queen contiguity).
Significant High–High belt: Edo, Taraba, Benue, Plateau, Nasarawa, Delta.

## 2. But the clustering is largely a detection signal
| Model | Predictors | R² | Residual Moran's I |
|---|---|---|---|
| M2 geography-only | dist-to-lab, treatment centre, hotspot-adjacency, lat, lon | 0.69 | −0.05 (p=0.60) |
| **M1 + surveillance** | M2 **+ log(suspected)** | **0.94** | −0.02 (p=0.34) |

- `log(suspected)` is overwhelmingly dominant: β = **1.24, p < 0.0001**
  (confirmed cases scale almost 1:1 with suspected-case volume, i.e. with how
  much testing/surveillance a state does). NB model: IRR ≈ 3.8 per log-unit.
- Once surveillance effort is in the model, **no residual spatial
  autocorrelation remains**: LM-lag p = 0.10, LM-error p = 0.89; spatial-lag
  ρ = −0.17 (ns) and spatial-error λ = −0.04 (ns) do **not** improve on OLS
  (AIC 61.7 / 62.2 / 62.2). A non-spatial model is adequate for *these*
  covariates.
- `borders_hotspot` is positive (β = 0.41) but not significant (p = 0.15)
  after adjustment; `has_treatment_centre`, `centroid_lat`, `centroid_lon`,
  `dist_to_lab` add little once surveillance is controlled.

## 3. Interpretation
The apparent spatial pattern in *detected* cases is substantially explained by
**where surveillance and diagnostic testing are concentrated**, not (yet) by
identifiable ecological or socioeconomic structure. This is the detection
confound made quantitative. It does **not** mean ecology is unimportant — it
means the available predictors cannot separate true risk from detection. To do
that we need to:

1. **Model incidence** (cases per population, population offset) or
   **test-positivity** (`confirmed/suspected`) to partially break the
   detection confound.
2. Add the real drivers: reservoir suitability (*Mastomys*), climate, land
   cover, poverty/MPI, literacy, housing/WASH — the pending covariates.
3. Re-test residual spatial autocorrelation and, if present, use spatial
   lag/error or a Bayesian BYM (CAR) model.

---

# Phase 3 — full covariate models (incidence + poverty + reservoir + geography)

Covariates now collected (network unblocked): **population/density** (WorldPop
v2.0), **poverty** (OPHI subnational MPI, MICS 2021), **health-facility
density** (HDX registry, 46k facilities), **reservoir occurrences** (GBIF
*Mastomys* etc.), plus geography and surveillance proxies. Outcome switched to
**incidence** (confirmed / population, NB with log-pop offset) and
**test-positivity** (confirmed / suspected).

### The detection confound persists on raw incidence
In a model that includes the surveillance proxy `log(suspected)`, that term
alone dominates (IRR ≈ 8.6 per SD, p<0.001) and **no ecological or
socioeconomic covariate is significant**. But `log(suspected)` is a
*mediator/collider* of disease (more true cases → more suspected cases), so
including it over-adjusts.

### Ecological/SES model (no surveillance proxy) — real gradients emerge
NB incidence, IRR per 1 SD (offset = log population):

| Predictor | IRR | 95% CI | p | Reading |
|---|---|---|---|---|
| **Centroid latitude** | **0.09** | 0.04–0.18 | <0.001 | incidence falls steeply going north — the southern/central Lassa belt |
| **Population density** | **0.30** | 0.20–0.44 | <0.001 | denser (urban) states have lower per-capita incidence — Lassa is rural/peridomestic |
| **Poverty (MPI)** | **2.53** | 1.17–5.46 | 0.018 | after adjusting for the N–S gradient, higher poverty → higher incidence |
| GBIF *Mastomys* occ. | 1.03 | 0.74–1.45 | 0.86 | ns — occurrence counts too sampling-biased (Ondo, #1 hotspot, has 0 records) |

Residual spatial autocorrelation is absent after covariates (resid Moran's
I ≈ 0, LM-lag/error ns), so these covariates absorb the spatial structure;
a non-spatial NB is adequate at this scale.

### Honest caveats
- State scale (n=37) entangles **true risk** with **detection geography**
  (southern/central states also host the diagnostic labs). The truth lies
  between the two models above; clean separation needs LGA-level data or a
  direct testing-capacity measure.
- The raw non-monotonic poverty pattern (hotspots Ondo/Edo are low-poverty)
  was **latitude confounding** — poverty's effect is positive once geography
  is controlled.
- Still missing: **climate** (rainfall/temperature; WorldClim & CHIRPS hosts
  remain blocked) and a proper **reservoir suitability surface** (GBIF counts
  are not a substitute). Latitude is currently proxying the climate/vegetation
  gradient.

## Reproduce
```bash
cd src
python build_covariates_available.py   # geography/surveillance/lab covariates
python fetch_gbif_rodents.py            # GBIF reservoir occurrences
python build_population.py              # WorldPop population + density
python build_socioeconomic.py           # OPHI MPI + HDX health facilities
python assemble_master.py               # -> data/processed/master_state.csv
python fit_models.py                     # phase-2 detection models
python fit_models_full.py                # phase-3 incidence + positivity models
```
Figures: `outputs/spatial_eda_maps.png`, `detection_scatter.png`,
`incidence_drivers.png`.
