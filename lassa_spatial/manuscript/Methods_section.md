# Methods

*Note on reporting.* This section describes an ecological spatial
disease-mapping study of Lassa fever across Nigeria's 37 first-order
administrative units. Reporting follows APA 7th edition; statistical symbols
are italicised in the manuscript (*M*, *SD*, *I*, *z*, *p*, *R²*, IRR, *φ*,
$\hat{R}$).

## Study design and setting

We conducted a retrospective, ecological (area-level) analysis of
laboratory-confirmed Lassa fever across the 36 states of Nigeria and the
Federal Capital Territory (*N* = 37 units). The unit of analysis was the
state; the observation window spanned epidemiological week 6 of 2020 to week
34 of 2026. Because the design is ecological, all associations describe
state-level relationships and are not interpreted as individual-level
(person-level) effects.

## Outcome data

Weekly counts of suspected, confirmed, and fatal Lassa fever cases by state
were obtained from the Nigeria Centre for Disease Control and Prevention
(NCDC) weekly situation reports, as compiled in the open BioDivHealth
*LF_Nigeria_Reports* repository (Creative Commons CC0). Because the compilation
was extracted from report tables, values were checked for internal
consistency (suspected ≥ confirmed ≥ deaths) and blank cells were treated as
zero. Weekly records were aggregated to cumulative state totals over the study
window. The primary outcome was the **incidence of confirmed cases**, modelled
as a count with the state population as the exposure (offset); the cumulative
confirmed count and test positivity (confirmed ÷ suspected) were examined as
secondary outcomes.

## Covariates

State-level covariates were assembled to represent the hypothesised
determinants of Lassa fever risk (reservoir ecology, climate, socioeconomic
deprivation, demography, and health-system/surveillance capacity). Sources and
processing are summarised in Table M1.

- **Population and density.** Modelled population estimates were taken from
  WorldPop bottom-up gridded estimates (version 2.0); density was computed as
  population divided by polygon area in an equal-area projection (UTM Zone 32N).
- **Climate.** WorldClim 2.1 bioclimatic normals (1970–2000, 5-arc-minute
  resolution) were summarised to state polygons as zonal means for annual mean
  temperature, temperature seasonality, annual precipitation, precipitation of
  the driest month, and precipitation seasonality.
- **Socioeconomic deprivation.** The subnational Multidimensional Poverty Index
  (MPI) and poverty headcount were obtained from the Oxford Poverty and Human
  Development Initiative (Multiple Indicator Cluster Survey, 2021), distributed
  through the Humanitarian Data Exchange (HDX).
- **Health system.** Health-facility density (facilities per 100,000
  population) was derived from the HDX Nigeria health-facility registry.
- **Reservoir.** Georeferenced occurrence records of *Mastomys natalensis* (the
  primary Lassa virus reservoir) and related rodents were retrieved from the
  Global Biodiversity Information Facility (GBIF) and aggregated to states by
  point-in-polygon overlay; occurrence counts index sampling effort as well as
  true abundance and were therefore treated as a coarse sensitivity covariate.
- **Geography and surveillance.** State centroid latitude and longitude,
  distance to the nearest NCDC Lassa diagnostic laboratory, and surveillance
  intensity (log suspected cases) were derived from the boundary file and the
  surveillance record.

State boundaries were taken from Natural Earth (1:10 m admin-1); names were
harmonised across sources to the 37 NCDC units.

## Statistical analysis

Analyses proceeded from exploratory spatial statistics to a Bayesian
hierarchical disease-mapping model.

**Spatial autocorrelation.** Global clustering of (log) case burden, incidence,
and test positivity was assessed with Moran's *I* using a row-standardised
queen-contiguity spatial weights matrix, with inference by 9,999 random
permutations. Local clusters were identified with local indicators of spatial
association (local Moran's *I*; 9,999 permutations), classified as high–high,
low–low, or spatial outliers at *p* < .05.

**Covariate regression.** Because case counts were overdispersed, state
incidence was modelled with negative binomial regression using population as
the exposure and a freely estimated dispersion parameter (*α*). Continuous
predictors were *z*-standardised so that coefficients express incidence-rate
ratios (IRRs) per one standard-deviation increase. Multicollinearity among the
candidate predictors was quantified with variance inflation factors (VIF) and a
principal-components analysis; because latitude, climate, and poverty formed a
single dominant gradient (first principal component = 91.3% of variance), a
parsimonious specification retained one mechanistic gradient proxy
(precipitation seasonality) together with the orthogonal population-density
term. The spatial-econometric workflow (ordinary least squares with
Lagrange-multiplier tests for spatial lag and spatial error, followed by
maximum-likelihood spatial lag and spatial error models) was used to test for
residual spatial dependence.

**Bayesian spatial disease-mapping model.** The primary spatial model was a
Bayesian hierarchical negative binomial model of the Besag–York–Mollié (BYM)
form. For state *i* with population *E*ᵢ,

$$y_i \sim \text{NegBin}(\mu_i, \alpha), \quad \log \mu_i = \log E_i + \beta_0 + \mathbf{x}_i^\top \boldsymbol{\beta} + \sigma_u\, u_i + \sigma_\theta\, \theta_i,$$

where **x**ᵢ contained the parsimonious fixed effects (precipitation
seasonality and log population density), *u*ᵢ was a spatially structured
intrinsic conditional autoregressive (ICAR) random effect defined on the queen
adjacency graph (37 nodes, 87 edges), and *θ*ᵢ was an unstructured independent
random effect. Weakly informative priors were used: *β* ~ Normal(0, 1), *β*₀ ~
Normal(0, 5), *σ*ᵤ and *σ*₍θ₎ ~ Half-Normal(1), and *α* ~ Half-Normal(5). The
proportion of residual area-level variance attributable to spatial structure
(the spatial fraction, *φ*) was computed from the posterior as the variance of
the structured component divided by the total random-effect variance. A
smoothed residual spatial relative-risk surface was mapped as the posterior
mean of exp(*σ*ᵤ *u*).

**Estimation and model comparison.** The model was estimated by Hamiltonian
Monte Carlo (No-U-Turn Sampler) with 4 chains of 1,500 post-warmup draws
(2,500 warmup; target acceptance 0.99). Convergence was assessed with the
potential scale reduction factor ($\hat{R}$ ≤ 1.01) and effective sample
sizes. The spatial model was compared with an otherwise identical non-spatial
model by approximate leave-one-out cross-validation (expected log pointwise
predictive density, ELPD).

**Software.** Analyses were conducted in Python 3.13 using geopandas and
rasterstats (spatial processing and zonal statistics), libpysal, esda, and
spreg (spatial weights, Moran's *I*, spatial econometric models), statsmodels
(negative binomial regression), and PyMC with ArviZ (Bayesian estimation and
model comparison). Analysis code and the assembled covariate data are openly
available in the project repository.

---

## Table M1

*Data Sources and State-Level Covariates*

| Domain | Variable(s) | Source | Processing |
|---|---|---|---|
| Outcome | Suspected, confirmed, fatal cases | NCDC weekly reports (BioDivHealth, CC0) | Weekly → cumulative state totals |
| Demography | Population, density | WorldPop v2.0 | Admin-1 table; density = pop ÷ area |
| Climate | Temperature, rainfall, seasonality | WorldClim 2.1 (5 arc-min) | Zonal means over state polygons |
| Deprivation | MPI, poverty headcount | OPHI subnational MPI (MICS 2021), via HDX | State table |
| Health system | Facilities per 100,000 | HDX health-facility registry | Count ÷ population |
| Reservoir | *Mastomys* occurrences | GBIF | Point-in-polygon counts |
| Geography | Latitude, lab distance | Natural Earth admin-1 | Centroids; nearest-lab distance |
| Surveillance | Suspected-case volume | NCDC weekly reports | log(1 + suspected) |

*Note.* MPI = Multidimensional Poverty Index; HDX = Humanitarian Data Exchange;
GBIF = Global Biodiversity Information Facility; NCDC = Nigeria Centre for
Disease Control and Prevention. All covariates were resolved to the 37
first-order units (36 states and the Federal Capital Territory).
