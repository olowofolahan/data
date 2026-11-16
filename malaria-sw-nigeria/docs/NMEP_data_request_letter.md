# Data request — monthly malaria surveillance data, South-West Nigeria

> Draft for you to adapt. Replace every **[bracketed]** field. Send on
> institutional letterhead (print or PDF with signature). Keep it to one page;
> attach the "Technical data specification" below as page 2.

---

**[Your Name]**
**[Title / Programme, e.g. MSc Candidate, Dept. of Epidemiology]**
**[Institution]**
**[Address] · [email] · [phone]**

**Date:** [DD Month YYYY]

**To:** The National Coordinator
National Malaria Elimination Programme (NMEP)
Federal Ministry of Health and Social Welfare
Abuja, Nigeria

**Through:** [State Epidemiologist / State Malaria Programme Manager, if routing
via a State Ministry of Health]

**Subject: Request for routine monthly malaria surveillance data (DHIS2/HMIS) for
six South-West states, for academic research**

Dear Sir/Madam,

I am **[role]** at **[institution]**, conducting a research study titled
**"[study title — e.g. Climate-driven transmission dynamics and forecasting of
malaria in South-West Nigeria]"**, under the supervision of **[supervisor /
department]**. The study develops a climate-forced transmission model and
statistical forecasting of malaria, to inform the timing and targeting of control
activities.

I write to request access to **aggregate, routine monthly malaria surveillance
data** held in the National Health Management Information System (DHIS2), for the
six states of the **South-West zone — Lagos, Oyo, Ogun, Osun, Ondo and Ekiti** —
for the period **[start, e.g. January 2015] to [most recent complete month]**.

The data requested are **facility-aggregated counts, not individual patient
records**, at **state and (where available) LGA** level. The specific indicators
are listed in the attached technical specification.

**Data handling and ethics.** The data will be used solely for the academic
purpose stated, stored securely on **[encrypted institutional storage]**, not
shared with third parties, and reported only in aggregate. NMEP/the State
Ministry will be **acknowledged in all outputs**, and I will share a copy of the
findings. Ethical approval **[has been obtained from / has been applied for at]
[name of Health Research Ethics Committee], ref. [number]**.

I am happy to complete any data-sharing agreement or data-request form NMEP
requires, and to cover any administrative costs. I can be reached at **[email /
phone]**.

Thank you for your consideration.

Yours faithfully,

**[Signature]**
**[Your Name]**

---

## Technical data specification (attach as page 2)

**Geography:** Lagos, Oyo, Ogun, Osun, Ondo, Ekiti (South-West zone).
**Disaggregation:** by **state** and, if available, **LGA**.
**Frequency:** **monthly**.   **Period:** [start] – [latest complete month].
**Format:** CSV or Excel export from the DHIS2 Pivot/Analytics app (long format
preferred: one row per state × month × indicator).

**Indicators requested** (standard NHMIS/NMEP malaria data elements):

| # | Indicator | Why needed |
|---|---|---|
| 1 | Confirmed malaria cases (RDT) — outpatient | Primary forecasting target |
| 2 | Confirmed malaria cases (microscopy) — outpatient | Combine with RDT |
| 3 | Suspected malaria cases | Denominator for test-positivity |
| 4 | Malaria tests conducted (RDT + microscopy) | Test-positivity rate (reporting-robust) |
| 5 | Confirmed cases <5 years / ≥5 years | Age-structured transmission |
| 6 | Malaria admissions and deaths (inpatient) | Severity / burden |
| 7 | LLINs/ITNs distributed | Intervention covariate |
| 8 | ANC/IPTp doses (if available) | Intervention covariate |
| 9 | Monthly facility reporting rate (completeness/timeliness) | Adjust for reporting bias |

**Note on reporting completeness (item 9):** routine case counts are sensitive to
how many facilities reported each month. The monthly **reporting/completeness
rate** per state is essential to distinguish true epidemiological change from
reporting artefacts, and is used to adjust the series before modelling.

**Delivery target for the analysis pipeline:** reshaped to
`data/raw/cases/monthly_cases.csv` with columns
`state, year, month, confirmed_cases, suspected_cases, tested, population,
source` (see `docs/DATA_ACCESS.md`). I can accept the raw DHIS2 export and do the
reshaping.

---

### Alternative / parallel routes while the formal request is processed
- **WHO Nigeria** and **US President's Malaria Initiative (PMI)** country teams
  often hold or can facilitate access to DHIS2 extracts for research.
- **Malaria Consortium** and **state malaria programmes** are possible partners.
- Your **institution's research office** may already have DHIS2 credentials.
- Some states publish **DHIS2 public dashboards**; confirm whether aggregate
  monthly malaria exports are openly available for your states.
