# Geography of Armed Conflict in Nigeria — state level

A complete (no-gap) state-level secondary dataset and spatial analysis of political violence in
Nigeria, built from ACLED (via HDX), 1997–2026, all 37 states.

## Files
- `Nigeria_Geography_of_Armed_Conflict_Report.pdf` — 5-page results report (maps embedded).
- `nigeria_state_armed_conflict_dataset.csv` — the state dataset (events, fatalities, rates,
  lethality, civilian-targeting share, escalation ratio, conflict character) for multiple time windows.
- `national_zonal_timeseries.csv` — annual political-violence fatalities by zone (for trends).
- `RESULTS.md` — written findings.
- `outputs/` — 6 maps + zonal time-series figure + `state_conflict_indices.csv`.

## Headline findings
- **2025 was the deadliest year on record** (15,771 political-violence deaths nationally).
- The **conflict epicentre has shifted North-East → North-West/North-Central** (banditry) since 2021;
  Borno is the only major theatre in decline.
- Conflict is **significantly spatially clustered** (Moran's I = 0.187, p = 0.033) — a contiguous
  North-West/North-Central hot belt (Kaduna, Katsina, Kebbi, Niger, Nasarawa) vs a cold southern bloc.
- 18 states are civilian-targeting-dominant; 15 battle-dominant; 4 low-intensity.

## Reproduce
Built with the scripts in the session scratchpad (ACLED HDX pulls → pandas aggregation →
geopandas/matplotlib/scipy analysis → reportlab report). Data: ACLED © ACLED (Terms of Use);
boundaries OCHA/HDX cod-ab-nga; population NBS/NPC.
