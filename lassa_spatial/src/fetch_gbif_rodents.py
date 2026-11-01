"""Fetch rodent-reservoir occurrence records from GBIF for Nigeria and
aggregate to states by point-in-polygon.

Targets the main Lassa reservoir (Mastomys natalensis) and the wider
Mastomys genus plus other documented/candidate reservoirs. Produces per-state
occurrence counts and a presence flag. Occurrence counts reflect sampling
effort as well as true distribution -> treat as a coarse reservoir proxy.
"""
import time
import requests
import pandas as pd
import geopandas as gpd
from common import PROCESSED, EXTERNAL

API = "https://api.gbif.org/v1/occurrence/search"
# GBIF taxonKeys: genus Mastomys = 2439233; we match by genus for breadth.
TAXA = {
    "Mastomys natalensis": "2438911",
    "Mastomys genus": "2438904",
    "Rattus rattus": "2439270",
    "Mus musculus": "7429082",
}


def fetch(taxon_key: str) -> pd.DataFrame:
    rows, offset, limit = [], 0, 300
    while True:
        r = requests.get(API, params={
            "taxonKey": taxon_key, "country": "NG", "hasCoordinate": "true",
            "hasGeospatialIssue": "false", "limit": limit, "offset": offset},
            timeout=60)
        r.raise_for_status()
        js = r.json()
        for o in js.get("results", []):
            rows.append({"lat": o.get("decimalLatitude"),
                         "lon": o.get("decimalLongitude"),
                         "year": o.get("year"),
                         "species": o.get("species")})
        if js.get("endOfRecords", True):
            break
        offset += limit
        time.sleep(0.2)
    df = pd.DataFrame(rows).dropna(subset=["lat", "lon"])
    return df


def main() -> None:
    frames = {}
    for name, key in TAXA.items():
        df = fetch(key)
        frames[name] = df
        print(f"{name}: {len(df)} georeferenced records")

    states = gpd.read_file(PROCESSED / "states.geojson")[["State", "geometry"]]
    out = states[["State"]].copy()

    for name, df in frames.items():
        if df.empty:
            out[f"gbif_{name.split()[0].lower()}_n"] = 0
            continue
        pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat),
                               crs=4326)
        j = gpd.sjoin(pts, states, how="inner", predicate="within")
        cnt = j.groupby("State").size()
        col = f"gbif_{name.split()[0].lower()}"
        if "natalensis" in name:
            col = "gbif_mnatalensis"
        out[f"{col}_n"] = out["State"].map(cnt).fillna(0).astype(int)

    out["mastomys_present"] = (out["gbif_mastomys_n"] > 0).astype(int) \
        if "gbif_mastomys_n" in out else 0
    dest = PROCESSED / "gbif_rodents_state.csv"
    out.to_csv(dest, index=False)
    print(f"\nwrote {dest}")
    print(out.sort_values("gbif_mnatalensis_n", ascending=False).head(12)
          .to_string(index=False))


if __name__ == "__main__":
    main()
