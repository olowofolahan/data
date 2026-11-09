# Results — Geography of (Kidnapping) Fear in Nigeria, state level

Analyses run on `nigeria_state_kidnapping_fear_dataset.csv` (37 states). Figures in `outputs/`.
State-level indices in `outputs/state_indices.csv`. All figures reproducible via the analysis script.

> **Scope reminder.** Objective risk and poverty are measured at **state** level. Perceived fear
> (Afrobarometer R9, 2022) is only representative at **North/South** level, so every state carries
> its regional fear value. State-level perception and true kidnapping victim counts still require
> the Afrobarometer microdata and an ACLED abduction export respectively.

## 2. Violence–poverty relationship (bivariate OLS, n = 37)
| Outcome (per 100k, 2020–2025) | slope | r | r² | p |
|---|---|---|---|---|
| All political-violence deaths vs poverty | 0.75 | **+0.37** | 0.14 | 0.025 |
| Civilian-targeting (abduction-inclusive) deaths vs poverty | 0.21 | **+0.42** | 0.17 | 0.010 |

Poverty is a **significant but modest** predictor of lethal violence: poorer states are more
violent, but poverty explains only ~14–17% of the variance. Violence is **uncorrelated with
population size** (r = +0.02) — insecurity is not a big-state artefact. → `fig_regression_poverty_violence.png`

## 3. Maps (choropleths, `outputs/`)
- `map1_civtarget_rate.png` — objective kidnapping-proxy death rate (civilian targeting).
- `map2_allviolence_rate.png` — all political-violence death rate.
- `map3_poverty.png` — multidimensional poverty headcount.
- `map4_composite_index.png` — composite Insecurity–Vulnerability Index.
- `map5_mismatch.png` — fear–risk mismatch (diverging).
- `map6_perceived_fear_region.png` — perceived fear (North/South).

All show the same **North–South fault line**: a high-insecurity, high-poverty northern band
(North-West + North-East + parts of North-Central) against a low-risk southern belt.

## 4. Composite Insecurity–Vulnerability Index (IVI) + typology
IVI = rescaled( 0.6·risk_z + 0.4·poverty_z ) → 0–100, where risk_z averages the standardised
civilian-targeting and all-violence death rates.

**Top 8:** Zamfara (100), Borno (99.8), Sokoto (58.5), Katsina (57.9), Plateau (54.4),
Niger (51.0), Kaduna (48.3), Benue (45.0) — every one in the North.

**Typology (risk × poverty, split at national medians):**
| Type | n | Examples |
|---|---|---|
| High-risk / High-poverty | 14 | Zamfara, Borno, Sokoto, Katsina, Niger |
| Lower-risk / Lower-poverty | 13 | Lagos, Osun, Ekiti, Anambra |
| High-risk / Lower-poverty | 5 | (states violent despite less poverty) |
| Lower-risk / High-poverty | 5 | (poor but relatively peaceful) |

The **High-risk/Lower-poverty** and **Lower-risk/High-poverty** cells are the analytically
interesting ones — they break the simple "poverty = violence" story.

## 5. Fear–risk mismatch (the geography-of-fear payoff)
mismatch = regional fear (z) − state objective risk (z). Positive = **fear exceeds local risk**
(fear paradox); negative = **risk exceeds fear** (normalised danger).

- **Fear exceeds risk:** Kano, Gombe, Jigawa, Bauchi, FCT — northern states with *relatively low*
  local violence that nonetheless sit inside the high-fear (65%) northern region. Regional dread
  outruns their own incident rates.
- **Risk exceeds fear:** Borno (−2.47), Zamfara (−1.99) — extreme violence that even high northern
  fear under-registers (danger normalised); and southern states (Ebonyi, Imo, Anambra) where
  rising violence outpaces still-moderate southern fear.

At the **regional** level the cleaner headline: the North's death rate is **6× the South's**, but
its fear is only **1.16× higher** — the **South fears disproportionately to its objective risk**,
consistent with kidnapping dread travelling via roads and media rather than local body counts.

> **Caveat on the mismatch metric.** Because fear is constant within each region, the state-level
> mismatch mostly re-expresses *within-region* risk variation. It is a valid illustration of the
> fear-paradox logic, but a genuine state-level fear–risk gap needs the Afrobarometer microdata
> (6-zone / state fear estimates). Treat map 5 as indicative, the regional comparison as robust.

## What would sharpen every result
1. **ACLED abduction export** → replace the civilian-targeting proxy with true kidnapping counts,
   re-estimate the regression and rebuild the index on kidnapping specifically.
2. **Afrobarometer R9/R10 microdata** → state/zone fear, turning map 5 into a real state-level
   fear–risk gap and enabling a proper perceived-vs-actual regression.
