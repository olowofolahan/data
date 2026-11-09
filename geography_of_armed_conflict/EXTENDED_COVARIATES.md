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
| **Number of police** | ❌ not obtained | Nigeria does not publish police **personnel by state** in clean open form. Proxy options: police-station *counts* (OpenStreetMap — host not yet allowlisted) or the Police Annual Report (manual) |
| **Foreign interest** | ❌ not obtained | No clean state-level measure. Partial proxy = oil-producer (foreign oil majors). Better options need definition: FDI by state, expatriate-targeted incidents, number of foreign firms/consulates |

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

## To complete the two missing variables
1. **Police** — allow an OSM/Overpass host (or HDX facility dataset) → I'll compute police-station
   counts and density per state; or supply the NPF Annual Report figures and I'll merge them.
2. **Foreign interest** — pick a definition (FDI inflow by state, count of foreign-owned firms,
   expatriate-targeted ACLED events, or oil-major concession area) and I'll build it.

Sources: terrain © WorldClim 2.1 (geodata.ucdavis.edu); IGR © NBS 2023; ACLED © ACLED (demos);
religion coding by analyst (no census); boundaries OCHA/HDX; population NBS/NPC.
