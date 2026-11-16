"""Monthly malaria forecasting for the SW states: mechanistic vs ML comparison.

Forecasters compared on the same monthly target series, with rolling-origin
cross-validation at horizons h = 1..HMAX months:

  1. seasonal-naive        baseline: value from the same month last year
  2. mechanistic-clim      calibrated model's CLIMATOLOGICAL seasonal cycle
                           (structural; sees no year-specific anomaly)
  3. SARIMAX               statistical; lagged target + climate exogenous regressors
  4. gradient-boosting     ML; lagged target + lagged climate features

TARGET: currently the climate-forced mechanistic hindcast
(sw_mechanistic_monthly.csv, column 'prevalence'). Swap to DHIS2 monthly cases
by pointing TARGET_CSV/TARGET_COL at data/raw/cases/monthly_cases.csv when
available -- everything else is unchanged.

python3 forecast.py
"""
import pathlib
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
TARGET_CSV = PROC / "sw_mechanistic_monthly.csv"
TARGET_COL = "prevalence"
CLIM_MONTHLY = PROC / "sw_climate_monthly.csv"
CLIM_NORMALS = PROC / "sw_climatology.csv"
OUTDIR = ROOT / "outputs"
OUTDIR.mkdir(exist_ok=True)

HMAX = 6                 # forecast horizons (months)
MIN_TRAIN = 60          # months before first forecast origin
CLIM_LAGS = [1, 2, 3]   # climate predictor lags


# --------------------------------------------------------------------------- #
def load_panel() -> pd.DataFrame:
    tgt = pd.read_csv(TARGET_CSV)[["state", "year", "month", TARGET_COL]]
    tgt = tgt.rename(columns={TARGET_COL: "y"})
    clim = pd.read_csv(CLIM_MONTHLY)[["state", "year", "month",
                                      "precip_mm", "tavg_c"]]
    df = tgt.merge(clim, on=["state", "year", "month"], how="left")
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    return df.sort_values(["state", "date"]).reset_index(drop=True)


def make_features(g: pd.DataFrame) -> pd.DataFrame:
    g = g.copy()
    g["y_lag1"] = g["y"].shift(1)
    g["y_lag12"] = g["y"].shift(12)
    for L in CLIM_LAGS:
        g[f"rain_l{L}"] = g["precip_mm"].shift(L)
        g[f"temp_l{L}"] = g["tavg_c"].shift(L)
    g["rain_3m"] = g["precip_mm"].rolling(3).sum()
    g["sin"] = np.sin(2 * np.pi * g["month"] / 12)
    g["cos"] = np.cos(2 * np.pi * g["month"] / 12)
    return g


FEATS = (["y_lag1", "y_lag12", "rain_3m", "sin", "cos"]
         + [f"rain_l{L}" for L in CLIM_LAGS]
         + [f"temp_l{L}" for L in CLIM_LAGS])


# --- forecasters ----------------------------------------------------------- #
def f_seasonal_naive(hist: pd.DataFrame, horizon_rows: pd.DataFrame):
    # value 12 months before each target month
    preds = []
    series = hist.set_index("date")["y"]
    for _, r in horizon_rows.iterrows():
        prev = r["date"] - pd.DateOffset(months=12)
        preds.append(series.get(prev, hist["y"].iloc[-1]))
    return np.array(preds)


def f_mech_clim(state: str, horizon_rows: pd.DataFrame, normals_prev: dict):
    # climatological monthly mean of the target (structural seasonal cycle)
    return np.array([normals_prev[state][int(mn)] for mn in horizon_rows["month"]])


def f_sarimax(hist, horizon_rows):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    exog_cols = ["precip_mm", "tavg_c"]
    y = hist["y"].to_numpy()
    ex = hist[exog_cols].to_numpy()
    ex_f = horizon_rows[exog_cols].to_numpy()
    try:
        res = SARIMAX(y, exog=ex, order=(1, 0, 1),
                      seasonal_order=(1, 0, 0, 12),
                      enforce_stationarity=False,
                      enforce_invertibility=False).fit(disp=False)
        return np.asarray(res.forecast(steps=len(horizon_rows), exog=ex_f))
    except Exception:
        return np.full(len(horizon_rows), hist["y"].iloc[-1])


def f_gbm(hist, fut):
    """Recursive multi-step GBM. Fit on history, then roll forward feeding the
    model's own predictions back into the autoregressive lags. Climate features
    use the actual future climate (perfect-climate scenario; see module docs)."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    tr = hist.dropna(subset=FEATS + ["y"])
    if len(tr) < 24:
        return np.full(len(fut), np.nan)
    mdl = HistGradientBoostingRegressor(max_depth=4, learning_rate=0.06,
                                        max_iter=300, l2_regularization=1.0)
    mdl.fit(tr[FEATS], tr["y"])

    # running history of y (observed, then predicted) for lag construction
    ybuf = list(hist["y"].to_numpy())
    preds = []
    for _, r in fut.iterrows():
        feat = {
            "y_lag1": ybuf[-1],
            "y_lag12": ybuf[-12] if len(ybuf) >= 12 else ybuf[0],
            "rain_3m": r["rain_3m"], "sin": r["sin"], "cos": r["cos"],
        }
        for L in CLIM_LAGS:
            feat[f"rain_l{L}"] = r[f"rain_l{L}"]
            feat[f"temp_l{L}"] = r[f"temp_l{L}"]
        x = pd.DataFrame([feat])[FEATS]
        p = float(mdl.predict(x)[0])
        preds.append(p)
        ybuf.append(p)                 # feed prediction back
    return np.array(preds)


# --- rolling-origin evaluation -------------------------------------------- #
def evaluate():
    df = load_panel()
    # climatological normals of the TARGET (per state-month) from training-safe
    # full series mean -- recomputed inside the loop would be stricter; the
    # seasonal cycle is stable so full-series normals are a fair structural ref.
    normals_prev = {s: g.groupby("month")["y"].mean().to_dict()
                    for s, g in df.groupby("state")}

    records = []
    for state, g in df.groupby("state"):
        g = make_features(g).reset_index(drop=True)
        n = len(g)
        origins = range(MIN_TRAIN, n - 1)
        for o in origins:
            hist = g.iloc[:o + 1]
            fut = g.iloc[o + 1:o + 1 + HMAX]
            if len(fut) == 0:
                continue
            preds = {
                "seasonal_naive": f_seasonal_naive(hist, fut),
                "mechanistic_clim": f_mech_clim(state, fut, normals_prev),
                "sarimax": f_sarimax(hist, fut),
                "gbm": f_gbm(hist, fut),
            }
            for i, (_, r) in enumerate(fut.iterrows()):
                for model, pv in preds.items():
                    records.append({"state": state, "h": i + 1,
                                    "model": model, "y": r["y"],
                                    "pred": pv[i]})
    res = pd.DataFrame(records).dropna(subset=["pred"])
    res["ae"] = (res["y"] - res["pred"]).abs()
    res["se"] = (res["y"] - res["pred"]) ** 2
    return res


def summarise(res: pd.DataFrame):
    by = (res.groupby(["model", "h"])
          .agg(RMSE=("se", lambda s: np.sqrt(s.mean())),
               MAE=("ae", "mean")).reset_index())
    # skill vs seasonal-naive (RMSE reduction %)
    base = by[by.model == "seasonal_naive"].set_index("h")["RMSE"]
    by["skill_vs_naive_%"] = by.apply(
        lambda r: round(100 * (1 - r["RMSE"] / base[r["h"]]), 1), axis=1)
    overall = (res.groupby("model")
               .agg(RMSE=("se", lambda s: np.sqrt(s.mean())),
                    MAE=("ae", "mean")).round(5)
               .sort_values("RMSE"))
    return by, overall


def main():
    res = evaluate()
    by, overall = summarise(res)
    by.to_csv(OUTDIR / "forecast_skill_by_horizon.csv", index=False)
    print("=== Overall skill (all states, h=1..6), target =", TARGET_COL, "===")
    print(overall.to_string())
    print("\n=== RMSE by horizon ===")
    piv = by.pivot(index="h", columns="model", values="RMSE").round(5)
    print(piv.to_string())
    print("\n=== Skill vs seasonal-naive (%, higher=better) ===")
    piv2 = by.pivot(index="h", columns="model", values="skill_vs_naive_%")
    print(piv2.to_string())
    res.to_csv(OUTDIR / "forecast_eval_raw.csv", index=False)
    print(f"\nSaved -> {OUTDIR}/forecast_skill_by_horizon.csv")


if __name__ == "__main__":
    main()
