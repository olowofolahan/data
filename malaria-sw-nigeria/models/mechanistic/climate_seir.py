"""Climate-forced malaria transmission model for a single state (STARTER).

Human SEIR coupled to mosquito SEI, Ross-Macdonald family, with mosquito
parameters driven by monthly temperature (thermal response) and rainfall
(larval carrying capacity). Forced by the WorldClim monthly climatology
produced by src/fetch_climate.py.

This is a documented starting point: parameters are literature defaults and
MUST be calibrated (to MAP annual PfPR now; to DHIS2 monthly cases when
available). It demonstrates the climate -> transmission linkage end to end.

Run:  python3 -I models/mechanistic/climate_seir.py --state Oyo
"""
import argparse
import pathlib

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLIM = ROOT / "data" / "processed" / "sw_climatology.csv"


# --- Temperature-dependent mosquito traits (Mordecai et al. 2013 style) -------
def briere(T, c, Tmin, Tmax):
    r = c * T * (T - Tmin) * np.sqrt(np.clip(Tmax - T, 0, None))
    return np.clip(r, 0, None)


def biting_rate(T):            # a(T), per day
    return briere(T, 2.02e-4, 13.35, 40.08)


def mosquito_mortality(T):     # mu(T), per day (inverse of lifespan)
    # parabolic lifespan peaking ~25C; floor keeps it positive
    lifespan = np.clip(-0.0016 * T**2 + 0.054 * T + 0.45, 0.08, None) * 30
    return 1.0 / np.clip(lifespan, 3.0, None)


def eip_rate(T):               # 1/EIP, parasite development in mosquito, per day
    return np.clip(briere(T, 7.0e-5, 14.3, 38.0), 1e-4, None)


def rain_carrying_capacity(rain_mm):
    """Relative mosquito carrying capacity from monthly rainfall (0..1.5)."""
    # saturating response; too little rain -> few breeding sites
    return 1.5 * (rain_mm / (rain_mm + 60.0))


# --- Coupled human-mosquito dynamics -----------------------------------------
def rhs(t, y, forcing):
    Sh, Eh, Ih, Rh, Sv, Ev, Iv = y
    Nh = Sh + Eh + Ih + Rh

    T = forcing["temp"](t)
    rain = forcing["rain"](t)

    a = biting_rate(T)                 # bites per mosquito per day
    muv = mosquito_mortality(T)
    n = eip_rate(T)
    b, c = 0.55, 0.35                  # transmission efficiencies v->h, h->v
    sigma_h = 1 / 10.0                 # human latency (days^-1)
    gamma = 1 / 200.0                  # human recovery (days^-1)
    omega = 1 / 365.0                  # loss of immunity
    # mosquito emergence scaled by rainfall carrying capacity
    K = rain_carrying_capacity(rain)
    Nv = 8.0 * K * Nh                  # mosquitoes per human * K
    emergence = muv * Nv               # equilibrium emergence to sustain Nv

    m = Nv / max(Nh, 1e-6)
    lam_h = m * a * b * (Iv / max(Nv, 1e-6))     # force of infection on humans
    lam_v = a * c * (Ih / max(Nh, 1e-6))         # FOI on mosquitoes

    dSh = -lam_h * Sh + omega * Rh
    dEh = lam_h * Sh - sigma_h * Eh
    dIh = sigma_h * Eh - gamma * Ih
    dRh = gamma * Ih - omega * Rh
    dSv = emergence - lam_v * Sv - muv * Sv
    dEv = lam_v * Sv - (n + muv) * Ev
    dIv = n * Ev - muv * Iv
    return [dSh, dEh, dIh, dRh, dSv, dEv, dIv]


def monthly_interpolator(values12):
    """Periodic linear interpolation of 12 monthly values over day-of-year."""
    month_days = np.array([15 + 30 * i for i in range(12)], dtype=float)
    ext_x = np.concatenate(([month_days[-1] - 365], month_days, [month_days[0] + 365]))
    ext_y = np.concatenate(([values12[-1]], values12, [values12[0]]))
    return lambda t: np.interp(t % 365, ext_x, ext_y)


def run_state(state: str, years: int = 6):
    clim = pd.read_csv(CLIM)
    s = clim[clim["state"] == state].sort_values("month")
    if s.empty:
        raise SystemExit(f"No climatology for {state}. Run src/fetch_climate.py first.")
    temp = monthly_interpolator(s["tavg_c"].to_numpy())
    rain = monthly_interpolator(s["precip_mm"].to_numpy())
    forcing = {"temp": temp, "rain": rain}

    Nh = 1.0
    y0 = [0.6 * Nh, 0, 0.1 * Nh, 0.3 * Nh, 7.0 * Nh, 0.2 * Nh, 0.1 * Nh]
    t_end = 365 * years
    sol = solve_ivp(rhs, [0, t_end], y0, args=(forcing,), max_step=5,
                    dense_output=True, rtol=1e-6, atol=1e-8)
    t = np.linspace(t_end - 365, t_end, 366)     # last year (spun up)
    Y = sol.sol(t)
    prev = Y[2] / (Y[0] + Y[1] + Y[2] + Y[3])    # Ih / Nh
    return t - (t_end - 365), prev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="Oyo")
    args = ap.parse_args()
    day, prev = run_state(args.state)
    months = (day / 30.4).astype(int)
    df = pd.DataFrame({"month": months, "prevalence": prev})
    monthly = df.groupby("month")["prevalence"].mean()
    print(f"Simulated seasonal prevalence (Ih/Nh) for {args.state}:")
    for m, p in monthly.items():
        bar = "#" * int(p * 100)
        print(f"  month {m+1:2d}: {p*100:5.1f}%  {bar}")
    print(f"\n  annual mean prevalence: {prev.mean()*100:.1f}%  "
          f"(peak {prev.max()*100:.1f}% / trough {prev.min()*100:.1f}%)")
    print("  NOTE: uncalibrated literature parameters - calibrate to MAP/DHIS2.")


if __name__ == "__main__":
    main()
