# Candidate predictors for Lassa fever spatial regression

Mechanism-based catalogue of state-level covariates, grouped by causal
pathway. The last two columns track where each can be obtained and whether
it is reachable from this cloud session's current network policy.

Legend for **Acquisition**:
`raster→zonal` = download gridded raster, average/sum within state polygons ·
`PDF table` = extract from a published report · `point→count` = geocode
point data (labs, occurrences), aggregate per state · `adjacency` = derive
from the boundary file (already available).

## A. Reservoir ecology (the source of spillover)
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| *Mastomys natalensis* occurrence / rel. abundance | Primary LASV reservoir | GBIF; published suitability models | point→count or raster→zonal | ✗ (api.gbif.org blocked) |
| Rodent LASV seroprevalence | Force of infection in reservoir | Literature (site-level, sparse) | manual | partial |
| Secondary reservoirs (*M. erythroleucus*, *Hylomyscus pamfi*) | Additional hosts | GBIF / literature | point→count | ✗ |
| % cropland / forest-edge / grassland | Rodent habitat | ESA CCI / Copernicus land cover | raster→zonal | ✗ |
| NDVI / vegetation greenness | Habitat productivity | MODIS / Sentinel | raster→zonal | ✗ |

## B. Climate (drives rodent cycles & dry-season peak)
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| Annual & seasonal rainfall | Rodent breeding; Dec–Mar peak | CHIRPS / WorldClim bio12 | raster→zonal | ✗ (data.chc.ucsb.edu blocked) |
| Rainfall seasonality | Timing of outbreaks | CHIRPS / WorldClim bio15 | raster→zonal | ✗ |
| Mean / min temperature | Rodent survival | WorldClim bio1/bio6 | raster→zonal | ✗ (ucdavis blocked) |
| Relative humidity, aridity index | Virus persistence, habitat | TerraClimate | raster→zonal | ✗ |

## C. Socioeconomic
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| **Multidimensional poverty (MPI)** | Deprivation → exposure | NBS 2022 MPI report | PDF table | ✗ (nigerianstat / ophi blocked) |
| Monetary poverty headcount | Vulnerability | NBS 2019 poverty survey | PDF table | ✗ |
| **Literacy rate** | Awareness, behaviour | NDHS 2018 | PDF table | ✗ (dhsprogram blocked) |
| Unemployment | Livelihood pressure | NBS labour force | PDF table | ✗ |
| Nightlights (GDP proxy) | Economic activity | NOAA VIIRS | raster→zonal | ✗ |

## D. Housing / WASH (proximate route into homes)
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| % mud/earthen walls, open eaves | Rodent entry to dwellings | NDHS 2018 housing module | PDF table | ✗ |
| Indoor / open food storage | Attracts rodents | NDHS / MICS | PDF table | ✗ |
| Improved water % | Hygiene | NDHS 2018 / HDX WASH | PDF / raster→zonal | ✗ (data.humdata.org blocked) |
| Improved sanitation %, open defecation | Environmental contamination | NDHS 2018 | PDF table | ✗ |
| Household crowding | Human–human & rodent contact | NDHS 2018 | PDF table | ✗ |

## E. Demographic
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| Population (incidence denominator) | Rate baseline | NPC 2006 census + projections / WorldPop | PDF / raster→zonal | ✗ (WorldPop blocked) |
| Population density | Transmission intensity | derived (pop / area_km2) | derived | once pop obtained |
| % rural | Reservoir contact | NDHS / WorldPop | PDF / raster→zonal | ✗ |
| % agricultural employment | Farm/bush exposure | NBS labour force | PDF table | ✗ |

## F. Health system (care access + survival / CFR)
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| Health-facility / physician density | Access to care | HeRAMS / HDX health facilities | point→count | ✗ |
| Presence of Lassa treatment centre | Ribavirin, outcomes | NCDC | manual list | ✓ (small, curatable) |
| Distance to nearest LASV diagnostic lab | **Detection + survival** | NCDC lab network | point→distance | ✓ (small, curatable) |

## G. Surveillance intensity (detection confounder — essential)
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| Suspected cases / tests performed | Detection effort | NCDC (in this dataset) | derived | ✓ already have |
| `pct_confirmed_of_suspected` | Test positivity | derived | derived | ✓ already have |
| Proximity to reference lab | Where we look | NCDC | point→distance | ✓ curatable |

## H. Spatial / connectivity
| Variable | Mechanism | Source | Acquisition | Reachable now? |
|---|---|---|---|---|
| Adjacency to a hotspot state | Diffusion / spillover | derived from boundaries | adjacency | ✓ have weights |
| Road connectivity | Movement of people | OSM / GRID3 | network | ✗ |
| Cross-border state | Importation | derived | adjacency | ✓ |

**Summary:** the spatial backbone, surveillance proxies, and curatable
health-geography variables (treatment centres, labs) are available now. The
raster- and PDF-based covariates (climate, land cover, poverty, literacy,
WASH, housing, population) need the blocked hosts allowlisted (see README),
or the files uploaded directly.
