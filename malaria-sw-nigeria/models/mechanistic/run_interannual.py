"""Force the calibrated mechanistic model with REAL interannual monthly climate
(sw_climate_monthly.csv) to produce a monthly prevalence hindcast per state,
2010-2024. This series:
  - is a deliverable in its own right (climate-driven interannual dynamics), and
  - serves as the ML target/benchmark until DHIS2 monthly cases are available.

python3 run_interannual.py
"""
import pathlib

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

import climate_seir as m

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIM = ROOT / "data" / "processed" / "sw_climate_monthly.csv"
PARAMS = pathlib.Path(__file__).resolve().parent / "calibrated_params.csv"
OUT = ROOT / "data" / "processed" / "sw_mechanistic_monthly.csv"


def interannual_forcing(df_state):
    """Daily interpolators of temp & rain across the full multi-year span."""
    d = df_state.sort_values(["year", "month"]).reset_index(drop=True)
    # day index at mid-month for each row, from series start
    t0 = d["year"].iloc[0]
    day = ((d["year"] - t0) * 365 + (d["month"] - 1) * 30.4 + 15).to_numpy()
    temp = d["tavg_c"].to_numpy()
    rain = d["precip_mm"].to_numpy()
    return (day,
            lambda t: np.interp(t, day, temp),
            lambda t: np.interp(t, day, rain),
            d)


def run_state(state, m0):
    df = pd.read_csv(CLIM)
    ds = df[df["state"] == state]
    if ds.empty:
        raise SystemExit(f"No interannual climate for {state}.")
    day, tempf, rainf, d = interannual_forcing(ds)
    p = {**m.DEFAULT_PARAMS, "m0": m0}
    forcing = {"temp": tempf, "rain": rainf}

    # spin up 4 years on the first year's climate, then integrate the record
    y0 = [0.6, 0, 0.1, 0.3, 7.0, 0.2, 0.1]
    spin = solve_ivp(m.rhs, [0, 365 * 4], y0, args=(forcing, p),
                     max_step=6, rtol=1e-6, atol=1e-8)
    y0 = spin.y[:, -1]
    sol = solve_ivp(m.rhs, [day.min() - 30, day.max() + 30], y0,
                    args=(forcing, p), max_step=6, dense_output=True,
                    rtol=1e-6, atol=1e-8)
    Y = sol.sol(day)
    prev = Y[2] / (Y[0] + Y[1] + Y[2] + Y[3])
    out = d[["state", "year", "month"]].copy()
    out["prevalence"] = np.round(prev, 5)
    return out


def main():
    cal = pd.read_csv(PARAMS)[["state", "fitted_m0"]]
    frames = []
    for _, r in cal.iterrows():
        print(f"  simulating {r['state']} (m0={r['fitted_m0']:.2f}) ...")
        frames.append(run_state(r["state"], r["fitted_m0"]))
    res = pd.concat(frames, ignore_index=True)
    res.to_csv(OUT, index=False)
    print(f"\nSaved {len(res)} state-months -> {OUT}")
    print(res.groupby("state")["prevalence"].agg(["mean", "min", "max"]).round(3).to_string())


if __name__ == "__main__":
    main()
