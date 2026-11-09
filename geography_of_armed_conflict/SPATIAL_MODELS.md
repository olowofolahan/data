# Which spatial regression model? — options, diagnostics, recommendation

Conflict data are spatially dependent (raw outcome Moran's I = 0.19, p = 0.03; LISA hot cluster in
the NW/NC), so OLS is mis-specified: its SEs are biased and it ignores spillover. Below are the
candidate spatial models, the formal test that chooses among them, the results on this data
(n = 37 states, outcome = log political-violence death rate 2020–25), and the recommendation.
Full output: `outputs/spatial_regression_output.txt`.

## Candidate models
| Model | Equation | When it's right |
|---|---|---|
| **OLS** | y = Xβ + ε | no spatial dependence left after X |
| **SLX** (spatial lag of X) | y = Xβ + WXθ + ε | neighbours' *covariates* matter; OLS-estimable |
| **SAR / Spatial Lag** | y = **ρWy** + Xβ + ε | **contagion/diffusion** in the outcome itself |
| **SEM / Spatial Error** | y = Xβ + u, u = **λWu** + ε | spatial dependence is a *nuisance* from omitted spatially-correlated variables |
| **SDM / Spatial Durbin** | y = ρWy + Xβ + WXθ + ε | general case; nests SAR & SLX; gives direct/indirect effects |
| **SARAR/SAC** | ρWy + Xβ + λWu + ε | lag *and* error dependence |
| **GWR** | local β(s) | coefficients vary over space (needs larger n) |

## The decision rule (Anselin LM tests) — run on this data
| Test (on OLS residuals) | value | p | verdict |
|---|---|---|---|
| Moran's I (error) | 1.66 | 0.097 | weak |
| LM-lag / Robust LM-lag | 0.20 / 0.41 | 0.65 / 0.52 | **ns** |
| LM-error / Robust LM-error | 0.60 / 0.80 | 0.44 / 0.37 | **ns** |
| LM-WX (Durbin) / Joint SDM | 3.73 / 4.32 | 0.59 / 0.63 | **ns** |

**AIC comparison:** OLS 119.9 · SEM 119.0 · SAR 121.7. SAR ρ = +0.12 (p = 0.57), SEM λ = +0.26
(both **non-significant**).

### What this means
Once the **spatially-patterned covariates** (temperature, population density, border exposure — all
North–South gradients) are in the model, they **absorb the spatial autocorrelation**: no significant
residual spatial dependence remains, and the spatial parameters (ρ, λ) are not significant. So for
the *cross-sectional determinants* question, **OLS is defensible; a Spatial Error Model (SEM) is the
marginally-preferred spatial form by AIC** — report it as a robustness check, not a headline.

## Recommendation
1. **Cross-sectional determinants (what you have now):** report **OLS with spatial diagnostics**, plus
   a **SEM** robustness check. Note ρ/λ are weak because covariates are collinear with the spatial
   structure and **n = 37 underpowers ML spatial estimation**. Report the SAR **impact decomposition**
   (direct/indirect/total) so spillover is visible even if ρ is imprecise.
2. **The scientifically correct model, given your contagion finding + panel data:** a
   **dynamic Spatial Durbin panel** —
   y&#8339; = ρ·W·y&#8339; + γ·y&#8339;&#8331;&#8321; + Xβ + WXθ + μ&#8336; + λ&#8336; + ε
   (spatial lag **and** a temporal lag, with state and year fixed effects). This matches the strong
   result from the prediction model (own history + **neighbours' history**, LOOCV R² 0.59→0.78): the
   spatial signal in Nigerian conflict is primarily **how it diffuses over time**, which a static
   cross-section cannot capture. I have the yearly 1997–2026 panel to estimate it.
3. **Weights:** row-standardised **queen contiguity** used here; test robustness with k-nearest (k=4–6)
   and inverse-distance W, and report Moran's I sensitivity.

## Bottom line
- *Static map of determinants* → **OLS + SEM** (spatial terms weak here — and that's a finding).
- *The diffusion story that the data actually supports* → **dynamic spatial Durbin / spatial-lag panel**
  with a temporal lag. That is the model I'd estimate next.

Tools: `spreg`/`libpysal` (Python). Equivalent in R: `spatialreg` (lagsarlm, errorsarlm, Durbin),
`splm` (spatial panels).
