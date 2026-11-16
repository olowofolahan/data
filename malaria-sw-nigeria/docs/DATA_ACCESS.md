# Data access guide

This project aims to model malaria in the six South-West Nigeria states
(Lagos, Oyo, Ogun, Osun, Ondo, Ekiti) at **monthly** resolution.

## Status of each source

| Source | What it gives | Resolution | Access | Script |
|---|---|---|---|---|
| WHO GHO | National incidence/mortality/ITN | national, **annual** | open ✅ | `src/fetch_who.py` |
| MAP survey points | Ground-truth PfPR observations | point, survey | open ✅ (sparse: ~32 in SW) | `src/fetch_map_surveys.py` |
| MAP modelled raster | PfPR 2–10 surface | ~5 km, **annual** | open ✅ | `src/fetch_map_raster.py` |
| CHIRPS | Rainfall | ~5 km, **monthly** | open ✅ | `src/fetch_climate.py` |
| CHIRTS | Temperature | ~5 km, **monthly** | open ✅ | `src/fetch_climate.py` |
| **DHIS2 / NMEP** | **Monthly confirmed malaria cases** | facility/LGA/state, **monthly** | **RESTRICTED** ⛔ | manual → `data/raw/cases/` |

## The monthly case-data gap (important)

True monthly seasonal **case** counts are **not openly downloadable** anywhere
(confirmed: not on HDX, WHO GHO, MAP, or DHS). They live in Nigeria's routine
health information system, **DHIS2**, managed by the **National Malaria
Elimination Programme (NMEP)** / Federal Ministry of Health.

### How to obtain the monthly case data

1. **DHIS2 instance.** Nigeria's HMIS runs on DHIS2 (National Health Management
   Information System). Access requires an account issued by the FMoH/NMEP or a
   State Ministry of Health. Routes:
   - A formal data-request letter to **NMEP** (common for academic/thesis use),
     stating states, period, and indicators.
   - Partner access via **WHO**, **PMI/US President's Malaria Initiative**, or
     **Malaria Consortium** if you are affiliated.
   - Your institution's research office may already hold DHIS2 credentials.
2. **Indicators to request** (monthly, by state, 2015–present is realistic):
   - Confirmed malaria cases (RDT + microscopy), outpatient
   - Suspected cases / tested
   - Malaria cases by age band (<5, ≥5) if available
   - Tests performed (RDT, microscopy) — needed for test-positivity rate
   - ITN/LLIN distributed (intervention covariate)
3. **Export format.** DHIS2 exports CSV/Excel via the Pivot/Analytics app or the
   `/api/analytics` endpoint. Reshape to the schema below and drop into
   `data/raw/cases/monthly_cases.csv`. The pipeline picks it up automatically.

### Drop-in schema — `data/raw/cases/monthly_cases.csv`

See `data/raw/cases/TEMPLATE_monthly_cases.csv`. Columns:

```
state,year,month,confirmed_cases,suspected_cases,tested,population,source
Oyo,2019,1,12345,20100,18900,7840000,DHIS2-NMEP
```

- `state` must match the GADM spelling in `config/states.yaml`.
- `confirmed_cases` is the primary forecasting target.
- `tested` lets us compute test-positivity (less sensitive to reporting-rate drift).
- `population` (optional) → incidence per 1,000; WorldPop fills gaps.

## Fallback if DHIS2 access is delayed

The pipeline runs **without** monthly cases by:
- calibrating the mechanistic model to **MAP annual state PfPR**, forced by real
  monthly climate (so seasonality is mechanistic, validation is annual);
- using the model's monthly output as a target the ML emulator learns.

When the DHIS2 CSV arrives, the same pipeline switches to monthly case targets
with no restructuring.
