# Results — The Geography of Armed Conflict in Nigeria (state level)

Built 2026-11-09 from ACLED (via HDX), 1997–2026 monthly, all 37 states. **No data gaps** —
every variable is objective and state-complete. Figures in `outputs/`; indices in
`outputs/state_conflict_indices.csv`; dataset `nigeria_state_armed_conflict_dataset.csv`.

## 1. A record, and a moving epicentre
- National political-violence deaths reached **15,771 in 2025** — the deadliest year in the series,
  surpassing the 2014–15 Boko Haram peak (~11,000/yr).
- The **epicentre has migrated North-East → North-West/North-Central**:

| Zone | 2015 deaths | 2025 deaths | Direction |
|---|---|---|---|
| North East | 9,199 | 4,467 | ↓ falling (Boko Haram past peak) |
| North West | 745 | 6,297 | ↑ 8.5× (banditry surge) |
| North Central | 901 | 3,865 | ↑ 4.3× |
| South East | 41 | 517 | ↑ 13× (IPOB/ESN unrest) |
| South South | 155 | 366 | ↑ |
| South West | 34 | 259 | ↑ |

→ `fig_zonal_timeseries.png`

## 2. Intensity (2020–2025, per 100,000)
Highest death rates: **Borno 270, Zamfara 155, Niger 82, Katsina 61, Kaduna 59, Benue 48, Plateau 47, Sokoto 41.** → `map1_fatality_rate.png`, `map2_event_density.png`

## 3. Character of the violence
Of the 37 states: **18 civilian-targeting-dominant** (≥45% of deaths are violence against
civilians — e.g. Plateau 78%, Benue 71%, Sokoto 60%), **15 battle/armed-clash-dominant**
(Borno, Zamfara, Niger), **4 low-intensity.** → `map3_civilian_share.png`, `map5_character.png`

## 4. Escalation 2014–19 → 2020–25 (fatality ratio)
Fastest-escalating states: **Kebbi 24×, Niger 21×, Kwara 16×, Sokoto 12×, Imo 10×, Oyo 9×,
Katsina 9×.** The North-West/North-Central banditry corridor and the South-East are the growth
fronts; Borno is the only major theatre *declining* (0.78×). → `map4_escalation.png`

## 5. Spatial clustering (the geographic argument)
**Global Moran's I = 0.187, p = 0.033** (queen contiguity, log fatality rate, 999 permutations):
conflict is **significantly spatially clustered**, not randomly scattered — it forms contiguous
belts, so a state's risk depends on its neighbours'.
- **High–High hot cluster:** Kaduna, Katsina, Kebbi, Niger, Nasarawa (+Ebonyi) — the core
  North-West/North-Central banditry belt.
- **Low–Low cold cluster:** the southern states (Abia, Akwa Ibom, Bayelsa, Edo, Ekiti…).
→ `map6_lisa_clusters.png`

## Method notes
- "Political violence" = ACLED battles + violence against civilians + explosions/remote +
  mob violence (the armed-conflict family). Demonstrations (protests/riots) are held separately.
- Rates use NBS 2023 projected population. 2026 excluded from annual comparisons (partial year).
- LISA uses standardised values; clusters shown descriptively (sign of local Moran), global
  significance from permutation. For publication, add FDR-adjusted local p-values (esda).

## Sources
ACLED © Armed Conflict Location & Event Data Project (state aggregates only, per Terms of Use),
via HDX dataset *Nigeria – Conflict Events*. Boundaries: OCHA/HDX cod-ab-nga. Population: NBS/NPC.
