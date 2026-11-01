"""State climate covariates from WorldClim 2.1 (5 arc-minute) bioclimatic
variables, averaged within state polygons (zonal mean).

Source: geodata.ucdavis.edu/climate/worldclim/2_1 (WorldClim 2.1, 1970-2000
normals). Selected variables relevant to Lassa fever / Mastomys ecology:
  bio1  Annual mean temperature (°C)
  bio4  Temperature seasonality (SD x100)
  bio12 Annual precipitation (mm)
  bio14 Precipitation of driest month (mm) - dry-season moisture
  bio15 Precipitation seasonality (CV %)
"""
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
from common import EXTERNAL, PROCESSED

WC = EXTERNAL / "worldclim"
VARS = {
    "bio_1": "temp_annual_mean_c",
    "bio_4": "temp_seasonality",
    "bio_12": "precip_annual_mm",
    "bio_14": "precip_driest_month_mm",
    "bio_15": "precip_seasonality_cv",
}


def main() -> None:
    g = gpd.read_file(PROCESSED / "states.geojson")[["State", "geometry"]]
    out = g[["State"]].copy()
    for bio, col in VARS.items():
        tif = WC / f"wc2.1_5m_{bio}.tif"
        zs = zonal_stats(g, str(tif), stats=["mean"], all_touched=True)
        out[col] = [round(z["mean"], 2) if z["mean"] is not None else None
                    for z in zs]
    dest = PROCESSED / "climate_state.csv"
    out.to_csv(dest, index=False)
    print(f"wrote {dest}  rows={len(out)}")
    print(out.sort_values("precip_annual_mm", ascending=False).head(6).to_string(index=False))
    print("...")
    print(out.sort_values("precip_annual_mm").head(6).to_string(index=False))


if __name__ == "__main__":
    main()
