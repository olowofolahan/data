"""Visualise the mechanistic-vs-ML forecast comparison."""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "outputs"
BYH = OUTDIR / "forecast_skill_by_horizon.csv"

LABELS = {"seasonal_naive": "Seasonal-naive", "mechanistic_clim": "Mechanistic (clim.)",
          "sarimax": "SARIMAX", "gbm": "Gradient boosting"}
COLORS = {"seasonal_naive": "#999999", "mechanistic_clim": "#0072B2",
          "sarimax": "#E69F00", "gbm": "#009E73"}


def main():
    by = pd.read_csv(BYH)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for mdl, g in by.groupby("model"):
        g = g.sort_values("h")
        ax1.plot(g["h"], g["RMSE"], marker="o", color=COLORS.get(mdl),
                 label=LABELS.get(mdl, mdl), lw=2)
    ax1.set_xlabel("Forecast horizon (months)"); ax1.set_ylabel("RMSE (prevalence)")
    ax1.set_title("A. Forecast error by horizon"); ax1.grid(alpha=0.2)
    ax1.legend(fontsize=9)

    for mdl, g in by.groupby("model"):
        if mdl == "seasonal_naive":
            continue
        g = g.sort_values("h")
        ax2.plot(g["h"], g["skill_vs_naive_%"], marker="o", color=COLORS.get(mdl),
                 label=LABELS.get(mdl, mdl), lw=2)
    ax2.axhline(0, color="#999999", ls="--", lw=1, label="Seasonal-naive")
    ax2.set_xlabel("Forecast horizon (months)")
    ax2.set_ylabel("Skill vs seasonal-naive (% RMSE reduction)")
    ax2.set_title("B. Skill over the seasonal-naive baseline")
    ax2.grid(alpha=0.2); ax2.legend(fontsize=9)

    fig.suptitle("SW Nigeria malaria forecasting: mechanistic vs ML "
                 "(rolling-origin CV; target = climate-forced mechanistic hindcast)",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    out = OUTDIR / "forecast_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
