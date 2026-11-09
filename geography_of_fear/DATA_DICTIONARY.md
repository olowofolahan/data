# Data Dictionary — `nigeria_state_fear_dataset.csv`

Unit of analysis: **Nigerian state** (36 states + FCT = 37 rows). Keyed on `state`.
Built: 2026-11-09. One row per state; sorted by `pv_fat_2020_2025` (most conflict deaths first).

| Column | Meaning | Source | Notes |
|---|---|---|---|
| `state` | State name | — | FCT = Federal Capital Territory (Abuja) |
| `zone` | Geopolitical zone (6 zones; FCT grouped in North Central) | Standard NG classification | Strongest analytical grouping for insecurity patterns |
| `pop_2023_proj` | Projected population, 2023 | NBS *Demographic Statistics Bulletin 2020* (via Wikipedia) | Projection, **not** a census; Nigeria has no post-2006 census |
| `pop_2006_census` | 2006 census population | National Population Commission | Last official census; disputed but authoritative |
| `pv_ev_2024` / `pv_fat_2024` | Political-violence **events** / **fatalities**, 2024 | ACLED (via HDX) | "Political violence" = battles, violence against civilians, explosions/remote, mob violence, riots |
| `pv_ev_2025` / `pv_fat_2025` | Political-violence events / fatalities, 2025 | ACLED | 2025 near-complete |
| `pv_ev_2020_2025` / `pv_fat_2020_2025` | Cumulative events / fatalities, 2020–2025 | ACLED | 6-year window; most robust ranking variable |
| `pv_fat_per100k_2025` | 2025 fatalities per 100,000 (on 2023 pop) | derived | Per-capita = "intensity of danger" (how NigeriaWatch ranks) |
| `pv_fat_per100k_2020_2025` | 2020–2025 fatalities per 100,000 | derived | Use this for a per-capita fear/risk map |
| `ct_ev_2020_2025` / `ct_fat_2020_2025` | **Civilian-targeting** events / fatalities, 2020–2025 | ACLED "civilian targeting" filter | *Violence against civilians* — the single most fear-relevant subset |
| `ct_fat_per100k_2020_2025` | Civilian-targeting fatalities per 100,000 | derived | Best objective proxy for "everyday fear of being harmed" |
| `mpi_ophi` | Multidimensional Poverty Index value (0–1) | OPHI Global MPI, **MICS 2021** (via HDX) | OPHI global methodology; **differs from** NBS National MPI 2022 |
| `mpi_headcount_pct` | % of people who are multidimensionally poor | OPHI / MICS 2021 | The headline poverty incidence |
| `mpi_intensity_pct` | Average deprivation share among the poor | OPHI / MICS 2021 | |
| `pct_vulnerable_poverty` | % vulnerable to multidimensional poverty | OPHI / MICS 2021 | |
| `pct_severe_poverty` | % in severe multidimensional poverty | OPHI / MICS 2021 | |
| `afro_feel_unsafe_pct` | % who felt unsafe walking in their neighbourhood (past year) | Afrobarometer R9/R10 | **EMPTY — not yet sourced** (see README); national R9 = 61% |

## Source notes & caveats
- **ACLED** data © Armed Conflict Location & Event Data Project, used under its Terms of Use / Attribution Policy. This file contains **state-level aggregates only** (not raw events) and must be cited as: *ACLED (acleddata.com), accessed via HDX, Nov 2026.*
- **OPHI MPI** here is the *global* MPI built on **MICS 2021**. It is methodologically different from the **NBS National MPI 2022** (which reported incidence from 27% in Ondo to 91% in Sokoto using Nigeria-specific dimensions incl. security/shocks). If your study needs the *national* MPI, swap this column — see README "Still to source".
- **Population** figures are projections; prefer per-capita rates for comparison but report raw counts too.
- `pv_` uses ACLED's **political violence** family; `ct_` is the **civilian targeting** subset of it (not additive — ct is a subset reported separately here).
