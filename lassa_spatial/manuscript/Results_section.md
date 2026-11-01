# Results

*Note on reporting.* Statistics follow APA 7th edition. Test statistics and
parameter symbols are italicised in the manuscript (*M*, *SD*, *Mdn*, *N*,
*p*, *r*, *R²*, *F*, *z*, *I*, *B*, *SE*); leading zeros are omitted for
statistics that cannot exceed one in absolute value (*p*, *r*, *R²*, Moran's
*I*). Incidence-rate ratios are denoted IRR with 95% confidence intervals in
brackets. All analyses were conducted in Python 3.13 (statsmodels 0.15,
PySAL/spreg 1.9, esda) on the 37 Nigerian first-order administrative units
(36 states and the Federal Capital Territory).

## Descriptive epidemiology

Between epidemiological week 6 of 2020 and week 34 of 2026, the Nigeria Centre
for Disease Control recorded 7,006 laboratory-confirmed Lassa fever cases and
1,128 associated deaths across the 37 states, an overall case-fatality rate of
16.10%. The burden was highly concentrated: the five most affected states
(Ondo, Edo, Bauchi, Taraba, and Ebonyi) together accounted for 86.3% of all
confirmed cases, whereas 9 states reported fewer than 5 confirmed cases over
the entire period and 1 state (Osun) reported none. Confirmed case counts were
strongly right-skewed (*M* = 189.35, *SD* = 496.87, *Mdn* = 13.00, range
0–2,372), as were state incidence rates (*M* = 4.39, *SD* = 13.35, *Mdn* =
0.31 per 100,000, range 0–70.66). Descriptive statistics for the outcome and
candidate predictors are presented in Table 1.

## Spatial dependence in disease burden

Global spatial autocorrelation was assessed with Moran's *I* using a
row-standardised queen-contiguity spatial weights matrix (mean = 4.70
neighbours; no islands). Log-transformed confirmed case counts were
significantly positively autocorrelated, *I* = .25, *z* = 2.65, *p* = .007,
indicating that high- and low-burden states were spatially clustered rather
than randomly distributed. The clustering persisted, with attenuation, for
log incidence, *I* = .19, *z* = 2.16, *p* = .029, and for logit-transformed
test positivity, *I* = .18, *z* = 2.01, *p* = .031.

Local indicators of spatial association (local Moran's *I*, 9,999
permutations) identified a single statistically significant high–high cluster
(*p* < .05) comprising a contiguous central–southern belt: Edo, Taraba, Benue,
Plateau, Nasarawa, and Delta. No significant low–low cluster was detected. The
choropleth of confirmed cases and the LISA cluster map are shown in Figure 1.

## Bivariate associations

At the bivariate level, state incidence (log scale) was weakly and negatively
correlated with latitude (*r* = −.20), population density (*r* = −.21), and
multidimensional poverty (*r* = −.09). These simple associations were
attenuated by the strongly right-skewed outcome, which was dominated by two
low-latitude southern outliers (Ondo and Edo). The predictors were themselves
intercorrelated—most strongly latitude with poverty (*r* = .89), reflecting
Nigeria's north–south socioeconomic gradient, and latitude with
health-facility density (*r* = −.57)—so their independent contributions are
better assessed in the multivariable models below. These bivariate patterns
are displayed in Figure 2. The number of georeferenced *Mastomys natalensis*
occurrences (the primary reservoir) was uncorrelated with incidence
(*r* = −.06); because occurrence records reflect trapping effort rather than
abundance (the highest-incidence state, Ondo, had zero records), this variable
was retained only as a sensitivity covariate.

## Negative binomial regression of incidence

Given the overdispersed count outcome, state incidence was modelled with
negative binomial regression using population as the exposure (equivalent to a
log-population offset); the dispersion parameter (*α*) was freely estimated.
Continuous predictors were *z*-standardised, so IRRs express the
multiplicative change in incidence per 1 *SD* increase. Two models are
reported in Table 2. Model 1 (ecological–socioeconomic) included the
hypothesised structural determinants; Model 2 additionally adjusted for
surveillance effort (log suspected cases), proximity to a diagnostic
laboratory, and health-facility density.

In Model 1 (*α* = 2.70), incidence was independently and strongly associated
with latitude, IRR = 0.09, 95% CI [0.02, 0.43], *z* = −3.02, *p* = .003, and
with population density, IRR = 0.30, 95% CI [0.12, 0.78], *z* = −2.46,
*p* = .014: each standard-deviation increase in latitude or in log population
density corresponded to a roughly 91% and 70% lower incidence, respectively.
Multidimensional poverty showed a positive but non-significant association
once the north–south gradient was accounted for, IRR = 2.51, 95% CI
[0.68, 9.18], *z* = 1.39, *p* = .166, and reservoir occurrence was null,
IRR = 1.03, 95% CI [0.61, 1.76], *p* = .909.

In Model 2 (*α* = 0.19), surveillance effort dominated: log suspected cases
was by far the strongest correlate of confirmed incidence, IRR = 8.14, 95% CI
[6.36, 10.41], *z* = 16.69, *p* < .001. Two further detection-related
covariates were significant—distance to the nearest diagnostic laboratory,
IRR = 1.60, 95% CI [1.19, 2.16], *p* = .002, and health-facility density,
IRR = 1.43, 95% CI [1.11, 1.84], *p* = .005—whereas latitude (*p* = .111),
population density (*p* = .069), poverty (*p* = .631), and reservoir
occurrence (*p* = .228) were no longer statistically significant. Model 2
provided a substantially better fit than Model 1 (AIC = 297.2 vs. 395.2;
McFadden *R²* = .30 vs. .05), consistent with detected cases being governed
heavily by where and how intensively surveillance was conducted.

## Model adequacy and residual spatial structure

To confirm that the covariates captured the observed spatial clustering, an
ordinary least squares model of log incidence on the full predictor set was
examined for residual autocorrelation. The model explained most of the
variance, *R²* = .88, adjusted *R²* = .85, *F*(7, 29) = 31.17, *p* < .001, and
its residuals exhibited no remaining spatial dependence (residual Moran's
*I* = −.02, *z* = 0.82, *p* = .41). Lagrange multiplier tests were
non-significant for both a spatial lag (*p* = .095; robust *p* = .060) and a
spatial error process (*p* = .85; robust *p* = .38). Spatial lag and spatial
error maximum-likelihood models yielded small, negatively signed and
non-interpretable autoregressive parameters (*ρ* = −.28; *λ* = −.07) and did
not materially improve fit over the non-spatial specification (lag AIC =
43.6, error AIC = 45.2, OLS AIC = 45.3). A non-spatial negative binomial
model was therefore retained as adequate at this spatial scale.

The relationship between confirmed and suspected cases that underlies Model 2
is illustrated in Figure 3.

---

## Table 1

*Descriptive Statistics for Lassa Fever Burden and Candidate State-Level
Predictors (N = 37 States)*

| Variable | *M* | *SD* | *Mdn* | Min | Max |
|---|---:|---:|---:|---:|---:|
| Confirmed cases (cumulative) | 189.35 | 496.87 | 13.00 | 0 | 2,372 |
| Incidence (per 100,000) | 4.39 | 13.35 | 0.31 | 0.00 | 70.66 |
| Test positivity (%) | 9.22 | 7.29 | 8.92 | 0.00 | 35.31 |
| Deaths | 30.49 | 66.67 | 3.00 | 0 | 294 |
| Case-fatality rate (%) | 23.15 | 21.95 | 18.61 | 0.00 | 100.00 |
| Population (millions) | 5.86 | 3.11 | 5.08 | 1.08 | 17.62 |
| Population density (per km²) | 408.24 | 466.03 | 244.00 | 84.50 | 2,676.00 |
| Multidimensional Poverty Index | 0.16 | 0.15 | 0.09 | 0.00 | 0.44 |
| Poverty headcount (%) | 31.22 | 24.88 | 19.95 | 1.11 | 75.36 |
| Health facilities (per 100,000) | 24.70 | 11.83 | 22.80 | 8.90 | 72.90 |
| *M. natalensis* occurrences (GBIF) | 3.73 | 6.45 | 0.00 | 0 | 24 |
| Centroid latitude (°N) | 8.47 | 2.52 | 8.03 | 4.77 | 13.03 |

*Note.* Burden figures are cumulative over epidemiological week 6 of 2020 to
week 34 of 2026 (Nigeria Centre for Disease Control weekly situation reports).
Population and density from WorldPop bottom-up estimates (v2.0); poverty from
the Oxford Poverty and Human Development Initiative subnational
Multidimensional Poverty Index (MICS 2021); health facilities from the
Humanitarian Data Exchange national registry; reservoir occurrences from the
Global Biodiversity Information Facility. The case-fatality rate row
summarises state-level ratios; the population-weighted national rate was
16.10%.

---

## Table 2

*Negative Binomial Regression of State Lassa Fever Incidence (N = 37)*

| Predictor (per 1 *SD*) | Model 1: Ecological IRR [95% CI] | Model 2: Surveillance-adjusted IRR [95% CI] |
|---|---|---|
| Multidimensional Poverty Index | 2.51 [0.68, 9.18] | 1.11 [0.73, 1.69] |
| Population density (log) | 0.30 [0.12, 0.78]* | 0.80 [0.63, 1.02] |
| *M. natalensis* occurrences | 1.03 [0.61, 1.76] | 0.90 [0.76, 1.07] |
| Centroid latitude | 0.09 [0.02, 0.43]** | 0.71 [0.46, 1.08] |
| Health facilities (per 100,000) | — | 1.43 [1.11, 1.84]** |
| Distance to nearest laboratory | — | 1.60 [1.19, 2.16]** |
| Suspected cases (log) | — | 8.14 [6.36, 10.41]*** |
| Dispersion (*α*) | 2.70 | 0.19 |
| McFadden *R²* | .05 | .30 |
| AIC | 395.2 | 297.2 |

*Note.* IRR = incidence-rate ratio per one standard-deviation increase in the
predictor; models use population as the exposure. Model 2 adds
surveillance/detection covariates. Em dashes indicate predictors not entered
in Model 1.
\**p* < .05. \***p* < .01. \****p* < .001.

---

## Figure captions

**Figure 1.** *Spatial distribution and local clustering of confirmed Lassa
fever cases across Nigerian states, 2020–2026.* Left: cumulative confirmed
cases (quantile classes). Right: local Moran's *I* (LISA) clusters; the
shaded high–high belt (Edo, Taraba, Benue, Plateau, Nasarawa, Delta) was
statistically significant at *p* < .05 (global Moran's *I* = .25, *p* = .007).

**Figure 2.** *Bivariate relationships between state Lassa fever incidence and
its principal determinants.* Incidence (log scale, per 100,000) plotted
against centroid latitude, population density, and the Multidimensional
Poverty Index, with ordinary least squares fit lines and Pearson correlations.

**Figure 3.** *Confirmed cases as a function of surveillance effort.*
Log-transformed confirmed versus suspected cases by state; states bordering
the high–high cluster are highlighted. The near-linear relationship (OLS
*R²* = .94) illustrates the dependence of detected burden on surveillance
intensity.
