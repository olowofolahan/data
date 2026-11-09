# Extended covariates — adding structural predictors to the conflict model

You asked to add: economic resources, terrain ruggedness, dominant religion, number of police,
political crisis, foreign interest. Here is what was obtainable at state level, how it was built,
and what it shows. Data: `outputs/extended_covariates.csv` (merged analysis set:
`outputs/determinants_merged.csv`).

## Availability of the six requested variables
| Requested | Status | How it was operationalised |
|---|---|---|
| **Economic resources** | ✅ full | **NBS IGR 2023 per capita** (Internally Generated Revenue, all 37 states, direct from nigerianstat.gov.ng) + **oil-producer** dummy |
| **Terrain ruggedness** | ✅ full | **Computed from a DEM** (WorldClim 2.5′ elevation): standard deviation of elevation within each state |
| **Dominant religion** | ⚠️ coded | 3-way category (Muslim / Christian / Mixed). **No official census of religion exists** — this is scholarly coding, approximate and contestable (esp. Kaduna, the Middle Belt, the Yoruba South-West coded "Mixed") |
| **Political crisis** | ⚠️ proxy | **ACLED demonstrations** (riots + protests) events 2020–25, as a civil-unrest proxy. A true "political crisis" index (impeachments, states of emergency, election violence) needs manual coding |
| **Number of police** | ⚠️ weak proxy | **OSM police-station counts** (315 nationally, via HOT-OSM) — but OSM completeness varies by state, so this under-measures real presence and is **not reliable**. Personnel figures still need the NPF Annual Report (manual) |
| **Foreign interest** | ⚠️ proxy | **International-border-state** dummy (cross-border exposure to Niger/Chad/Cameroon/Benin — arms/banditry corridors) + oil-producer. A direct FDI/foreign-firm measure still needs sourcing |

## New variables now in the dataset (all 37 states)
`ruggedness` (elevation SD), `elev_mean`, `igr_2023_naira`, `igr_per_capita`, `oil_producer`,
`dominant_religion`, `political_unrest_events_20_25`, `area_sqkm`, `pop_density`.
- Most rugged: Plateau, Taraba, Adamawa, Bauchi (Middle-Belt/highlands); flattest: Bayelsa, Lagos, Rivers (Niger Delta).
- Richest per capita: Lagos ₦51.7k, FCT ₦44.0k, Rivers ₦27.0k; poorest: Kebbi ₦2.0k, Kano ₦2.3k.

## What these covariates explain (determinants of conflict intensity)
Outcome = log(political-violence deaths per 100k, 2020–25). Standardised OLS, n = 37, LOOCV.

**Bivariate correlations:**
| Covariate | r | p |
|---|---|---|
| Population density | **−0.48** | **0.002** |
| Economic resources (log IGR/cap) | −0.30 | 0.075 |
| Poverty (MPI) | +0.28 | 0.090 |
| Oil-producing | −0.21 | 0.202 |
| Muslim-majority | +0.20 | 0.245 |
| Terrain ruggedness | +0.18 | 0.281 |
| Political unrest | −0.20 | 0.228 |

**Multivariate model:** R² = 0.25, **LOOCV R² = −0.14** (no out-of-sample skill). Only
**population density is significant** (β = −0.65, p = 0.03): conflict intensity is higher in
**sparsely-populated, rural** states — the classic periphery/"ungoverned space" pattern. Terrain
ruggedness, religion, oil, economic resources and poverty are **not** significant once density is
accounted for (and some are collinear with the North–South divide — MPI VIF 5.3, Muslim 4.1).

## The headline (and why it matters)
> Static **structural** conditions explain Nigerian conflict intensity **poorly** (R² ≈ 0.25, zero
> out-of-sample skill). The earlier **violence-history + spatial-spillover** model reached
> **LOOCV R² = 0.78**. → Nigerian conflict is driven far more by its **own dynamics (persistence +
> diffusion)** than by terrain, religion, resources or poverty. The one structural factor that
> survives is **rurality (low population density)**.

This directly adjudicates a core debate — *grievance/structural* vs *conflict-trap/diffusion*
theories — in favour of the latter for Nigeria. That is a publishable argument.

## Added (suggested) variables — climate, border, displacement, police
Pulled on request, all 37 states unless noted:
- **Rainfall (annual mm)** and **temperature (°C)** — zonal means from WorldClim 2.1. Sharp
  gradient: 483 mm (Yobe) → 3,131 mm (Bayelsa).
- **International-border-state** dummy (16 states) — cross-border/foreign-exposure proxy.
- **Displacement (IDPs present)** — IOM DTM latest round, 2.38 M IDPs across 19 (conflict) states
  (Borno 1.7 M). This is a **consequence** of conflict, used for validation, not as a predictor.
- **Police stations** — OSM counts (315 total). ⚠️ unreliable (mapping-coverage bias).

### Expanded determinants — what now correlates with conflict intensity
| Covariate | r | p |
|---|---|---|
| Displacement (log IDPs) *[consequence]* | **+0.48** | **0.003** |
| Population density (log) | **−0.48** | **0.002** |
| **International border state** | **+0.37** | **0.026** |
| Temperature (°C) | +0.32 | 0.050 |
| Poverty (MPI) | +0.28 | 0.090 |
| Economic (log IGR/cap) | −0.30 | 0.075 |
| Rainfall (mm) | −0.22 | 0.197 |
| Terrain ruggedness | +0.18 | 0.281 |
| Muslim-majority | +0.20 | 0.245 |
| Police per million (OSM) | −0.04 | 0.832 |

**New structural signal:** conflict concentrates in **rural (low-density), international-border,
hotter** states — the "ungoverned rural periphery / porous frontier" pattern. Border-state exposure
is a meaningful, significant correlate (cross-border banditry/arms). Multivariate structural model
R² = 0.28, **LOOCV R² ≈ 0** — so even with the richer set, **static structure still has no
out-of-sample predictive skill**, reaffirming that conflict dynamics (history + diffusion, LOOCV
R² = 0.78) dominate. Figure: `outputs/fig_determinants_expanded.png`.

## Still open
- **Police personnel** by state (NPF Annual Report — manual; OSM counts are too incomplete to trust).
- **Direct foreign-interest** measure (FDI by state / foreign-firm counts) — border dummy is only a proxy.

Sources: terrain, rainfall, temperature © WorldClim 2.1 (geodata.ucdavis.edu); IGR © NBS 2023;
displacement © IOM DTM (via HDX); police © HOT-OSM; ACLED © ACLED (demos); religion coding by
analyst (no census); boundaries OCHA/HDX; population NBS/NPC.
