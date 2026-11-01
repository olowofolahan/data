"""Bayesian hierarchical spatial model (Besag-York-Mollie) for Lassa incidence.

Negative binomial counts with a log-population offset, the parsimonious
low-collinearity fixed effects (rainfall seasonality + log population density),
and TWO area random effects:
  - a spatially structured ICAR effect (queen adjacency)
  - an unstructured iid effect
This is the disease-mapping standard spatial regression. It reports the
spatial fraction of residual variance and a smoothed residual spatial
relative-risk surface, and is compared with a non-spatial model by LOO.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import pymc as pm
import arviz as az
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from common import PROCESSED, OUTPUTS

SEED = 2025
FIXED = ["precip_seasonality_cv", "log_popdens"]


def adjacency(g):
    w = Queen.from_dataframe(g, ids=list(range(len(g))), use_index=False)
    n = len(g)
    A = np.zeros((n, n), int)
    for i, nbrs in w.neighbors.items():
        for j in nbrs:
            A[i, j] = 1
    return ((A + A.T) > 0).astype(int)


def build(g, A, spatial=True):
    y = g["confirmed"].values.astype(int)
    logpop = np.log(g["population"].values)
    X = np.column_stack([(g[c] - g[c].mean()) / g[c].std(ddof=0) for c in FIXED])
    with pm.Model() as m:
        b0 = pm.Normal("b0", 0, 5)
        beta = pm.Normal("beta", 0, 1, shape=X.shape[1])
        theta = pm.Normal("theta", 0, 1, shape=len(g))      # unstructured
        sig_t = pm.HalfNormal("sig_t", 1)
        eta = b0 + pm.math.dot(X, beta) + sig_t * theta + logpop
        if spatial:
            u = pm.ICAR("u", W=A)                            # structured
            sig_u = pm.HalfNormal("sig_u", 1)
            eta = eta + sig_u * u
        alpha = pm.HalfNormal("alpha", 5)                    # NB inverse-dispersion
        mu = pm.math.exp(eta)
        pm.NegativeBinomial("y", mu=mu, alpha=alpha, observed=y)
    return m


def main() -> None:
    g = gpd.read_file(PROCESSED / "master_state.geojson").sort_values(
        "State").reset_index(drop=True)
    g["log_popdens"] = np.log(g["pop_density_km2"])
    A = adjacency(g)

    with build(g, A, spatial=True):
        idata = pm.sample(1500, tune=2500, chains=4, cores=4,
                          target_accept=0.99, random_seed=SEED,
                          idata_kwargs={"log_likelihood": True}, progressbar=False)
    with build(g, A, spatial=False):
        idata0 = pm.sample(1500, tune=2500, chains=4, cores=4,
                           target_accept=0.99, random_seed=SEED,
                           idata_kwargs={"log_likelihood": True}, progressbar=False)

    post = idata.posterior
    # Fixed-effect IRRs
    beta = post["beta"].stack(s=("chain", "draw")).values  # (2, S)
    irr = np.exp(beta)
    print("=== BYM fixed effects (IRR per 1 SD) ===")
    for i, c in enumerate(FIXED):
        lo, hi = np.percentile(irr[i], [2.5, 97.5])
        pdir = (beta[i] < 0).mean()
        print(f"  {c:24s} IRR={np.exp(beta[i].mean()):.3f} "
              f"[{lo:.3f}, {hi:.3f}]  P(beta<0)={pdir:.3f}")

    # Spatial fraction: var(structured)/(var(structured)+var(unstructured)) per draw
    uu = (post["u"] * post["sig_u"]).stack(s=("chain", "draw")).values   # (n,S)
    tt = (post["theta"] * post["sig_t"]).stack(s=("chain", "draw")).values
    frac = uu.var(0) / (uu.var(0) + tt.var(0))
    print(f"\nSpatial fraction phi = {frac.mean():.3f} "
          f"[{np.percentile(frac,2.5):.3f}, {np.percentile(frac,97.5):.3f}]")
    summ = az.summary(idata, var_names=["b0", "beta", "sig_t", "sig_u", "alpha"])
    print(f"max R-hat (key params) = {summ['r_hat'].max():.3f}; "
          f"min ESS = {summ['ess_bulk'].min():.0f}")

    # Model comparison (LOO)
    cmp = az.compare({"BYM_spatial": idata, "non_spatial": idata0})
    print("\n=== LOO comparison ===")
    keep = [c for c in ["rank", "elpd_loo", "p_loo", "elpd_diff", "dse", "weight"]
            if c in cmp.columns]
    print(cmp[keep].to_string())

    # Smoothed residual spatial relative risk = exp(sig_u * u)
    rr = np.exp(uu).mean(1)
    g["spatial_RR"] = rr
    g[["State", "spatial_RR"]].to_csv(PROCESSED / "bym_spatial_rr.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.5, 7))
    g.plot(column="spatial_RR", scheme="quantiles", k=6, cmap="RdBu_r",
           legend=True, edgecolor="0.4", linewidth=0.4, ax=ax,
           legend_kwds={"title": "Residual spatial RR", "loc": "lower left"})
    ax.set_title("BYM residual spatial relative risk\n(after rainfall seasonality + population density)")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUTPUTS / "bym_spatial_rr.png", dpi=140, bbox_inches="tight")
    print(f"\nwrote {OUTPUTS/'bym_spatial_rr.png'}")
    idata.to_netcdf(str(PROCESSED / "bym_idata.nc"))


if __name__ == "__main__":
    main()
