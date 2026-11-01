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

## Reproduce
```bash
cd src
python build_covariates_available.py   # -> data/processed/covariates_available.csv
python fit_models.py                    # -> model comparison + data/processed/model_frame.csv
```
Outputs: `outputs/spatial_eda_maps.png`, `outputs/detection_scatter.png`.
