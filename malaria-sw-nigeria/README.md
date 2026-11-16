# Malaria modelling in South-West Nigeria

Transmission-dynamics **and** statistical/ML forecasting of malaria across the
six South-West zone states: **Lagos, Oyo, Ogun, Osun, Ondo, Ekiti**.
Intended output: an academic paper comparing a climate-forced mechanistic model
with ML forecasting (and a hybrid).

## Status

| Component | State |
|---|---|
| Project scaffold | ✅ done |
| State boundaries (GADM admin-1) | ✅ 6/6 states |
| WHO GHO national trend | ✅ fetched (2000–2024) |
| MAP survey points (validation) | ✅ fetched (32 pts in SW; sparse) |
| WorldClim monthly climatology (forcing) | ✅ fetched (6 states × 12 months) |
| MAP modelled PfPR raster (calibration target) | ⏳ to wire (WCS zonal) |
| CHIRPS interannual monthly rainfall | ⏳ optional (host flaky; retry wrapper ready) |
| **Monthly case data (DHIS2/NMEP)** | ⛔ access-gated — see `docs/DATA_ACCESS.md` |
| Mechanistic model (climate-forced SEIR–SEI) | ✅ runnable starter (uncalibrated) |
| ML forecasting | ⏳ skeleton next |
| Calibration (MAP / cases) | ⏳ next |

## Key data finding

Openly-published malaria **outcome** data for Nigeria is **annual**
(WHO national; MAP state-level raster). True **monthly case** counts live in
**DHIS2/NMEP** and are login-gated. Climate covariates, by contrast, are
monthly. The design handles this:

- **Mechanistic model** runs monthly, forced by real climate, validated against
  MAP **annual** state prevalence (seasonality stays mechanistic).
- **ML** works as an interannual state panel now, and switches to monthly case
  targets the moment a DHIS2 export lands in `data/raw/cases/monthly_cases.csv`
  (schema in `docs/DATA_ACCESS.md`).

## Layout

```
config/states.yaml          study config (states, period, sources)
data/raw/{who,map,climate,boundaries,cases}   raw downloads
data/processed/             analysis-ready tables
src/fetch_who.py            WHO GHO national series
src/fetch_map_surveys.py    MAP Pf survey points -> clip to SW
src/fetch_climate.py        WorldClim climatology (+ CHIRPS interannual helper)
models/mechanistic/climate_seir.py   climate-forced SEIR–SEI starter
models/ml/                  forecasting (next)
docs/DATA_ACCESS.md         how to obtain monthly case data
```

## Quickstart

```bash
pip install -r requirements.txt
python3 -I src/fetch_who.py
python3 -I src/fetch_map_surveys.py
python3 -I src/fetch_climate.py --res 2.5m
python3 -I models/mechanistic/climate_seir.py --state Oyo
```

## Data sources & licences

- WHO Global Health Observatory — `ghoapi.azureedge.net`
- Malaria Atlas Project (CC BY) — `data.malariaatlas.org`
- WorldClim 2.1 (CC BY) — `geodata.ucdavis.edu`
- CHIRPS/CHIRTS — `data.chc.ucsb.edu`
- GADM v4.1 boundaries — `geodata.ucdavis.edu`
- Monthly cases: Nigeria DHIS2 / NMEP (restricted)

_Not medical or operational advice; modelled estimates only._
