"""Interannual monthly climate for the SW states from WorldClim 2.1 historical
weather (CRU-TS 4.09 downscaled). Real month-by-month precipitation and
temperature -> the ML covariate set and the mechanistic model's interannual
forcing.

Downloads decade zips (prec, tmin, tmax) at 10m, extracts per-month GeoTIFFs,
computes per-state zonal means, derives tavg=(tmin+tmax)/2, writes a tidy
state-year-month table. Zips are deleted after processing to save disk.

python3 -I src/fetch_climate_interannual.py --start 2010 --end 2024
"""
import argparse
import pathlib
import re
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

BASE = ("https://geodata.ucdavis.edu/climate/worldclim/2_1/hist/cts4.09/"
        "wc2.1_cruts4.09_{res}_{var}_{decade}.zip")
DECADES = ["2000-2009", "2010-2019", "2020-2024"]


def _download(url, dest, retries=4):
    for i in range(retries):
        try:
            urllib.request.urlretrieve(url, dest)
            return dest
        except Exception as e:  # noqa: BLE001
            print(f"  retry {i+1}/{retries}: {e}")
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"failed {url}")


def _decades_for(start, end):
    out = []
    for d in DECADES:
        a, b = (int(x) for x in d.split("-"))
        if b >= start and a <= end:
            out.append(d)
    return out


def zonal_month(zpath, bnd, states):
    """Return {(year,month): {state: mean}} for every tif in the zip."""
    res = {}
    zf = zipfile.ZipFile(zpath)
    for name in zf.namelist():
        if not name.endswith(".tif"):
            continue
        mobj = re.search(r"_(\d{4})-(\d{2})\.tif$", name)
        if not mobj:
            continue
        year, month = int(mobj.group(1)), int(mobj.group(2))
        import io
        with rasterio.open(io.BytesIO(zf.read(name))) as src:
            vals = {}
            for _, r in bnd.iterrows():
                out, _ = mask(src, [r.geometry.__geo_interface__], crop=True,
                              nodata=src.nodata, indexes=[1])
                a = out[0].astype("float64")
                a = a[(a != src.nodata) & np.isfinite(a)]
                vals[r["NAME_1"]] = float(np.nanmean(a)) if a.size else np.nan
        res[(year, month)] = vals
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2010)
    ap.add_argument("--end", type=int, default=2024)
    ap.add_argument("--res", default="10m")
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / "config" / "states.yaml").read_text())
    states = cfg["states"]
    bnd = gpd.read_file(ROOT / "data/raw/boundaries/gadm41_NGA_1.json")
    bnd = bnd[bnd["NAME_1"].isin(states)][["NAME_1", "geometry"]]

    frames = {}
    for var in ["prec", "tmin", "tmax"]:
        series = {}
        for dec in _decades_for(args.start, args.end):
            url = BASE.format(res=args.res, var=var, decade=dec)
            zpath = RAW / f"wc_{var}_{dec}.zip"
            print(f"Downloading {var} {dec} ...")
            _download(url, zpath)
            print(f"  processing {zpath.name} ...")
            series.update(zonal_month(zpath, bnd, states))
            zpath.unlink(missing_ok=True)      # free disk
        frames[var] = series

    rows = []
    for (year, month), prec_vals in frames["prec"].items():
        if not (args.start <= year <= args.end):
            continue
        for st in states:
            tmin = frames["tmin"].get((year, month), {}).get(st, np.nan)
            tmax = frames["tmax"].get((year, month), {}).get(st, np.nan)
            rows.append({
                "state": st, "year": year, "month": month,
                "precip_mm": round(prec_vals.get(st, np.nan), 2),
                "tavg_c": round((tmin + tmax) / 2.0, 2),
                "tmin_c": round(tmin, 2), "tmax_c": round(tmax, 2),
            })
    df = (pd.DataFrame(rows)
          .sort_values(["state", "year", "month"]).reset_index(drop=True))
    out = PROC / "sw_climate_monthly.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {len(df)} state-months "
          f"({df.year.min()}-{df.year.max()}) -> {out}")
    print(df.groupby("state")["precip_mm"].agg(["count", "mean"]).round(1).to_string())


if __name__ == "__main__":
    main()
