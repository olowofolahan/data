"""Visualise the mechanistic calibration: model vs MAP PfPR, and seasonal curves."""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import climate_seir as m

ROOT = pathlib.Path(__file__).resolve().parents[2]
PARAMS = pathlib.Path(__file__).resolve().parent / "calibrated_params.csv"
OUTDIR = ROOT / "outputs"
OUTDIR.mkdir(exist_ok=True)

# colourblind-safe (Okabe-Ito)
COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4C9"]


def main() -> None:
    cal = pd.read_csv(PARAMS).sort_values("state").reset_index(drop=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    # Panel 1: calibrated model all-age prevalence vs MAP target (with 95% CrI)
    x = cal["target_allage"]
    y = cal["model_prev"]
    lci = cal["target_allage"] * (cal["pfpr_lci"] / cal["map_pfpr_2_10"])
    uci = cal["target_allage"] * (cal["pfpr_uci"] / cal["map_pfpr_2_10"])
    ax1.plot([0, 0.6], [0, 0.6], ls="--", c="grey", lw=1, zorder=1)
    ax1.errorbar(x, y, xerr=[x - lci, uci - x], fmt="none", ecolor="lightgrey",
                 elinewidth=2, zorder=2)
    for i, r in cal.iterrows():
        ax1.scatter(r["target_allage"], r["model_prev"], s=90, color=COLORS[i],
                    zorder=3, label=r["state"])
        ax1.annotate(r["state"], (r["target_allage"], r["model_prev"]),
                     textcoords="offset points", xytext=(7, 4), fontsize=9)
    ax1.set_xlabel("MAP target, all-age (= 0.83 × PfPR$_{2-10}$), 95% CrI")
    ax1.set_ylabel("Calibrated model annual-mean prevalence")
    ax1.set_title("A. Mechanistic calibration vs MAP")
    ax1.set_xlim(0, 0.6); ax1.set_ylim(0, 0.6)
    ax1.set_aspect("equal"); ax1.grid(alpha=0.2)

    # Panel 2: calibrated seasonal prevalence curves per state
    for i, r in cal.iterrows():
        day, prev = m.simulate(r["state"], {"m0": r["fitted_m0"]}, years=8)
        ax2.plot(day / 30.4 + 1, prev * 100, color=COLORS[i], lw=2,
                 label=f"{r['state']} (m0={r['fitted_m0']:.2f})")
    ax2.set_xlabel("Month"); ax2.set_ylabel("Prevalence (%)")
    ax2.set_title("B. Calibrated seasonal transmission (climate-forced)")
    ax2.set_xlim(1, 12); ax2.set_xticks(range(1, 13))
    ax2.grid(alpha=0.2); ax2.legend(fontsize=8, loc="upper left")

    fig.suptitle("SW Nigeria malaria: climate-forced mechanistic model "
                 "calibrated to Malaria Atlas Project PfPR (release 202406)",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    out = OUTDIR / "calibration.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
