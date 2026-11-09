# Forecasting 2026 state-level armed conflict

A one-step-ahead forecast of full-year 2026 political-violence fatalities for all 37 states, with
prediction intervals and an early validation against the 10 months (Jan–Oct 2026) already recorded
in ACLED. Outputs: `outputs/forecast_2026.csv`, `outputs/map9_forecast2026.png`,
`outputs/fig_forecast2026_validation.png`.

## Method
A pooled one-step-ahead model was trained on all state-year transitions 2015→2025:
log(1+fatalities)&#8339; = β&#8320; + β&#8321;·log(1+fatalities)&#8339;&#8331;&#8321; + β&#8322;·W·log(1+fatalities)&#8339;&#8331;&#8321; + ε,
i.e. a state's violence as a function of its **own prior-year level** and its **neighbours' prior-year
level** (row-standardised queen weights) — the persistence + diffusion engine validated earlier
(LOOCV R² = .78 for 2025). Estimates: β₁ = 0.75 (persistence), β₂ = 0.04 (spillover), in-sample
R² = .63. Full-year 2026 was forecast from 2025 values. Point forecasts use **Duan's smearing
estimator** (unbiased means, correcting log-retransformation bias); 80%/95% prediction intervals use
**empirical residual quantiles**.

## Results
**National.** Forecast 2026 total ≈ **15,400 deaths**, essentially flat on 2025 (15,771). This is
corroborated by the actual-so-far: Jan–Oct 2026 recorded 13,348 deaths, which annualises to ≈ 16,000.

**State forecasts (top 10, deaths; 80% PI).**
| State | 2025 | Forecast 2026 | 80% PI |
|---|---|---|---|
| Borno | 3,864 | 2,608 | [483, 4,918] |
| Zamfara | 2,747 | 2,204 | [408, 4,158] |
| Katsina | 1,862 | 1,567 | [290, 2,956] |
| Niger | 1,526 | 1,369 | [253, 2,582] |
| Sokoto | 914 | 970 | [179, 1,830] |
| Benue | 879 | 854 | [158, 1,611] |
| Plateau | 663 | 703 | [130, 1,327] |
| Kwara | 489 | 540 | [99, 1,020] |
| Kebbi | 328 | 457 | [84, 863] |
| Kaduna | 322 | 424 | [78, 801] |

The forecast keeps the epicentre in the **North-West/North-Central belt**, with **Kebbi (+39%) and
Kaduna (+32%)** projected to rise — the continuing diffusion front.

**Validation against Jan–Oct 2026 (annualised).** The forecast tracks the realised data closely:
**Pearson (log) r = .90, Spearman ρ = .86**, and **84%** of states' annualised actuals fall within the
80% prediction interval — good calibration for a parsimonious model.

## Caveats (important)
- **Mean-reversion under-predicts actively escalating states.** Borno's annualised 2026 (≈ 4,950) is
  already above its forecast (2,608): an AR model pulls extreme values toward the recent mean, so it
  lags a state that is still accelerating. Treat top-state point forecasts as conservative.
- **Shocks are unforecastable.** As the 2025 residuals showed (Kwara), the model cannot anticipate new
  armed-actor entry, major operations, or truces — only the continuation of current dynamics.
- **Wide intervals.** σ(log) ≈ 1.03 implies ~5× multiplicative uncertainty; the point forecast is a
  central tendency, not a precise count.
- **Annualisation assumes no strong seasonality** (Jan–Oct × 12/10); Nigerian violence has modest
  seasonal structure (dry-season banditry), so the annualised actual is itself approximate.
- 2026 ACLED data are preliminary and subject to revision.

## Bottom line
2026 is forecast to remain at 2025's elevated level (~15–16k deaths), concentrated in the
North-West/North-Central, with the diffusion front (Kebbi, Kaduna) still advancing — and the realised
first ten months confirm this trajectory (r = .90).

Source: ACLED via HDX (data to 30 Oct 2026); boundaries OCHA/HDX; population NBS/NPC.
