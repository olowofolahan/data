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
| MAP modelled PfPR raster (calibration target) | ✅ fetched (per-state, 95% CrI) |
| Interannual monthly climate (WorldClim CRU-TS) | ✅ fetched (2010–2024, 1080 state-months) |
| **Monthly case data (DHIS2/NMEP)** | ⛔ access-gated — letter drafted (`docs/NMEP_data_request_letter.md`) |
| Mechanistic model (climate-forced SEIR–SEI) | ✅ calibrated to MAP PfPR |
| Mechanistic interannual hindcast | ✅ 2010–2024 monthly prevalence |
| ML forecasting + mechanistic-vs-ML comparison | ✅ rolling-origin CV, h=1–6 |

## Key results

**Calibration (A).** Climate-forced model calibrated per state to MAP PfPR; all
six states match within the MAP 95% credible interval. Fitted transmission
intensity separates *climate suitability* from *residual transmission* — Lagos
calibrates far lower (urban), and Ekiti needs higher intensity than Oyo for
similar prevalence. See `outputs/calibration.png`.

**Forecasting (B).** Rolling-origin CV, horizons 1–6 months (target = the
climate-forced mechanistic hindcast, pending DHIS2 cases):
- Gradient boosting is best short-term (**52%** RMSE reduction vs seasonal-naive
  at 1 month), declining with horizon.
- Mechanistic-climatology is horizon-stable (**~22–24%**) and **overtakes ML by
  month 5–6** — the ML-for-nowcasting / mechanistic-for-long-range trade-off.
- SARIMAX is competitive at 1 month but falls below naive for multi-step.

See `outputs/forecast_comparison.png`. Caveats: the target is model-generated
until DHIS2 cases arrive; climate is assumed known over the horizon. The pipeline
swaps to real cases unchanged.

## Key data finding

Openly-published malaria **outcome** data for Nigeria is **annual**
(WHO national; MAP state-level raster). True **monthly case** counts live in
**DHIS2/NMEP** and are login-gated. Climate covariates, by contrast, are
monthly. The design handles this:

- **Mechanistic model** runs monthly, forced by real climate, validated against
  MAP **annual** state prevalence (seasonality stays mechanistic).
- **ML** forecasts the monthly series now (on the mechanistic hindcast) and
  switches to monthly case targets the moment a DHIS2 export lands in
  `data/raw/cases/monthly_cases.csv` (schema in `docs/DATA_ACCESS.md`).

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
