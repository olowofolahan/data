# Network allowlist — hosts to add (kidnapping-framed study)

Study reframed around **kidnapping / abduction** as the fear object. To pull the
kidnapping-specific layers automatically, add the hosts below to this
environment's network allowlist (Settings → Environment → Network).

Use **exact lowercase hostnames, no `https://`, no paths, no wildcards.**

## Already allowed (no action needed)
`data.humdata.org` · `en.wikipedia.org` · `dhsprogram.com` · `data.worldpop.org` ·
`drive.google.com` · `drive.usercontent.google.com` · `api.gbif.org` · `geodata.ucdavis.edu`

---

## Tier 1 — essential (directly unlock the kidnapping + fear layers)
```
acleddata.com
api.acleddata.com
www.afrobarometer.org
nigerianstat.gov.ng
microdata.nigerianstat.gov.ng
```
- **acleddata.com / api.acleddata.com** — ACLED portal + API. Needed to filter the
  `Abduction/forced disappearance` sub-event by state (the HDX mirror only gives
  aggregate totals, not kidnapping specifically). API needs a free registered key.
- **www.afrobarometer.org** — perceived insecurity / fear of crime / kidnapping
  items (R9 2022, R10 2024), dispatches + microdata. The perception layer.
- **nigerianstat.gov.ng + microdata.nigerianstat.gov.ng** — NBS crime statistics
  (police-reported kidnapping offences) and NBS National MPI 2022.

## Tier 2 — high value (kidnapping-specialist trackers + corroboration)
```
www.noi-polls.com
www.sbmintel.com
humanglemedia.com
dataphyte.com
www.nigeriawatch.org
www.cfr.org
www.acaps.org
```
- **www.noi-polls.com** — Nigerian polls on kidnapping as a "serious problem".
- **www.sbmintel.com** — SBM Intelligence kidnap-industry reports (ransom, hotspots).
- **humanglemedia.com** — HumAngle abduction tracking / data journalism.
- **dataphyte.com** — Nigerian data journalism, kidnapping trackers.
- **www.nigeriawatch.org** — per-capita lethal-violence ranking by state.
- **www.cfr.org** — Council on Foreign Relations Nigeria Security Tracker.
- **www.acaps.org** — ACAPS Nigeria conflict/abduction analysis.

---
If a bare host fails, add its `www.` variant (or vice-versa). Tell me once added
and I'll pull kidnapping incidence by state, fill the perception column, and
rebuild the dataset with a kidnapping framing.
