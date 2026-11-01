"""State socioeconomic covariates.

Poverty: OPHI subnational Multidimensional Poverty Index for Nigeria
(MICS 2021), from HDX (nga_mpi.csv). The MPI bundles deprivations in
education (incl. schooling/literacy), health, and living standards
(water, sanitation, housing, cooking fuel, assets) -> an efficient composite
for several of the hypothesised drivers.

Health system: facility density from the HDX Nigeria health-facilities
registry (facilities per 100k population).
"""
import pandas as pd
from common import EXTERNAL, PROCESSED, canon, CANON_STATES

MPI = EXTERNAL / "hdx" / "nga_mpi.csv"
HEALTH = EXTERNAL / "hdx" / "nga_health.csv"
POP = PROCESSED / "population_state.csv"


def main() -> None:
    m = pd.read_csv(MPI)
    m = m[m["Admin 1 Name"].notna()].copy()
    m["State"] = m["Admin 1 Name"].map(canon)
    m = m[m["State"].isin(CANON_STATES)]
    ses = m[["State", "MPI", "Headcount Ratio", "Intensity of Deprivation",
             "Vulnerable to Poverty", "In Severe Poverty"]].rename(columns={
        "MPI": "mpi", "Headcount Ratio": "poverty_headcount_pct",
        "Intensity of Deprivation": "deprivation_intensity_pct",
        "Vulnerable to Poverty": "vulnerable_pct",
        "In Severe Poverty": "severe_poverty_pct"})
    assert len(ses) == 37, f"MPI states={len(ses)}"

    h = pd.read_csv(HEALTH, low_memory=False)
    h["State"] = h["state_name"].map(canon)
    h = h[h["State"].isin(CANON_STATES)]
    fac = h.groupby("State").size().rename("n_health_facilities").reset_index()
    # facility type mix (Primary/Secondary/Tertiary) if present
    if "type" in h.columns:
        sec = (h[h["type"].isin(["Secondary", "Tertiary"])]
               .groupby("State").size().rename("n_sec_tert_facilities"))
        fac = fac.merge(sec.reset_index(), on="State", how="left")
        fac["n_sec_tert_facilities"] = fac["n_sec_tert_facilities"].fillna(0).astype(int)

    pop = pd.read_csv(POP)[["State", "population"]]
    out = ses.merge(fac, on="State").merge(pop, on="State")
    out["facilities_per_100k"] = (1e5 * out["n_health_facilities"]
                                  / out["population"]).round(1)
    out = out.drop(columns="population").sort_values("mpi", ascending=False)

    dest = PROCESSED / "socioeconomic_state.csv"
    out.to_csv(dest, index=False)
    print(f"wrote {dest}  rows={len(out)}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
