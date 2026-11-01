"""Spatial autocorrelation EDA on the Lassa outcome.

Global Moran's I + Local Moran (LISA) on log(confirmed+1) using queen
contiguity. Produces a choropleth + LISA cluster map. This step decides
whether spatial regression is warranted over plain OLS.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from common import PROCESSED, OUTPUTS

RNG = 2025


def main() -> None:
    g = gpd.read_file(PROCESSED / "states.geojson")
    out = pd.read_csv(PROCESSED / "outcome_state.csv")
    g = g.merge(out, on="State")

    g["log_conf"] = np.log1p(g["confirmed"])
    w = Queen.from_dataframe(g, ids=g["State"].tolist(), use_index=False)
    w.transform = "r"
    y = g["log_conf"].values

    np.random.seed(RNG)
    mi = Moran(y, w, permutations=9999)
    print(f"Global Moran's I (log confirmed) = {mi.I:.3f}  "
          f"p(perm) = {mi.p_sim:.4f}  z = {mi.z_sim:.2f}")

    lisa = Moran_Local(y, w, permutations=9999)
    labels = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
    g["lisa_q"] = lisa.q
    g["lisa_sig"] = lisa.p_sim < 0.05
    g["lisa_cluster"] = np.where(g["lisa_sig"],
                                 [labels[q] for q in lisa.q], "ns")
    print("\nSignificant local clusters (p<0.05):")
    print(g.loc[g["lisa_sig"], ["State", "confirmed", "lisa_cluster"]]
          .sort_values("confirmed", ascending=False).to_string(index=False))

    # --- maps ---
    fig, ax = plt.subplots(1, 2, figsize=(15, 7))
    g.plot(column="confirmed", scheme="quantiles", k=6, cmap="OrRd",
           legend=True, edgecolor="0.5", linewidth=0.4, ax=ax[0],
           legend_kwds={"title": "Confirmed (cum.)", "loc": "lower left"})
    ax[0].set_title("Lassa fever confirmed cases, 2020-2026 (cumulative)")
    ax[0].axis("off")

    cmap = {"High-High": "#b2182b", "Low-Low": "#2166ac",
            "Low-High": "#92c5de", "High-Low": "#f4a582", "ns": "#efefef"}
    for cl, col in cmap.items():
        sub = g[g["lisa_cluster"] == cl]
        if len(sub):
            sub.plot(ax=ax[1], color=col, edgecolor="0.5", linewidth=0.4,
                     label=cl)
    ax[1].set_title(f"LISA clusters (Moran's I={mi.I:.2f}, p={mi.p_sim:.3f})")
    ax[1].legend(loc="lower left", fontsize=8)
    ax[1].axis("off")
    fig.tight_layout()
    dest = OUTPUTS / "spatial_eda_maps.png"
    fig.savefig(dest, dpi=140, bbox_inches="tight")
    print(f"\nwrote {dest}")

    g[["State", "confirmed", "log_conf", "lisa_cluster", "lisa_sig"]].to_csv(
        PROCESSED / "lisa_results.csv", index=False)


if __name__ == "__main__":
    main()
