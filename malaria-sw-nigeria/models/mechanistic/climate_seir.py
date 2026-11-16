"""Climate-forced malaria transmission model for a single state.

Human SEIR coupled to mosquito SEI (Ross-Macdonald family). Mosquito traits are
temperature-dependent (Mordecai-style thermal responses); larval carrying
capacity is rainfall-dependent. Forced by the WorldClim monthly climatology from
src/fetch_climate.py.

Parameterised and importable: `annual_prevalence(state, params)` and
`simulate(state, params)` are used by calibrate.py. Per-state transmission
intensity is set by params['m0'] (baseline mosquitoes per human), the parameter
calibrated to MAP PfPR.

Run:  python3 -I models/mechanistic/climate_seir.py --state Oyo --m0 20
"""
import argparse
import pathlib

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIM = ROOT / "data" / "processed" / "sw_climatology.csv"

# NOTE: m0 is an EFFECTIVE transmission-intensity / vector-density scaler, not a
# literal mosquito count (its scale is set by the simplified biting/efficiency
# constants). Calibration recovers RELATIVE transmission intensity across states.
# omega/gamma set the attainable prevalence range: with these values the model
# spans ~0.05-0.80 prevalence, covering the SW PfPR gradient (Lagos low -> others
# high) without saturating. See docs for the age-standardisation caveat.
DEFAULT_PARAMS = {
    "m0": 1.0,          # effective vector density scaler (CALIBRATED per state)
    "b": 0.22,          # transmission efficiency mosquito -> human
    "c": 0.15,          # transmission efficiency human -> mosquito
    "sigma_h": 1 / 10.0,  # human latency rate (1/days)
    "gamma": 1 / 200.0,   # parasite-positive (infectious) clearance rate (1/days)
    "omega": 1 / 40.0,    # loss of clinical immunity -> re-susceptible (1/days)
    "k_half": 60.0,       # rainfall (mm) at half-max larval carrying capacity
}


# --- Temperature-dependent mosquito traits -----------------------------------
def briere(T, c, Tmin, Tmax):
    return np.clip(c * T * (T - Tmin) * np.sqrt(np.clip(Tmax - T, 0, None)), 0, None)


def biting_rate(T):
    return briere(T, 2.02e-4, 13.35, 40.08)


def mosquito_mortality(T):
    lifespan = np.clip(-0.0016 * T**2 + 0.054 * T + 0.45, 0.08, None) * 30
    return 1.0 / np.clip(lifespan, 3.0, None)


def eip_rate(T):
    return np.clip(briere(T, 7.0e-5, 14.3, 38.0), 1e-4, None)


def rain_carrying_capacity(rain_mm, k_half):
    return 1.5 * (rain_mm / (rain_mm + k_half))


# --- Coupled dynamics --------------------------------------------------------
def rhs(t, y, forcing, p):
    Sh, Eh, Ih, Rh, Sv, Ev, Iv = y
    Nh = Sh + Eh + Ih + Rh
    T = forcing["temp"](t)
    rain = forcing["rain"](t)

    a = biting_rate(T)
    muv = mosquito_mortality(T)
    n = eip_rate(T)
    K = rain_carrying_capacity(rain, p["k_half"])
    Nv = p["m0"] * K * Nh
    emergence = muv * Nv
    m = Nv / max(Nh, 1e-6)

    lam_h = m * a * p["b"] * (Iv / max(Nv, 1e-6))
    lam_v = a * p["c"] * (Ih / max(Nh, 1e-6))

    dSh = -lam_h * Sh + p["omega"] * Rh
    dEh = lam_h * Sh - p["sigma_h"] * Eh
    dIh = p["sigma_h"] * Eh - p["gamma"] * Ih
    dRh = p["gamma"] * Ih - p["omega"] * Rh
    dSv = emergence - lam_v * Sv - muv * Sv
    dEv = lam_v * Sv - (n + muv) * Ev
    dIv = n * Ev - muv * Iv
    return [dSh, dEh, dIh, dRh, dSv, dEv, dIv]


def monthly_interpolator(values12):
    md = np.array([15 + 30 * i for i in range(12)], dtype=float)
    ext_x = np.concatenate(([md[-1] - 365], md, [md[0] + 365]))
    ext_y = np.concatenate(([values12[-1]], values12, [values12[0]]))
    return lambda t: np.interp(t % 365, ext_x, ext_y)


def _forcing(state):
    clim = pd.read_csv(CLIM)
    s = clim[clim["state"] == state].sort_values("month")
    if s.empty:
        raise SystemExit(f"No climatology for {state}. Run src/fetch_climate.py.")
    return {"temp": monthly_interpolator(s["tavg_c"].to_numpy()),
            "rain": monthly_interpolator(s["precip_mm"].to_numpy())}


def simulate(state, params=None, years=6):
    p = {**DEFAULT_PARAMS, **(params or {})}
    forcing = _forcing(state)
    y0 = [0.6, 0, 0.1, 0.3, 7.0, 0.2, 0.1]
    t_end = 365 * years
    sol = solve_ivp(rhs, [0, t_end], y0, args=(forcing, p), max_step=6,
                    dense_output=True, rtol=1e-6, atol=1e-8)
    t = np.linspace(t_end - 365, t_end, 366)
    Y = sol.sol(t)
    prev = Y[2] / (Y[0] + Y[1] + Y[2] + Y[3])
    return (t - (t_end - 365)), prev


def annual_prevalence(state, params=None, years=6):
    _, prev = simulate(state, params, years)
    return float(prev.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="Oyo")
    ap.add_argument("--m0", type=float, default=None)
    args = ap.parse_args()
    params = {"m0": args.m0} if args.m0 is not None else None
    day, prev = simulate(args.state, params)
    months = (day / 30.4).astype(int)
    monthly = pd.DataFrame({"m": months, "p": prev}).groupby("m")["p"].mean()
    print(f"Seasonal prevalence (Ih/Nh) for {args.state} "
          f"(m0={(params or DEFAULT_PARAMS)['m0']}):")
    for m, pv in monthly.items():
        print(f"  month {m+1:2d}: {pv*100:5.1f}%  {'#'*int(pv*100)}")
    print(f"\n  annual mean {prev.mean()*100:.1f}% | peak {prev.max()*100:.1f}% "
          f"| trough {prev.min()*100:.1f}%")


if __name__ == "__main__":
    main()
