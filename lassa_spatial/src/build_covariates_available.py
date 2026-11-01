"""Build the covariate table from sources reachable/curatable in this session.

NOT included (blocked network -> pending): climate, land cover, poverty/MPI,
literacy, WASH, housing, population/WorldPop. See VARIABLES.md.

Included here:
  - Geography derived from the boundary polygons: centroid lat/lon, area.
  - Surveillance proxies from the NCDC dataset (detection-effort confounder).
  - Health geography: distance (km) to the nearest NCDC Lassa diagnostic lab,
    and a treatment-centre flag.  CURATED from NCDC's publicly documented
    LASV molecular-testing network (situation reports); city-level coordinates
    are approximate and flagged for verification.
  - Spatial structure: borders a LISA High-High hotspot state.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from common import PROCESSED, canon

PROJ = 32632  # UTM 32N, metres

# Curated NCDC LASV diagnostic laboratories (name, state, approx lat, lon).
# Provenance: NCDC Lassa fever situation reports / NCDC laboratory network.
# Coordinates are city/institution level and APPROXIMATE -> verify before use.
LABS = [
    ("ISTH Irrua",                  "Edo",    6.730, 6.218),
    ("UBTH Benin",                  "Edo",    6.396, 5.624),
    ("FMC Owo",                     "Ondo",   7.196, 5.587),
    ("ACEGID Redeemer's, Ede",      "Osun",   7.740, 4.441),
    ("NCDC NRL Abuja",              "FCT",    8.986, 7.382),
    ("CPHL / LUTH Lagos",           "Lagos",  6.517, 3.380),
    ("ATBUTH Bauchi",               "Bauchi", 10.312, 9.844),
    ("UMTH Maiduguri",              "Borno", 11.846, 13.157),
    ("AE-FUTHA Abakaliki",          "Ebonyi", 6.324, 8.113),
]
# States with a designated Lassa treatment centre (documented, approximate).
TREATMENT_CENTRE_STATES = {"Edo", "Ondo", "Ebonyi", "Bauchi", "Taraba", "FCT"}


def main() -> None:
    g = gpd.read_file(PROCESSED / "states.geojson")
    gp = g.to_crs(PROJ)
    cen = gp.geometry.centroid
    g["cx"], g["cy"] = cen.x.values, cen.y.values  # metres, for distances
    cen_ll = gpd.GeoSeries(cen, crs=PROJ).to_crs(4326)
    g["centroid_lat"] = cen_ll.y.round(4).values
    g["centroid_lon"] = cen_ll.x.round(4).values

    labs = gpd.GeoDataFrame(
        pd.DataFrame(LABS, columns=["lab", "state", "lat", "lon"]),
        geometry=gpd.points_from_xy([l[3] for l in LABS], [l[2] for l in LABS]),
        crs=4326).to_crs(PROJ)
    lx, ly = labs.geometry.x.values, labs.geometry.y.values
    dmin = [np.min(np.hypot(r.cx - lx, r.cy - ly)) / 1000.0 for r in g.itertuples()]
    g["dist_nearest_lab_km"] = np.round(dmin, 1)
    g["has_treatment_centre"] = g["State"].isin(TREATMENT_CENTRE_STATES).astype(int)

    # Borders a High-High hotspot state (from LISA results).
    lisa = pd.read_csv(PROCESSED / "lisa_results.csv")
    hh = set(lisa.loc[lisa["lisa_cluster"] == "High-High", "State"])
    w = Queen.from_dataframe(g, ids=g["State"].tolist(), use_index=False)
    g["borders_hotspot"] = [
        int(any(nb in hh for nb in w.neighbors[s]) or s in hh)
        for s in g["State"]]

    # Surveillance proxies from the outcome table.
    out = pd.read_csv(PROCESSED / "outcome_state.csv")
    g = g.merge(out[["State", "suspected", "confirmed", "deaths",
                     "weeks_reporting", "pct_confirmed_of_suspected"]], on="State")

    cols = ["State", "centroid_lat", "centroid_lon", "area_km2",
            "dist_nearest_lab_km", "has_treatment_centre", "borders_hotspot",
            "suspected", "weeks_reporting", "pct_confirmed_of_suspected",
            "confirmed", "deaths"]
    tab = g[cols].sort_values("confirmed", ascending=False)
    dest = PROCESSED / "covariates_available.csv"
    tab.to_csv(dest, index=False)
    print(f"wrote {dest}  rows={len(tab)}")
    print(tab.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
