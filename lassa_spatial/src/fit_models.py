"""First spatial regression models on currently-available covariates.

Exploratory only: these predictors are dominated by surveillance/detection
and geography. Ecological and socioeconomic covariates are pending data
access (see VARIABLES.md). Interpret as a detection-adjusted geographic
baseline, not a causal ecological model.

Pipeline: OLS + spatial diagnostics (LM-lag / LM-error) -> spatial lag and
spatial error ML models -> negative binomial GLM on the raw counts.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import statsmodels.api as sm
from libpysal.weights import Queen
from spreg import OLS, ML_Lag, ML_Error
from statsmodels.stats.outliers_influence import variance_inflation_factor
from common import PROCESSED, OUTPUTS

RNG = 2025


def vif_report(X: pd.DataFrame) -> pd.Series:
    Xc = sm.add_constant(X)
    return pd.Series(
        {c: variance_inflation_factor(Xc.values, i)
         for i, c in enumerate(Xc.columns) if c != "const"}).round(2)


def main() -> None:
    g = gpd.read_file(PROCESSED / "states.geojson")
    cov = pd.read_csv(PROCESSED / "covariates_available.csv")
    g = g.merge(cov, on="State").sort_values("State").reset_index(drop=True)

    g["log_conf"] = np.log1p(g["confirmed"])
    g["log_susp"] = np.log1p(g["suspected"])
    w = Queen.from_dataframe(g, ids=g["State"].tolist(), use_index=False)
    w.transform = "r"

    preds = ["log_susp", "dist_nearest_lab_km", "has_treatment_centre",
             "borders_hotspot", "centroid_lat", "centroid_lon"]
    X = g[preds].astype(float)
    y = g[["log_conf"]].values

    print("=== VIF (collinearity) ===")
    print(vif_report(X).to_string())

    names = preds
    ols = OLS(y, X.values, w=w, spat_diag=True, moran=True, name_x=names,
              name_y="log_conf", name_w="queen", name_ds="lassa")
    print("\n=== OLS with spatial diagnostics ===")
    print(f"R2 = {ols.r2:.3f}   adj-R2 = {ols.ar2:.3f}   n = {ols.n}")
    print("coef (var: beta, p):")
    for nm, b, p in zip(["CONST"] + names, ols.betas.flatten(),
                        [np.nan] + [t[1] for t in ols.t_stat[1:]]):
        print(f"  {nm:22s} {b:9.4f}   p={p:.4f}" if not np.isnan(p)
              else f"  {nm:22s} {b:9.4f}")
    print(f"Moran's I (resid) = {ols.moran_res[0]:.3f}  p={ols.moran_res[2]:.4f}")
    print(f"LM-lag   stat={ols.lm_lag[0]:.3f}  p={ols.lm_lag[1]:.4f}")
    print(f"LM-error stat={ols.lm_error[0]:.3f}  p={ols.lm_error[1]:.4f}")
    print(f"Robust LM-lag   p={ols.rlm_lag[1]:.4f}   "
          f"Robust LM-error p={ols.rlm_error[1]:.4f}")

    lag = ML_Lag(y, X.values, w=w, name_x=names, name_y="log_conf")
    err = ML_Error(y, X.values, w=w, name_x=names, name_y="log_conf")
    print(f"\n=== Spatial lag ML ===  rho={lag.rho:.3f}  "
          f"pseudo-R2={lag.pr2:.3f}  AIC={lag.aic:.1f}")
    print(f"=== Spatial error ML ===  lambda={err.lam:.3f}  "
          f"pseudo-R2={err.pr2:.3f}  AIC={err.aic:.1f}")
    print(f"OLS AIC (for comparison) = {ols.aic:.1f}")

    # Contrast model M2: geography/structure only (NO surveillance term) ---
    # shows how much of the raw spatial clustering is really a detection signal.
    preds2 = ["dist_nearest_lab_km", "has_treatment_centre", "borders_hotspot",
              "centroid_lat", "centroid_lon"]
    ols2 = OLS(y, g[preds2].astype(float).values, w=w, spat_diag=True,
               moran=True, name_x=preds2, name_y="log_conf")
    print("\n=== M2: geography only (no surveillance term) ===")
    print(f"R2 = {ols2.r2:.3f}   adj-R2 = {ols2.ar2:.3f}")
    print(f"Moran's I (resid) = {ols2.moran_res[0]:.3f}  p={ols2.moran_res[2]:.4f}"
          f"   -> residual spatial dependence BEFORE adjusting for detection")

    # Negative binomial on the raw counts (natural scale for overdispersed counts)
    Xnb = sm.add_constant(g[preds].astype(float))
    nb = sm.GLM(g["confirmed"], Xnb,
                family=sm.families.NegativeBinomial(alpha=1.0)).fit()
    print("\n=== Negative binomial GLM (count) ===")
    print(f"pseudo-R2 (CS) = {1 - np.exp((nb.llnull - nb.llf) * 2 / nb.nobs):.3f}"
          f"   deviance/df = {nb.deviance / nb.df_resid:.2f}")
    print(np.exp(nb.params).round(3).rename("IRR").to_string())

    g[["State", "confirmed", "log_conf"] + preds].to_csv(
        PROCESSED / "model_frame.csv", index=False)
    print(f"\nwrote {PROCESSED/'model_frame.csv'}")


if __name__ == "__main__":
    main()
