"""Assemble the master state-level modeling frame from all built tables."""
import numpy as np
import pandas as pd
import geopandas as gpd
from common import PROCESSED

def main() -> None:
    g = gpd.read_file(PROCESSED / "states.geojson")
    out = pd.read_csv(PROCESSED / "outcome_state.csv")
    cov = pd.read_csv(PROCESSED / "covariates_available.csv")[
        ["State", "centroid_lat", "centroid_lon", "dist_nearest_lab_km",
         "has_treatment_centre", "borders_hotspot", "weeks_reporting"]]
    pop = pd.read_csv(PROCESSED / "population_state.csv")
    ses = pd.read_csv(PROCESSED / "socioeconomic_state.csv")
    gbif = pd.read_csv(PROCESSED / "gbif_rodents_state.csv")
    clim = pd.read_csv(PROCESSED / "climate_state.csv")

    m = (g.merge(out, on="State").merge(cov, on="State")
         .merge(pop, on="State").merge(ses, on="State").merge(gbif, on="State")
         .merge(clim, on="State"))

    # Epidemiological outcomes
    m["incidence_per100k"] = (1e5 * m["confirmed"] / m["population"]).round(3)
    m["susp_incidence_per100k"] = (1e5 * m["suspected"] / m["population"]).round(3)
    m["test_positivity_pct"] = (100 * m["confirmed"] / m["suspected"]).round(2)
    m["log_suspected"] = np.log1p(m["suspected"])
    m["log_pop"] = np.log(m["population"])
    m["log_popdens"] = np.log(m["pop_density_km2"])

    dest_csv = PROCESSED / "master_state.csv"
    m.drop(columns="geometry").to_csv(dest_csv, index=False)
    m.to_file(PROCESSED / "master_state.geojson", driver="GeoJSON")
    print(f"wrote {dest_csv}  rows={len(m)}  cols={m.shape[1]}")
    cols = ["State", "confirmed", "population", "incidence_per100k",
            "test_positivity_pct", "mpi", "pop_density_km2",
            "gbif_mnatalensis_n", "facilities_per_100k", "centroid_lat"]
    print(m[cols].sort_values("incidence_per100k", ascending=False)
          .head(12).to_string(index=False))


if __name__ == "__main__":
    main()
