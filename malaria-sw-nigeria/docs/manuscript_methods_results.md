# Methods and Results (draft)

> Draft manuscript sections for *Climate-driven transmission dynamics and
> forecasting of malaria in South-West Nigeria*. Every numerical value here is
> computed by the code in this repository from open data; nothing is invented.
> Statistics follow APA 7th edition conventions. **Reference list entries should
> be verified against the originals before submission** (years, volumes, pages).
> The forecasting comparison uses a model-generated target pending routine case
> data; this is stated explicitly in the Design and Limitations (see the notes).

---

## 2. Methods

### 2.1 Study setting

The study covers the six states of Nigeria's South-West geopolitical zone —
Lagos, Oyo, Ogun, Osun, Ondo, and Ekiti — a predominantly tropical, perennially
endemic region in which *Plasmodium falciparum* is the dominant parasite. The
zone spans a gradient from the densely urbanised, coastal Lagos conurbation to
inland, more rural states. Nationally, WHO estimates of malaria incidence in
Nigeria declined from 401.8 per 1,000 population at risk in 2000 to 283.8 in
2015, then plateaued (294.3 in 2024; WHO Global Health Observatory), motivating
subnational analysis of where and when transmission persists.

### 2.2 Data sources

All inputs are openly available; access hosts and retrieval scripts are given in
the repository (`src/`).

**Parasite prevalence.** Modelled *P. falciparum* parasite rate standardised to
ages 2–10 years (PfPR₂₋₁₀) was obtained from the Malaria Atlas Project (MAP)
"Global Pf Parasite Rate" surface (release 202406) via the MAP OGC Web Coverage
Service as GeoTIFF, retaining the point-estimate band and the lower and upper
bounds of the 95% credible interval (Weiss et al., 2019).

**Climate.** Two WorldClim 2.1 products were used (Fick & Hijmans, 2017): (a) the
1970–2000 monthly climatological normals of precipitation and mean temperature at
2.5 arc-minute resolution, used as the baseline seasonal forcing for model
calibration; and (b) the historical monthly weather series (CRU TS 4.09
downscaled; Harris et al., 2020) at 10 arc-minute resolution for January 2010 to
December 2024, from which monthly precipitation and mean temperature
(tavg = [tmin + tmax] / 2) were derived for the interannual simulation and the
forecasting covariates.

**Administrative boundaries.** State (admin-1) polygons were taken from GADM
version 4.1 (Global Administrative Areas, 2022).

All gridded layers were reduced to state-level monthly series by zonal
arithmetic mean of raster cells intersecting each state polygon
(`rasterio.mask`); for PfPR, cells flagged by the MAP sparsely-populated mask or
carrying the nodata value were excluded.

### 2.3 Mechanistic transmission model

Transmission was represented by a deterministic, climate-forced compartmental
model of the Ross–Macdonald family (Macdonald, 1957): humans follow
Susceptible–Exposed–Infectious–Recovered (SEIR) dynamics and mosquitoes follow
Susceptible–Exposed–Infectious (SEI) dynamics, giving the seven-compartment
system

```
dS_h/dt = −λ_h S_h + ω R_h
dE_h/dt =  λ_h S_h − σ_h E_h
dI_h/dt =  σ_h E_h − γ I_h
dR_h/dt =  γ I_h − ω R_h
dS_v/dt =  μ_v N_v − λ_v S_v − μ_v S_v
dE_v/dt =  λ_v S_v − (n + μ_v) E_v
dI_v/dt =  n E_v − μ_v I_v
```

with human force of infection λ_h = m·a·b·(I_v / N_v) and mosquito force of
infection λ_v = a·c·(I_h / N_h), where m = N_v / N_h. Mosquito bionomic traits
were made temperature-dependent following the thermal-response framework of
Mordecai et al. (2013): the per-mosquito biting rate a(T) and the parasite
development rate n(T) = 1/EIP were modelled with Brière functions, and the
mosquito mortality rate μ_v(T) with a unimodal (quadratic-lifespan) function.
Larval carrying capacity scaled with monthly rainfall R through a saturating
function K(R) = 1.5·R/(R + 60), setting the baseline adult density
N_v = m₀·K·N_h. Fixed parameters are given in Table 1; temperature and rainfall
were supplied as periodic monthly forcings interpolated to daily resolution, and
the system was integrated with an adaptive Runge–Kutta solver
(`scipy.integrate.solve_ivp`).

The scaler m₀ is an **effective transmission-intensity (vector-density)
parameter** rather than a literal mosquito count; its scale is absorbed into the
fixed biting and transmission-efficiency constants, so calibration recovers
*relative* transmission intensity across states.

### 2.4 Calibration

Because PfPR₂₋₁₀ is age-standardised whereas the model yields all-age prevalence,
MAP targets were converted with a fixed factor of 0.83 (a pragmatic
approximation of the age-standardised–to–all-age relationship; cf. Smith et al.,
2007). For each state, m₀ was estimated by solving, with Brent's method
(`scipy.optimize.brentq`; search interval [0.05, 20]), the equation

  annual-mean simulated prevalence(m₀) = 0.83 × PfPR₂₋₁₀,

under the 1970–2000 climatological forcing, with an 8-year spin-up to remove
transient dependence on initial conditions. All other parameters were held at the
Table 1 values and shared across states, so between-state differences are
attributed to climate forcing and the single fitted m₀.

### 2.5 Interannual simulation

Each calibrated state model was then driven by its **observed** 2010–2024 monthly
climate (CRU TS) to generate a monthly all-age prevalence hindcast
(*N* = 1,080 state-months = 6 states × 180 months), following a 4-year spin-up on
the first year's climate. This series carries genuine interannual variation
arising from observed rainfall and temperature anomalies.

### 2.6 Forecasting models

Four one-step-to-six-step forecasters were compared on the monthly series:

1. **Seasonal-naïve** (baseline): ŷ_{t+h} = y_{t+h−12}.
2. **Mechanistic-climatology**: the state × calendar-month mean of the target —
   the structural seasonal expectation, carrying no year-specific information.
3. **SARIMAX**(1,0,1)(1,0,0)₁₂ with monthly rainfall and temperature as
   exogenous regressors (`statsmodels`; Seabold & Perktold, 2010).
4. **Gradient boosting**: histogram gradient-boosted regression trees
   (`scikit-learn` `HistGradientBoostingRegressor`; max_depth = 4,
   learning_rate = 0.06, 300 iterations, L2 = 1.0; Pedregosa et al., 2011) on
   features {y_{t−1}, y_{t−12}, 3-month rainfall sum, sin/cos of calendar month,
   and rainfall and temperature at lags 1–3}, applied **recursively** for
   multi-step horizons (predictions fed back into the autoregressive lags).

Climate covariates over the forecast horizon were treated as known (a
**perfect-climate** scenario), isolating malaria-dynamics forecast skill from
climate-forecast error.

### 2.7 Evaluation design

Models were evaluated by **rolling-origin cross-validation** with an expanding
training window: the first forecast origin followed 60 months of training, and
forecasts were issued at horizons h = 1–6 months for every subsequent origin, in
each state (4,194 forecast–observation pairs per model). Accuracy was summarised
by root-mean-square error (RMSE) and mean absolute error (MAE), and by a skill
score relative to the seasonal-naïve baseline,
skill = 1 − RMSE_model / RMSE_naïve. Pairwise predictive accuracy was tested with
the Diebold–Mariano test (Diebold & Mariano, 1995) on squared-error loss, using a
Newey–West long-run variance (truncation lag h − 1) and the Harvey–Leybourne–
Newbold small-sample correction (Harvey et al., 1997); tests were computed per
state and on the pooled loss differentials.

**Design note.** The forecasting target is the mechanistic hindcast, a
model-generated series. This is a controlled benchmark of forecaster behaviour
under a known climate-driven signal, **not** an empirical validation against
observed cases; the mechanistic-climatology forecaster is, by construction, the
climatological component of the target. Absolute skill magnitudes should
therefore be read as properties of the comparison design. The pipeline is built
to substitute routine monthly case counts (DHIS2/NMEP) as the target without
modification once those data are obtained.

### 2.8 Software and reproducibility

Analyses used Python 3.13 with numpy 2.5.3, scipy 1.18.1, pandas 3.0.5,
scikit-learn 1.9.1, statsmodels 0.15.0, geopandas 1.2.0, and rasterio 1.5.2. All
retrieval, calibration, simulation, and evaluation scripts, and the processed
data tables, are in the project repository.

---

## 3. Results

### 3.1 Environmental and prevalence gradient

Across 2010–2024, mean annual rainfall ranged from 1,198 mm (*SD* = 134) in Oyo
to 1,652 mm (*SD* = 221) in Lagos, and mean monthly temperature from 25.3 °C
(*SD* = 1.35) in Ekiti to 27.8 °C (*SD* = 1.26) in Lagos (Table 2). Modelled
PfPR₂₋₁₀ (MAP, 2022) averaged .458 (*SD* = .132) across the six states but was
markedly heterogeneous: Lagos was the clear low outlier at .210, 95% CI
[.113, .354], whereas the five less-urbanised states ranged from .419 (Ogun) to
.567 (Osun) — consistent with the expected suppression of transmission in the
highly urbanised Lagos conurbation.

**Table 2**
*State-level environmental conditions (2010–2024) and modelled* P. falciparum
*parasite prevalence (MAP release 202406)*

| State | Annual rainfall (mm), *M* (*SD*) | Temperature (°C), *M* (*SD*) | PfPR₂₋₁₀ | 95% CI |
|-------|-------------------------------:|----------------------------:|---------:|:------------:|
| Lagos | 1,652 (221) | 27.77 (1.26) | .210 | [.113, .354] |
| Ogun  | 1,446 (183) | 27.53 (1.37) | .419 | [.223, .634] |
| Oyo   | 1,198 (134) | 26.97 (1.53) | .535 | [.232, .824] |
| Osun  | 1,391 (145) | 26.46 (1.31) | .567 | [.284, .831] |
| Ondo  | 1,645 (133) | 26.53 (1.24) | .496 | [.202, .779] |
| Ekiti | 1,302 (110) | 25.30 (1.35) | .522 | [.169, .834] |

*Note.* CI = credible interval from the MAP posterior. Rainfall *SD* is the
between-year standard deviation of annual totals; temperature *M* and *SD* are
over all state-months.

### 3.2 Mechanistic calibration

The calibrated model reproduced the MAP targets essentially exactly: absolute
residuals did not exceed .0004 in any state (calibration RMSE = .0002; Table 3).
The fitted effective vector density m₀ increased monotonically across the
transmission gradient, from 0.25 in Lagos to 0.79 in Ekiti, and was strongly
associated with PfPR₂₋₁₀ (Pearson *r* = .93, *p* = .008; Spearman *r_s* = .83,
*p* = .042). Importantly, the ordering of m₀ was not identical to that of
prevalence: Ekiti required a higher fitted density than Oyo (0.79 vs. 0.69)
despite a lower PfPR (.522 vs. .535), because its cooler mean temperature
(25.3 °C vs. 27.0 °C) and lower rainfall render the local climate less suitable
for transmission. The model thus separates *climatic suitability* from *residual
transmission intensity*, which the raw prevalence surface confounds.

**Table 3**
*Per-state calibration of the climate-forced transmission model to MAP PfPR*

| State | PfPR₂₋₁₀ | All-age target | Fitted m₀ | Simulated prevalence | Residual |
|-------|---------:|---------------:|----------:|---------------------:|---------:|
| Lagos | .210 | .174 | 0.25 | .174 | −.0004 |
| Ogun  | .419 | .348 | 0.43 | .348 | −.0000 |
| Ondo  | .496 | .412 | 0.55 | .412 | −.0000 |
| Oyo   | .535 | .444 | 0.69 | .444 | +.0001 |
| Osun  | .567 | .471 | 0.74 | .471 | +.0001 |
| Ekiti | .522 | .433 | 0.79 | .433 | +.0000 |

*Note.* All-age target = 0.83 × PfPR₂₋₁₀. Residual = simulated − target
(prevalence units). m₀ is an effective transmission-intensity scaler.

### 3.3 Interannual hindcast

Driven by observed 2010–2024 climate, the calibrated models produced monthly
prevalence series that preserved the between-state ordering (mean prevalence
.199 in Lagos to .489 in Osun) and exhibited a coherent, climate-driven seasonal
cycle: in all six states the within-year minimum occurred in April and the
maximum in December, lagging the mid-year rains. Within-year seasonal amplitude
ranged from .068 (Lagos) to .151 (Oyo), and interannual variability (the
standard deviation of monthly prevalence) from .015 (Lagos) to .036 (Oyo),
indicating that the wetter, warmer, lower-transmission dynamics in Lagos were
also the most temporally stable.

### 3.4 Forecast comparison

Pooled over all states and horizons (h = 1–6), gradient boosting was the most
accurate forecaster (RMSE = .0113, MAE = .0088), followed by the
mechanistic-climatology model (RMSE = .0128, MAE = .0106), the seasonal-naïve
baseline (RMSE = .0165, MAE = .0135), and SARIMAX (RMSE = .0230, MAE = .0179).
The horizon-resolved results (Table 4) reveal a systematic crossover. At a
one-month horizon the data-driven models dominated — gradient boosting and
SARIMAX reduced RMSE by 51.9% and 39.3% relative to the seasonal-naïve baseline —
but their advantage decayed with horizon, whereas the mechanistic-climatology
model held a stable ≈ 22–24% skill at all horizons. By five to six months the
mechanistic model matched or exceeded gradient boosting, while SARIMAX
deteriorated to 57–73% *worse* than the naïve baseline as its recursive multi-step
errors compounded.

**Table 4**
*Forecast accuracy (RMSE) and skill relative to the seasonal-naïve baseline, by
model and horizon (rolling-origin cross-validation, six states)*

| Horizon (months) | Seasonal-naïve RMSE | Mechanistic RMSE (skill) | SARIMAX RMSE (skill) | Gradient boosting RMSE (skill) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | .0164 | .0128 (21.9%) | .0099 (39.3%) | .0079 (51.9%) |
| 2 | .0164 | .0128 (21.9%) | .0177 (−7.5%) | .0099 (39.7%) |
| 3 | .0165 | .0129 (22.0%) | .0228 (−38.0%) | .0113 (31.4%) |
| 4 | .0166 | .0128 (22.6%) | .0259 (−56.7%) | .0122 (26.6%) |
| 5 | .0166 | .0127 (23.5%) | .0277 (−67.3%) | .0129 (22.3%) |
| 6 | .0166 | .0126 (24.2%) | .0287 (−73.2%) | .0132 (20.7%) |

*Note.* Skill = 1 − RMSE_model / RMSE_naïve (positive = better than naïve).
RMSE is in prevalence units. Climate covariates were treated as known over the
horizon (perfect-climate scenario).

Diebold–Mariano tests confirmed these patterns (Table 5). At h = 1, gradient
boosting significantly outperformed every alternative — versus seasonal-naïve
(*DM* = −16.91, *p* < .001), mechanistic-climatology (*DM* = −14.18, *p* < .001),
and SARIMAX (*DM* = −4.16, *p* < .001), with all six per-state tests favouring
gradient boosting in the first two contrasts. At h = 6, however, gradient
boosting's edge over the mechanistic model disappeared (*DM* = +0.94, *p* = .349;
no per-state test significant in either direction), while gradient boosting
remained significantly better than both seasonal-naïve (*DM* = −3.64, *p* < .001)
and SARIMAX (*DM* = −8.82, *p* < .001). The mechanistic-climatology model
significantly beat the naïve baseline at both horizons (h = 1: *DM* = −8.68; h = 6:
*DM* = −4.81; both *p* < .001). SARIMAX significantly beat the baseline at h = 1
(*DM* = −11.88, *p* < .001) but was significantly *worse* at h = 6 (*DM* = +8.55,
*p* < .001; five of six states favouring the baseline).

**Table 5**
*Diebold–Mariano tests of equal predictive accuracy (squared-error loss), pooled
across states*

| Contrast (Model A vs. Model B) | Horizon | *DM* | *p* | States favouring A |
|---|:---:|:---:|:---:|:---:|
| Gradient boosting vs. seasonal-naïve | 1 | −16.91 | < .001 | 6/6 |
| Gradient boosting vs. seasonal-naïve | 6 | −3.64 | < .001 | 1/6 |
| Gradient boosting vs. mechanistic | 1 | −14.18 | < .001 | 6/6 |
| Gradient boosting vs. mechanistic | 6 | +0.94 | .349 | 0/6 |
| Gradient boosting vs. SARIMAX | 1 | −4.16 | < .001 | 4/6 |
| Gradient boosting vs. SARIMAX | 6 | −8.82 | < .001 | 6/6 |
| Mechanistic vs. seasonal-naïve | 1 | −8.68 | < .001 | 6/6 |
| Mechanistic vs. seasonal-naïve | 6 | −4.81 | < .001 | 5/6 |
| SARIMAX vs. seasonal-naïve | 1 | −11.88 | < .001 | 5/6 |
| SARIMAX vs. seasonal-naïve | 6 | +8.55 | < .001 | 0/6 (5/6 favour naïve) |

*Note.* Negative *DM* indicates Model A has lower squared-error loss than Model B.
*p* from the Harvey–Leybourne–Newbold-corrected statistic, *t* reference
distribution. "States favouring A" counts the six per-state tests significant at
α = .05 in A's favour. Loss differentials from overlapping rolling-origin windows
are serially dependent; the Newey–West variance mitigates but does not eliminate
this, so *p*-values are approximate.

### 3.5 Summary

Three findings emerge. First, a parsimonious climate-forced transmission model,
calibrated through a single effective-density parameter, reproduces the
MAP-estimated prevalence gradient across South-West Nigeria and disentangles
climatic suitability from residual transmission intensity (Lagos lowest; Ekiti
climatically least suitable). Second, the resulting dynamics are strongly
seasonal, peaking in December and troughing in April across all states. Third, in
a controlled forecasting benchmark, machine learning is most accurate for
short-range prediction whereas the mechanistic model's structural seasonal signal
is more robust at longer horizons, the two becoming statistically
indistinguishable by six months — a quantitative basis for a hybrid strategy
(machine learning for nowcasting, mechanistic structure for long-range
projection). These forecasting magnitudes are established on a model-generated
target and require confirmation against routine surveillance data.

---

## Limitations (abridged — for Discussion)

- The forecasting comparison uses the mechanistic hindcast as the target;
  empirical validation requires routine monthly case data (DHIS2/NMEP), which are
  access-restricted. The pipeline accepts such data without modification.
- The PfPR₂₋₁₀-to-all-age conversion uses a fixed factor (0.83) rather than the
  prevalence-dependent relationship; m₀ is an effective, not mechanistic,
  density; and several thermal responses use literature-form approximations.
- Climate covariates were treated as known over the forecast horizon; operational
  skill would additionally depend on climate-forecast error.
- MAP prevalence is itself modelled (not observation), and the calibration uses a
  single reference year; an annual PfPR time series would permit interannual
  calibration and out-of-sample validation of the transmission model.

## References (verify before submission)

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy.
*Journal of Business & Economic Statistics, 13*(3), 253–263.

Fick, S. E., & Hijmans, R. J. (2017). WorldClim 2: New 1-km spatial resolution
climate surfaces for global land areas. *International Journal of Climatology,
37*(12), 4302–4315.

Global Administrative Areas. (2022). *GADM database of global administrative
areas* (Version 4.1). https://gadm.org

Harris, I., Osborn, T. J., Jones, P., & Lister, D. (2020). Version 4 of the CRU
TS monthly high-resolution gridded multivariate climate dataset. *Scientific
Data, 7*, 109.

Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality of
prediction mean squared errors. *International Journal of Forecasting, 13*(2),
281–291.

Macdonald, G. (1957). *The epidemiology and control of malaria.* Oxford
University Press.

Mordecai, E. A., Paaijmans, K. P., Johnson, L. R., Balzer, C., Ben-Horin, T., de
Moor, E., McNally, A., Pawar, S., Ryan, S. J., Smith, T. C., & Lafferty, K. D.
(2013). Optimal temperature for malaria transmission is dramatically lower than
previously predicted. *Ecology Letters, 16*(1), 22–30.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O.,
Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos,
A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011).
Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research,
12*, 2825–2830.

Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical
modeling with Python. *Proceedings of the 9th Python in Science Conference*,
92–96.

Smith, D. L., Guerra, C. A., Snow, R. W., & Hay, S. I. (2007). Standardizing
estimates of the *Plasmodium falciparum* parasite rate. *Malaria Journal, 6*,
131.

Weiss, D. J., Lucas, T. C. D., Nguyen, M., Nandi, A. K., Bisanzio, D., Battle, K.
E., Cameron, E., Twohig, K. A., Pfeffer, D. A., Rozier, J. A., Gibson, H. S.,
Rao, P. C., Casey, D., Bertozzi-Villa, A., Collins, E. L., Dalrymple, U., Gray,
N., Harris, J. R., Howes, R. E., … Gething, P. W. (2019). Mapping the global
prevalence, incidence, and mortality of *Plasmodium falciparum*, 2000–17: A
spatial and temporal modelling study. *The Lancet, 394*(10195), 322–331.

World Health Organization. (2024). *World Malaria Report 2024.* WHO Global Health
Observatory (malaria indicators). https://www.who.int/data/gho
