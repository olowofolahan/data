"""Build the monthly climate forcing for the six SW states.

Primary (reliable, open): WorldClim 2.1 monthly climatology -> 12-month normals
of precipitation and mean temperature per state. This drives the mechanistic
model's SEASONAL cycle.

For INTERANNUAL monthly series (needed once DHIS2 monthly cases are in hand),
CHIRPS/CHIRTS on data.chc.ucsb.edu can be added; see fetch_chirps_month().
That host is intermittent through the proxy, so a retry wrapper is included.

python3 -I src/fetch_climate.py --res 2.5m
"""
import argparse
import io
import pathlib
import time
import urllib.request
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import yaml
from rasterio.mask import mask

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "climate"
PROC = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

WC = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_{res}_{var}.zip"


def _download(url: str, dest: pathlib.Path, retries: int = 4) -> pathlib.Path:
    for i in range(retries):
        try:
            urllib.request.urlretrieve(url, dest)
            return dest
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1}/{retries} ({e})")
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"failed: {url}")


def worldclim_climatology(res: str, states: list[str]) -> pd.DataFrame:
    bnd = gpd.read_file(ROOT / "data" / "raw" / "boundaries" / "gadm41_NGA_1.json")
    bnd = bnd[bnd["NAME_1"].isin(states)][["NAME_1", "geometry"]]
    rows = []
    varmap = {"prec": "precip_mm", "tavg": "tavg_c"}
    for var, col in varmap.items():
        zpath = RAW / f"wc2.1_{res}_{var}.zip"
        if not zpath.exists():
            print(f"Downloading WorldClim {var} ({res}) ...")
            _download(WC.format(res=res, var=var), zpath)
        zf = zipfile.ZipFile(zpath)
        tifs = sorted(n for n in zf.namelist() if n.endswith(".tif"))
        for month, name in enumerate(tifs, start=1):  # 12 files, Jan..Dec
            with rasterio.open(io.BytesIO(zf.read(name))) as src:
                nod = src.nodata
                for _, r in bnd.iterrows():
                    out, _ = mask(src, [r.geometry.__geo_interface__], crop=True,
                                  nodata=nod)
                    a = out[0].astype("float64")
                    a = a[(a != nod) & np.isfinite(a)]
                    rows.append({"state": r["NAME_1"], "month": month,
                                 "var": col, "value": round(float(np.nanmean(a)), 2)})
    df = (pd.DataFrame(rows)
          .pivot_table(index=["state", "month"], columns="var", values="value")
          .reset_index())
    return df


def fetch_chirps_month(year: int, month: int, states, retries: int = 5):
    """Interannual monthly rainfall (mm) per state from CHIRPS. Intermittent host."""
    url = ("https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/"
           f"chirps-v2.0.{year}.{month:02d}.tif.gz")
    import gzip
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                raw = gzip.decompress(r.read())
            bnd = gpd.read_file(ROOT / "data/raw/boundaries/gadm41_NGA_1.json")
            bnd = bnd[bnd["NAME_1"].isin(states)]
            res = {}
            with rasterio.open(io.BytesIO(raw)) as src:
                for _, row in bnd.iterrows():
                    out, _ = mask(src, [row.geometry.__geo_interface__], crop=True,
                                  nodata=src.nodata)
                    a = out[0].astype("float64")
                    a = a[a != src.nodata]
                    res[row["NAME_1"]] = round(float(np.nanmean(a)), 2)
            return res
        except Exception as e:  # noqa: BLE001
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"CHIRPS failed {year}-{month:02d}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="2.5m", choices=["10m", "5m", "2.5m"])
    args = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "config" / "states.yaml").read_text())
    states = cfg["states"]
    df = worldclim_climatology(args.res, states)
    out = PROC / "sw_climatology.csv"
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nSaved monthly climatology -> {out}")


if __name__ == "__main__":
    main()
