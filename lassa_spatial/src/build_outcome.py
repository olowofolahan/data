"""Build the state-level Lassa fever outcome table (cross-sectional, 37 states).

Reads the NCDC State_Weekly surveillance tab and produces one row per state
with cumulative and per-year Suspected/Confirmed/Deaths, CFR, and the
confirmed-share of suspected (a crude test-positivity / detection signal).
"""
import pandas as pd
from common import RAW, PROCESSED, canon

SRC = RAW / "Lassa_Fever_Nigeria_Data_2020_2026.xlsx"
NUM = ["Suspected", "Confirmed", "Probable", "HCW cases", "Deaths"]


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="State_Weekly")
    df["State"] = df["State"].map(canon)
    for c in NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    cum = df.groupby("State").agg(
        suspected=("Suspected", "sum"),
        confirmed=("Confirmed", "sum"),
        probable=("Probable", "sum"),
        hcw_cases=("HCW cases", "sum"),
        deaths=("Deaths", "sum"),
        weeks_reporting=("Epi week", "size"),
    ).reset_index()

    cum["cfr_confirmed_pct"] = (100 * cum["deaths"] / cum["confirmed"]).round(3)
    cum["pct_confirmed_of_suspected"] = (
        100 * cum["confirmed"] / cum["suspected"]
    ).round(3)

    yr = df.pivot_table(index="State", columns="Year", values="Confirmed",
                        aggfunc="sum", fill_value=0)
    yr.columns = [f"conf_{int(c)}" for c in yr.columns]
    out = cum.merge(yr.reset_index(), on="State").sort_values(
        "confirmed", ascending=False)

    # Mean annual confirmed over complete-ish seasons (exclude partial 2020 & 2026)
    full_years = [c for c in ["conf_2021", "conf_2022", "conf_2023",
                              "conf_2024", "conf_2025"] if c in out.columns]
    out["conf_mean_annual_2021_2025"] = out[full_years].mean(axis=1).round(2)

    dest = PROCESSED / "outcome_state.csv"
    out.to_csv(dest, index=False)
    print(f"wrote {dest}  rows={len(out)}")
    print(out[["State", "suspected", "confirmed", "deaths",
               "cfr_confirmed_pct", "pct_confirmed_of_suspected"]].head(8)
          .to_string(index=False))


if __name__ == "__main__":
    main()
