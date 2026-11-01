"""Climate covariates: collinearity with the north-south gradient and a
parsimonious climate-based incidence model.

Shows that latitude, rainfall, rainfall/temperature seasonality and poverty
collapse onto a single gradient (PCA PC1), so they cannot be separated at the
state scale; the low-VIF model retains one gradient proxy (rainfall
seasonality) plus population density.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.api as sm
from numpy.linalg import svd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from common import PROCESSED

GRAD = ["centroid_lat", "precip_annual_mm", "precip_seasonality_cv",
        "temp_seasonality", "mpi"]


def main() -> None:
    g = gpd.read_file(PROCESSED / "master_state.geojson")
    g["log_popdens"] = np.log(g["pop_density_km2"])

    # VIFs for the gradient set + density
    cols = GRAD + ["log_popdens"]
    Z = (g[cols].astype(float) - g[cols].astype(float).mean()) / g[cols].astype(float).std(ddof=0)
    Xc = sm.add_constant(Z)
    print("VIF:")
    for i, c in enumerate(Xc.columns):
        if c == "const":
            continue
        print(f"  {c:24s} {variance_inflation_factor(Xc.values, i):6.1f}")

    # PCA of the gradient variables
    Zg = ((g[GRAD].astype(float) - g[GRAD].astype(float).mean())
          / g[GRAD].astype(float).std(ddof=0)).values
    _, S, _ = svd(Zg, full_matrices=False)
    ev = S**2 / (S**2).sum()
    print(f"\nPCA gradient set: PC1 = {100*ev[0]:.1f}%, PC2 = {100*ev[1]:.1f}%")

    # Parsimonious climate model
    pr = ["precip_seasonality_cv", "log_popdens", "gbif_mnatalensis_n"]
    for c in pr:
        g["z_" + c] = (g[c] - g[c].mean()) / g[c].std(ddof=0)
    X = sm.add_constant(g[["z_" + c for c in pr]].astype(float))
    m = sm.NegativeBinomial(g["confirmed"], X,
                            exposure=g["population"].values).fit(disp=0, maxiter=300)
    ci = m.conf_int()
    print(f"\nParsimonious climate NB  alpha={m.params.get('alpha', float('nan')):.2f}  "
          f"AIC={m.aic:.1f}")
    for t in m.params.index:
        if t == "alpha":
            continue
        print(f"  {t:26s} IRR={np.exp(m.params[t]):.3f} "
              f"[{np.exp(ci.loc[t,0]):.3f}, {np.exp(ci.loc[t,1]):.3f}] p={m.pvalues[t]:.4f}")


if __name__ == "__main__":
    main()
