"""Full spatial/epidemiological models with reservoir, poverty, density,
health-system and geography covariates.

Two outcomes:
  (1) INCIDENCE  - confirmed cases with a log(population) offset, negative
      binomial. The standard count model for disease rates.
  (2) TEST POSITIVITY - confirmed/suspected, a partially detection-robust
      signal of true LASV circulation (conditions on being investigated).

Continuous predictors are z-standardised so NB coefficients read as
incidence-rate ratios per 1 SD. n=37 -> deliberately few predictors.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from libpysal.weights import Queen
from esda.moran import Moran
from spreg import OLS, ML_Lag, ML_Error
from common import PROCESSED

RNG = 2025
PREDS = ["mpi", "log_popdens", "gbif_mnatalensis_n", "facilities_per_100k",
         "centroid_lat", "dist_nearest_lab_km", "log_suspected"]


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


def main() -> None:
    g = gpd.read_file(PROCESSED / "master_state.geojson").sort_values(
        "State").reset_index(drop=True)
    for c in PREDS:
        g[f"z_{c}"] = z(g[c].astype(float))
    zp = [f"z_{c}" for c in PREDS]

    w = Queen.from_dataframe(g, ids=g["State"].tolist(), use_index=False)
    w.transform = "r"

    # Spatial autocorrelation of the incidence outcome
    g["log_inc"] = np.log1p(g["incidence_per100k"])
    np.random.seed(RNG)
    mi = Moran(g["log_inc"].values, w, permutations=9999)
    print(f"Moran's I log-incidence = {mi.I:.3f} (p={mi.p_sim:.4f})")

    # (1) Negative binomial incidence model, dispersion (alpha) ESTIMATED
    # (NB2 via exposure=population). Estimating alpha gives honest SEs/CIs.
    X = sm.add_constant(g[zp].astype(float))
    nb = sm.NegativeBinomial(g["confirmed"], X,
                             exposure=g["population"].values).fit(disp=0, maxiter=200)
    ci = nb.conf_int()
    irr = pd.DataFrame({
        "IRR": np.exp(nb.params), "p": nb.pvalues,
        "ci_lo": np.exp(ci[0]), "ci_hi": np.exp(ci[1])}).round(3)
    print("\n=== (1) NB2 incidence (IRR per 1 SD; exposure=pop) ===")
    print(f"alpha = {nb.params.get('alpha', float('nan')):.3f}   "
          f"McFadden R2 = {1 - nb.llf/nb.llnull:.3f}   AIC = {nb.aic:.1f}")
    print(irr.to_string())

    # OLS on log-incidence + spatial diagnostics
    ols = OLS(g[["log_inc"]].values, g[zp].astype(float).values, w=w,
              spat_diag=True, moran=True, name_x=PREDS, name_y="log_inc")
    print(f"\n=== OLS log-incidence ===  R2={ols.r2:.3f} adjR2={ols.ar2:.3f}")
    print(f"resid Moran's I={ols.moran_res[0]:.3f} (p={ols.moran_res[2]:.4f}); "
          f"LM-lag p={ols.lm_lag[1]:.3f}; LM-error p={ols.lm_error[1]:.3f}")
    for nm, b, t in zip(PREDS, ols.betas.flatten()[1:], ols.t_stat[1:]):
        print(f"  {nm:22s} beta={b:8.4f}  p={t[1]:.4f}")

    # (1b) Ecological/SES-only NB incidence (NO surveillance proxy, which is a
    # mediator/collider of disease). Fewer predictors for n=37.
    eco = ["mpi", "log_popdens", "gbif_mnatalensis_n", "centroid_lat"]
    zeco = [f"z_{c}" for c in eco]
    Xe = sm.add_constant(g[zeco].astype(float))
    nbe = sm.NegativeBinomial(g["confirmed"], Xe,
                              exposure=g["population"].values).fit(disp=0, maxiter=200)
    cie = nbe.conf_int()
    irre = pd.DataFrame({"IRR": np.exp(nbe.params), "p": nbe.pvalues,
                         "ci_lo": np.exp(cie[0]), "ci_hi": np.exp(cie[1])}).round(3)
    print("\n=== (1b) NB2 incidence, ECOLOGICAL/SES only (no surveillance) ===")
    print(f"alpha = {nbe.params.get('alpha', float('nan')):.3f}")
    print(irre.to_string())

    # (2) Test-positivity (detection-robust) via OLS on logit-ish fraction
    g["pos_frac"] = (g["confirmed"] / g["suspected"]).clip(1e-3, 0.999)
    g["logit_pos"] = np.log(g["pos_frac"] / (1 - g["pos_frac"]))
    posm = smf.ols("logit_pos ~ " + " + ".join(zp), data=g).fit()
    print("\n=== (2) Test-positivity (logit) OLS ===  R2=%.3f" % posm.rsquared)
    print(posm.params.round(3).to_string())
    print("p-values:")
    print(posm.pvalues.round(4).to_string())
    np.random.seed(RNG)
    mip = Moran(g["logit_pos"].values, w, permutations=9999)
    print(f"Moran's I logit-positivity = {mip.I:.3f} (p={mip.p_sim:.4f})")


if __name__ == "__main__":
    main()
