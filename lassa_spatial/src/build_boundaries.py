"""Build harmonized Nigeria state polygons + contiguity spatial weights.

Source: Natural Earth 10m Admin-1 (public domain), filtered to Nigeria.
Outputs a GeoJSON (processed/states.geojson) with canonical names and
area_km2, plus a queen-contiguity neighbour list (processed/queen_weights.gal).
"""
import geopandas as gpd
from libpysal.weights import Queen
from common import EXTERNAL, PROCESSED, CANON_STATES, canon

NE = EXTERNAL / "ne_admin1" / "ne_10m_admin_1_states_provinces.shp"
# Nigeria lies in UTM zone 32N; EPSG:32632 gives metric area in m^2.
EQ_AREA = 32632


def main() -> None:
    g = gpd.read_file(NE)
    ng = g[g["admin"] == "Nigeria"].copy()
    ng["State"] = ng["name"].map(canon)

    missing = set(CANON_STATES) - set(ng["State"])
    extra = set(ng["State"]) - set(CANON_STATES)
    assert not missing, f"missing states: {missing}"
    assert not extra, f"unexpected states: {extra}"

    ng["area_km2"] = (ng.to_crs(EQ_AREA).geometry.area / 1e6).round(1)
    ng = ng[["State", "area_km2", "geometry"]].sort_values("State").reset_index(drop=True)

    dest = PROCESSED / "states.geojson"
    ng.to_file(dest, driver="GeoJSON")
    print(f"wrote {dest}  units={len(ng)}")

    w = Queen.from_dataframe(ng, ids=ng["State"].tolist(), use_index=False)
    print(f"queen weights: avg neighbours={w.mean_neighbors:.2f}, "
          f"islands={w.islands}")
    w.to_file(str(PROCESSED / "queen_weights.gal"))
    print("wrote queen_weights.gal")


if __name__ == "__main__":
    main()
