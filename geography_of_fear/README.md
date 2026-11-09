# Geography of Fear — Nigeria, State-Level Secondary Dataset

A starter secondary-data compilation for a **nationwide (state-level) study of the geography of fear** in Nigeria. The "geography of fear" tradition (Valentine, Pain, Koskela) studies how fear of crime/violence shapes perception of space and everyday behaviour. A national study of it rests on overlaying **three layers**:

1. **Objective violence/risk** — where harm actually happens
2. **Perceived fear** — where people *feel* unsafe
3. **Vulnerability/context** — poverty, population

The analytical payoff is in the **mismatch** between layers 1 and 2.

## What's in here

`nigeria_state_fear_dataset.csv` — 37 rows (36 states + FCT), analysis-ready. See `DATA_DICTIONARY.md` for every column.

### Layers successfully pulled (real data, all 37 states)
| Layer | Variable(s) | Source | Status |
|---|---|---|---|
| Population | 2023 projection, 2006 census | NBS Demographic Bulletin / NPC | ✅ complete |
| Political violence | events + fatalities (2024, 2025, 2020–2025) + per-capita | **ACLED** via HDX | ✅ complete |
| Violence against civilians | events + fatalities 2020–2025 + per-capita | **ACLED** (civilian targeting) via HDX | ✅ complete |
| Poverty / vulnerability | MPI, headcount, intensity, vulnerable, severe | **OPHI MPI (MICS 2021)** via HDX | ✅ complete |

### Layer still to source (the perception layer — the heart of a *fear* study)
| Layer | Variable | Source | Why blocked |
|---|---|---|---|
| Perceived fear | `afro_feel_unsafe_pct` (felt unsafe walking in neighbourhood) | **Afrobarometer** Round 9 (2022) / Round 10 (2024) Nigeria microdata | `afrobarometer.org` is not on this environment's network allowlist, so the PDFs/microdata couldn't be fetched automatically. National R9 figure = **61%** (up from 33% in 2017). |

## How the data was built (reproducible)
All pulls used the HDX API (`data.humdata.org`), which is allowlisted here.
- ACLED: dataset `nigeria-acled-conflict-data` → monthly admin1 panels (`political_violence...`, `civilian_targeting...`), aggregated by state/year.
- MPI: dataset `nigeria-mpi` (OPHI) → `nga_mpi.csv`, state-level.
- Population: Wikipedia *List of Nigerian states by population* (cites NBS Demographic Statistics Bulletin 2020).

## Headline findings (from this data)
- National political-violence fatalities **2020–2025 ≈ 65,000**; 2025 alone ≈ 15,800.
- Highest absolute deaths: **Borno, Zamfara, Katsina, Niger, Kaduna**.
- Highest **per-capita** death rate 2020–2025: **Borno (270/100k)**, then **Zamfara (155/100k)** — danger is concentrated in the North-East and North-West.
- Poverty tracks the same geography: headcount >70% in Zamfara, Sokoto, Bauchi; <10% in Anambra, Abia, FCT.

## Still to source / next steps
1. **Perception (priority).** Get Afrobarometer R9/R10 Nigeria state or zone breakdowns for "felt unsafe walking" + "feared crime in home" + "fear of political violence". Either (a) allow `afrobarometer.org` on the environment network, or (b) download the Round 9/10 Nigeria dataset manually and drop it in `geography_of_fear/raw/` — I can then compute state means and fill `afro_feel_unsafe_pct`.
2. **NBS National MPI 2022** (optional) — if you want the *national* poverty measure (Ondo 27% … Sokoto 91%) instead of OPHI global MPI, provide the NBS PDF/CSV or allow `nigerianstat.gov.ng`.
3. **Gendered fear** — NDHS GBV module (`dhsprogram.com` is allowlisted) can add a women's-safety / GBV-prevalence column by state.
4. **Boundaries for mapping** — HDX `cod-ab-nga` (state shapefiles) to turn this table into choropleth fear maps.

## Attribution
ACLED data © ACLED (acleddata.com), used under its Terms of Use; only state-level aggregates are stored here. MPI © OPHI, University of Oxford. Population © NBS / NPC.
