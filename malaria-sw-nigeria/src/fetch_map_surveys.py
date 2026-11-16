"""Fetch Malaria Atlas Project P. falciparum survey points for Nigeria and
clip to the six SW states. These are sparse (~32 pts in SW) -> used for
VALIDATION, not primary modelling (use the modelled raster for that).

python3 -I src/fetch_map_surveys.py
"""
import pathlib
import urllib.request

import geopandas as gpd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "map"
PROC = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

LAYER = "Malaria:202406_Global_Pf_Parasite_Rate_Surveys"
WFS = (
    "https://data.malariaatlas.org/geoserver/Malaria/ows"
    "?service=WFS&version=2.0.0&request=GetFeature"
    f"&typeName={LAYER}&outputFormat=application/json"
    "&cql_filter=country_id='NGA' AND malaria_metrics_available=true"
)


def main() -> None:
    cfg = yaml.safe_load((ROOT / "config" / "states.yaml").read_text())
    states = cfg["states"]

    raw_path = RAW / "nga_pf_surveys.json"
    print("Downloading MAP Pf surveys for Nigeria ...")
    urllib.request.urlretrieve(WFS.replace(" ", "%20"), raw_path)

    pts = gpd.read_file(raw_path)
    pts = pts[pts.geometry.notna() & pts["pf_pr"].notna()].copy()

    bnd = gpd.read_file(ROOT / "data" / "raw" / "boundaries" / "gadm41_NGA_1.json")
    bnd = bnd[bnd["NAME_1"].isin(states)][["NAME_1", "geometry"]]

    sw = gpd.sjoin(pts, bnd, predicate="within", how="inner").rename(
        columns={"NAME_1": "state"}
    )
    sw = sw.drop(columns=[c for c in ["index_right"] if c in sw])
    sw.to_file(PROC / "sw_pf_surveys.geojson", driver="GeoJSON")

    print(f"Nigeria survey points: {len(pts)} | inside SW states: {len(sw)}")
    summary = (
        sw.groupby("state")
        .agg(points=("pf_pr", "size"), mean_pfpr=("pf_pr", "mean"),
             yr_min=("year_start", "min"), yr_max=("year_start", "max"))
        .round(3)
    )
    print(summary.to_string())
    print(f"Saved -> {PROC/'sw_pf_surveys.geojson'}")


if __name__ == "__main__":
    main()
