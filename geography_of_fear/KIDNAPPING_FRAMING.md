# Kidnapping-framed geography of fear — Nigeria (state level)

File: `nigeria_state_kidnapping_fear_dataset.csv` (37 states, sorted by civilian-targeting death rate).
Built 2026-11-09. This reframes the study around **kidnapping / abduction** as the fear object.

## Why kidnapping is a strong "geography of fear" frame
Kidnapping fear is **spatially diffuse**: it travels along highways and affects people far
from where abductions actually occur (travellers avoid roads, schools close, farmers abandon
fields). So *perceived* fear decouples from *actual* incidence — which is exactly the
tension the geography-of-fear tradition exists to study.

## What's in the dataset (by layer)

### Objective — kidnapping-adjacent (state level, real data)
- `civtarget_events_2020_2025`, `civtarget_fatalities_2020_2025`, `civtarget_fat_per100k_2020_2025`
  — ACLED **"civilian targeting"** events/deaths (2020–2025), via HDX. This category **includes
  abductions** and is the best *fully state-resolved* proxy reachable here for bandit/kidnap
  victimisation. **Top per-capita: Zamfara, Plateau, Borno, Benue, Kaduna.**
- `nw_kidnap_fatalities_2024` — NigeriaWatch 2024 kidnapping-related **deaths**. Only the 5
  states NigeriaWatch names in text are filled: **Kaduna 86, FCT 43, Delta 41, Taraba 33,
  Rivers 23** (national kidnap deaths fell 536→425). Blank = not published (chart not machine-readable).

### Perception — the fear layer (regional, from Afrobarometer R9/2022)
- `afro_unsafe_walk_pct_region` — % who felt unsafe walking in their neighbourhood in the past
  year: **North 65% / South 56%** (national 61%, up from 33% in 2017). Afrobarometer is
  representative at North/South level, **not** by state, so every state carries its regional value.
- `afro_kidnap_serious_pct_nat` = **84%** consider abductions/kidnappings a serious problem
  (65% "very serious"). `afro_kidnap_rising_pct_nat` = **74%** say kidnappings have increased.
  These are national figures (no published sub-national split).

### Context (state level)
- `mpi_headcount_pct`, `pct_severe_poverty` — OPHI MPI (MICS 2021).
- `pv_fat_*` — ACLED all political-violence deaths (insecurity backdrop).
- `pop_2023_proj`, `pop_2006_census` — NBS / NPC.

## National kidnapping reference points (from sources, for your lit review)
- **4,243** people abducted in 2023 (Nigeria Security Tracker / ACLED, via TheCable).
- **15,398** abducted since 2019 (SBM Intelligence).
- Hotspot states repeatedly named: **Zamfara, Katsina, Niger, Kaduna** (North-West + North-Central).
- Afrobarometer: theft, robbery, **kidnapping** = the three most-cited neighbourhood threats.

## The one real gap: clean state-level kidnapping *incidence*
A complete 37-state count of **abduction incidents / victims** is not reachable in this
environment:
- **ACLED abduction sub-event** (`Abduction/forced disappearance`) — the authoritative source —
  requires the ACLED API, which is **auth-gated and unreachable through this session's proxy**
  (`api.acleddata.com` returns 502/000 even though it's allowlisted).
- **NBS crime statistics** — `nigerianstat.gov.ng` resets the proxy connection (blocks automated traffic).
- **SBM Intelligence** (`sbmintel.com`) — returns 403 to the proxy.
- Media trackers (Dataphyte, BusinessDay, TheCable) give partial, differently-dated state figures
  (e.g. an undated BusinessDay list: Zamfara 132 incidents/1,639 victims; Katsina 119/887;
  Niger 48/689) — usable for triangulation, not as a clean panel.

### To close it, easiest first
1. **ACLED export (recommended):** register a free ACLED account → Data Export Tool → filter
   Country=Nigeria, Event/sub-event = Abduction/forced disappearance, 2019–2025 → download CSV →
   drop in `geography_of_fear/raw/`. I'll aggregate it to a real `kidnap_incidents_by_state` column.
   (Or give me an ACLED API key via the secure prompt and I'll retry the API.)
2. **Afrobarometer microdata:** download the Round 9 (2022) / Round 10 (2024) Nigeria SPSS/CSV
   from afrobarometer.org → drop in `raw/`. I'll compute **6-zone** (and approximate state) fear
   percentages to replace the coarse North/South column.

## Attribution
ACLED © ACLED (acleddata.com), state-level aggregates only. Afrobarometer © Afrobarometer
(Round 9 Nigeria, 2022). NigeriaWatch © Nigeria Watch Project. MPI © OPHI. Population © NBS/NPC.
