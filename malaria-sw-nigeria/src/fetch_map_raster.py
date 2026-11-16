"""Fetch the Malaria Atlas Project modelled PfPR (2-10) surface via WCS and
reduce to per-state values for the six SW states. This is the CALIBRATION
TARGET for the mechanistic model.

The coverage exposes 4 fields: band 1 = Data (PfPR point estimate),
band 2 = population mask, band 3 = LCI, band 4 = UCI (95% credible interval)
for the latest modelled year of the chosen release.

python3 -I src/fetch_map_raster.py
"""
import io
import pathlib
import urllib.request

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import yaml
from rasterio.mask import mask

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "map"
PROC = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)

RELEASE = "202406"            # MAP data release; latest modelled year
COV = f"Malaria__{RELEASE}_Global_Pf_Parasite_Rate"
# SW Nigeria bounding window
BBOX = dict(lon=(2.5, 6.1), lat=(5.4, 9.6))
WCS = (
    "https://data.malariaatlas.org/geoserver/Malaria/ows?service=WCS&version=2.0.1"
    f"&request=GetCoverage&coverageId={COV}&format=image/geotiff"
    f"&subset=Long({BBOX['lon'][0]},{BBOX['lon'][1]})"
    f"&subset=Lat({BBOX['lat'][0]},{BBOX['lat'][1]})"
)
BANDS = {1: "pfpr", 3: "pfpr_lci", 4: "pfpr_uci"}


def main() -> None:
    cfg = yaml.safe_load((ROOT / "config" / "states.yaml").read_text())
    states = cfg["states"]

    tif = RAW / f"pfpr_sw_{RELEASE}.tif"
    print(f"Downloading MAP PfPR surface ({COV}) ...")
    urllib.request.urlretrieve(WCS, tif)

    bnd = gpd.read_file(ROOT / "data" / "raw" / "boundaries" / "gadm41_NGA_1.json")
    bnd = bnd[bnd["NAME_1"].isin(states)][["NAME_1", "geometry"]]

    rows = []
    with rasterio.open(tif) as src:
        nod = src.nodata
        for _, r in bnd.iterrows():
            rec = {"state": r["NAME_1"]}
            for band, name in BANDS.items():
                out, _ = mask(src, [r.geometry.__geo_interface__], crop=True,
                              nodata=nod, indexes=[band])
                a = out[0].astype("float64")
                a = a[(a != nod) & np.isfinite(a) & (a >= 0)]
                rec[name] = round(float(np.nanmean(a)), 4)
            rows.append(rec)

    df = pd.DataFrame(rows).sort_values("state").reset_index(drop=True)
    df["release"] = RELEASE
    out = PROC / "sw_map_pfpr.csv"
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nSaved calibration target -> {out}")
    print("NOTE: PfPR is age-standardised (2-10y); convert when comparing to "
          "all-age model prevalence (see calibrate.py).")


if __name__ == "__main__":
    main()
