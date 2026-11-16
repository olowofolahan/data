"""Calibrate the climate-forced mechanistic model to MAP PfPR, per state.

For each SW state we fit the baseline vector density m0 so the model's annual
mean prevalence matches the MAP PfPR point estimate. Climate forcing sets the
seasonal shape and relative differences between states; m0 sets transmission
intensity (level). Lagos should calibrate to a markedly lower m0 (urban).

Age note: MAP PfPR is standardised to ages 2-10. Model prevalence is all-age.
We convert PfPR(2-10) -> all-age with a fixed factor (AGE_FACTOR); the default
0.83 is a pragmatic constant (Smith et al. 2007 give a prevalence-dependent
relationship -- refine later). Calibration target = AGE_FACTOR * PfPR.

python3 -I models/mechanistic/calibrate.py
"""
import pathlib

import pandas as pd
from scipy.optimize import brentq

import climate_seir as m

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGETS = ROOT / "data" / "processed" / "sw_map_pfpr.csv"
OUT = pathlib.Path(__file__).resolve().parent / "calibrated_params.csv"

AGE_FACTOR = 0.83          # PfPR(2-10) -> all-age prevalence (approx)
M0_BOUNDS = (0.05, 20.0)
SPINUP_YEARS = 8


def fit_state(state: str, target_allage: float) -> dict:
    def resid(m0):
        return m.annual_prevalence(state, {"m0": m0}, years=SPINUP_YEARS) - target_allage
    lo, hi = M0_BOUNDS
    r_lo, r_hi = resid(lo), resid(hi)
    if r_lo > 0:            # even minimum m0 overshoots target
        m0 = lo
    elif r_hi < 0:         # cannot reach target even at max density
        m0 = hi
    else:
        m0 = brentq(resid, lo, hi, xtol=1e-3, rtol=1e-4, maxiter=60)
    model_prev = m.annual_prevalence(state, {"m0": m0}, years=SPINUP_YEARS)
    return {"m0": round(m0, 3), "model_prev": round(model_prev, 4)}


def main() -> None:
    tgt = pd.read_csv(TARGETS)
    rows = []
    for _, r in tgt.iterrows():
        state = r["state"]
        target_allage = AGE_FACTOR * r["pfpr"]
        fit = fit_state(state, target_allage)
        rows.append({
            "state": state,
            "map_pfpr_2_10": round(r["pfpr"], 4),
            "target_allage": round(target_allage, 4),
            "fitted_m0": fit["m0"],
            "model_prev": fit["model_prev"],
            "residual": round(fit["model_prev"] - target_allage, 4),
            "pfpr_lci": r.get("pfpr_lci"), "pfpr_uci": r.get("pfpr_uci"),
        })
        print(f"{state:7s} PfPR={r['pfpr']:.3f} -> target(all-age)={target_allage:.3f} "
              f"| fitted m0={fit['m0']:7.2f} | model={fit['model_prev']:.3f}")
    df = pd.DataFrame(rows).sort_values("fitted_m0").reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"\nSaved -> {OUT}")
    print("\nTransmission-intensity ranking (fitted m0, low=urban/low transmission):")
    for _, r in df.iterrows():
        print(f"  {r['state']:7s} m0={r['fitted_m0']:7.2f}  PfPR={r['map_pfpr_2_10']:.2f}")


if __name__ == "__main__":
    main()
