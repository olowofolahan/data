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

## Climate covariates and the dimensionality of the risk gradient

State-level climate normals (WorldClim 2.1, 5-arc-minute zonal means) mirrored
the latitudinal gradient closely: annual rainfall ranged from 488 mm in the
arid northeast (Yobe) to 3,115 mm on the southern coast (Bayelsa), and the
southern high-incidence states (Ondo, Edo, Ebonyi) received 1,659–1,880 mm.
Climate was, however, almost perfectly collinear with the other gradient
predictors. Centroid latitude was correlated *r* = −.92 with annual rainfall,
*r* = .95 with rainfall seasonality, *r* = .97 with temperature seasonality,
and *r* = .89 with multidimensional poverty. Variance inflation factors in a
combined model were accordingly extreme (temperature seasonality = 56.0,
rainfall seasonality = 41.4, latitude = 34.8, annual rainfall = 9.3, poverty =
7.0), whereas population density was effectively orthogonal (VIF = 1.3). A
principal-components analysis of the five gradient variables confirmed their
redundancy: the first component alone accounted for 91.3% of their variance.
Latitude, climate, and poverty therefore represent a single latent north–south
axis and cannot be identified separately at this spatial scale.

A low-collinearity model retaining one mechanistic gradient proxy (rainfall
seasonality) together with the orthogonal density term reproduced the pattern
cleanly and stably: incidence fell with rainfall seasonality, IRR = 0.31, 95%
CI [0.17, 0.57], *p* < .001, and with population density, IRR = 0.23, 95% CI
[0.11, 0.49], *p* < .001, while reservoir occurrence remained null, IRR = 1.02,
95% CI [0.56, 1.85], *p* = .944 (Table 3). The instability of the poverty
coefficient across specifications (positive when conditioned on rainfall,
negative when conditioned on dry-season moisture) further indicates that it
carries no risk signal independent of the gradient.

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

## Bayesian spatial (BYM) model

Because the spatial-econometric diagnostics above test only for residual
*linear-Gaussian* dependence, we additionally fitted the disease-mapping
standard: a Bayesian hierarchical negative binomial model with a
log-population offset, the two separable fixed effects (rainfall seasonality
and log population density), and two area random effects—a spatially
structured intrinsic conditional autoregressive (ICAR) term on the queen
adjacency graph and an unstructured independent term (Besag–York–Mollié
specification). The model was estimated by Hamiltonian Monte Carlo (4 chains,
1,500 post-warmup draws each; maximum $\hat{R}$ = 1.01).

The fixed-effect gradients were retained, with high posterior probability of a
protective direction: incidence decreased with rainfall seasonality (IRR =
0.45, 95% credible interval [0.18, 1.06]; posterior *P*(IRR < 1) = .97) and
with population density (IRR = 0.56, 95% CrI [0.28, 1.11]; *P*(IRR < 1) = .95).
The structured random effect accounted for an estimated **22% of the residual
area-level variance** (spatial fraction *φ* = 0.22, 95% CrI [0.00, 0.85]); the
wide interval, spanning zero, indicates that the spatial and unstructured
components cannot be reliably separated with only 37 areas. Consistent with
this, leave-one-out cross-validation did not favor the spatial model over an
otherwise identical non-spatial model (ΔELPD = −1.0, *SE* = 0.8). Nonetheless,
the smoothed residual spatial relative-risk surface (Figure 4) localized a
coherent central–eastern high-risk belt that persisted after adjustment for
climate and density—Edo (RR = 3.98), Bauchi (3.74), Ebonyi (2.96), Taraba
(2.68), Plateau (2.61), and Ondo (2.50)—with the lowest residual risk in the
south-west (Osun, Ogun, Kwara). The spatial regression is therefore estimable
and informative for hypothesis generation, but a definitive spatial signal is
not identifiable at state resolution and would require local-government-area
(n = 774) data.

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
| Annual mean temperature (°C) | 26.50 | 0.72 | 26.40 | 24.70 | 28.20 |
| Annual precipitation (mm) | 1,434.10 | 656.60 | 1,326.70 | 488.40 | 3,114.80 |
| Precipitation seasonality (CV) | 92.50 | 27.30 | 82.60 | 63.10 | 148.30 |
| Temperature seasonality (SD ×100) | 173.70 | 72.30 | 151.50 | 88.80 | 320.90 |

*Note.* Burden figures are cumulative over epidemiological week 6 of 2020 to
week 34 of 2026 (Nigeria Centre for Disease Control weekly situation reports).
Population and density from WorldPop bottom-up estimates (v2.0); poverty from
the Oxford Poverty and Human Development Initiative subnational
Multidimensional Poverty Index (MICS 2021); health facilities from the
Humanitarian Data Exchange national registry; reservoir occurrences from the
Global Biodiversity Information Facility; climate from WorldClim 2.1
(1970–2000 normals, 5-arc-minute zonal means). The case-fatality rate row
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

## Table 3

*Parsimonious Low-Collinearity Negative Binomial Model of State Lassa Fever
Incidence (N = 37)*

| Predictor (per 1 *SD*) | IRR | 95% CI | *p* |
|---|---:|---|---:|
| Precipitation seasonality (CV) | 0.31 | [0.17, 0.57] | < .001 |
| Population density (log) | 0.23 | [0.11, 0.49] | < .001 |
| *M. natalensis* occurrences | 1.02 | [0.56, 1.85] | .944 |

*Note.* IRR = incidence-rate ratio per one standard-deviation increase;
exposure = population; dispersion estimated (*α* = 2.82). Rainfall seasonality
is retained as a single, mechanistic proxy for the collinear north–south
gradient (latitude, rainfall, temperature seasonality, and poverty; PCA first
component = 91.3% of variance). All variance inflation factors < 1.4.

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

**Figure 4.** *Smoothed Residual Spatial Relative Risk From the Bayesian Besag–York–Mollié Model.* Posterior mean of the structured spatial random effect, exp(*u*), after adjustment for rainfall seasonality and population density. Values above 1 (red) indicate residual excess risk; a coherent central–eastern belt persists, with the lowest residual risk in the south-west. Spatial fraction *φ* = 0.22, 95% CrI [0.00, 0.85].
