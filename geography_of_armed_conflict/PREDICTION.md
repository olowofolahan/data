# Can we predict 2025 conflict from pre-2025 data? — Yes, mostly.

Question: using only information available **before 2025**, how well can we predict each state's
2025 political-violence fatalities? Outcome = log(1 + 2025 fatalities), n = 37 states.
Validation = **exact leave-one-out cross-validation** (PRESS), so R²_LOOCV is genuine
out-of-sample skill, not in-sample fit.

## How predictable? (pre-2025 features only)
| Model | predictors | R² (fit) | **R²_LOOCV** (out-of-sample) |
|---|---|---|---|
| M1 Persistence | 2024 fatalities | 0.65 | 0.59 |
| M2 + spatial spillover | + neighbours' 2024 fatalities | 0.74 | 0.67 |
| **M3 + 3-yr history** | 2022–24 mean + spillover | **0.81** | **0.78** |
| M4 full | + poverty + population + North | 0.84 | 0.77 |

**Findings**
1. **Conflict is highly predictable and highly persistent.** Prior-year violence alone explains
   ~59% of out-of-sample variance; r(2024, 2025) = **0.80**.
2. **Spatial spillover adds real signal** — neighbours' prior violence lifts LOOCV R² from 0.59 → 0.67.
   Diffusion matters: you are more at risk if your neighbours were.
3. **Best model = violence history + spatial spillover (M3, LOOCV R² = 0.78).**
4. **Poverty and population add *nothing* out-of-sample.** M4's fit rises but its LOOCV R² *falls*
   (0.78 → 0.77) — once you know a state's violence history and its neighbours', structural poverty
   is redundant for prediction (it correlated with violence only because both are spatially clustered).

## The "surprises" (where the forecast missed) → early-warning value
Residuals from the full model flag states that broke their own trend:

**Under-predicted (emerging hotspots — more violence than history implied):**
| State | 2024 | 2025 | predicted | note |
|---|---|---|---|---|
| **Kwara** | 22 | **489** | ~66 | banditry spilling from Niger/Kebbi into North-Central — the standout |
| Sokoto | 336 | 914 | ~530 | Lakurawa/bandit expansion |
| Zamfara | 1,429 | 2,747 | ~1,680 | re-escalation |
| Ondo, Abia, Edo | — | — | — | smaller southern upticks |

**Over-predicted (cooled faster than history implied):**
| State | 2024 | 2025 | predicted | note |
|---|---|---|---|---|
| **Kaduna** | 819 | **322** | ~1,355 | sharp decline — operations/displacement? |
| Taraba, Bauchi, FCT | — | — | — | quieter than trend |

→ `fig_pred_vs_actual.png`, `map7_forecast_residuals.png`, `predict2025_table.csv`

## What this means for the study
A **lagged spatial-autoregressive** structure (own history + neighbours' history) is the engine of
Nigerian conflict geography — consistent with the Moran's I clustering result. The residual map is
itself a finding: **Kwara is the state to watch**, a new front where violence outran its past.

## Caveats
- n = 37 is small; LOOCV guards against overfit but confidence intervals are wide.
- Fatalities are skewed; modelled in log space. Big absolute counts still dominate rank.
- "Prediction" here is an explanatory/now-cast exercise, not an operational forecast — a real
  early-warning model would use monthly data and roll the window forward.
- A richer model needs pre-2025 covariates we don't yet have at state level (food prices,
  displacement, security deployments, rainfall) — candidates for the next data pull.

Source: ACLED via HDX (state aggregates); boundaries OCHA/HDX cod-ab-nga; population NBS/NPC.
