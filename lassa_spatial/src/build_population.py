"""State population + density from WorldPop bottom-up v2.0 admin-level-1 table.

Source: data.worldpop.org/repo/wopr/NGA/population/v2.0 (CC-BY). Gives a
modeled total population per state (national ~216.7M). Density uses polygon
area (UTM 32N) from states.geojson.
"""
import pandas as pd
import geopandas as gpd
from common import EXTERNAL, PROCESSED, canon, CANON_STATES

SRC = EXTERNAL / "wpop_admin" / "NGA_population_v2_0_admin_level1.csv"


def main() -> None:
    p = pd.read_csv(SRC)
    p["State"] = p["state"].map(canon)
    p = p.rename(columns={"mean": "population"})[["State", "population"]]
    p["population"] = p["population"].round().astype(int)

    missing = set(CANON_STATES) - set(p["State"])
    assert not missing, f"missing: {missing}"

    area = gpd.read_file(PROCESSED / "states.geojson")[["State", "area_km2"]]
    out = p.merge(area, on="State")
    out["pop_density_km2"] = (out["population"] / out["area_km2"]).round(1)
    out = out.sort_values("population", ascending=False)

    dest = PROCESSED / "population_state.csv"
    out.to_csv(dest, index=False)
    print(f"wrote {dest}  national={out['population'].sum():,}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
