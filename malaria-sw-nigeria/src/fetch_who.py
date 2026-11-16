"""Fetch WHO Global Health Observatory malaria indicators for Nigeria.

National, annual. Context layer (trend) for the SW-state study.
Run with -I to avoid importing local shadowing modules:  python3 -I src/fetch_who.py
"""
import json
import pathlib
import urllib.request

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw" / "who"
OUT.mkdir(parents=True, exist_ok=True)

# Indicator code -> friendly name
INDICATORS = {
    "MALARIA_EST_INCIDENCE": "est_incidence_per_1000_at_risk",
    "MALARIA_EST_CASES": "est_cases",
    "MALARIA_EST_DEATHS": "est_deaths",
    "MALARIA_ITN_USE": "itn_use_pct",
    "MALARIA_CONF_CASES": "confirmed_cases_reported",
}
BASE = "https://ghoapi.azureedge.net/api/{code}?$filter=SpatialDim%20eq%20'NGA'"


def fetch(code: str) -> list[dict]:
    url = BASE.format(code=code)
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)["value"]
    rows = []
    for rec in data:
        if rec.get("NumericValue") is None:
            continue
        rows.append({"year": int(rec["TimeDim"]), "value": rec["NumericValue"]})
    return sorted(rows, key=lambda d: d["year"])


def main() -> None:
    combined = {}
    for code, name in INDICATORS.items():
        try:
            rows = fetch(code)
            (OUT / f"{name}.json").write_text(json.dumps(rows, indent=2))
            combined[name] = {r["year"]: r["value"] for r in rows}
            print(f"{name}: {len(rows)} yearly points "
                  f"({rows[0]['year']}-{rows[-1]['year']})" if rows else f"{name}: empty")
        except Exception as e:  # noqa: BLE001
            print(f"{name}: FAILED ({e})")
    (OUT / "who_nigeria_combined.json").write_text(json.dumps(combined, indent=2))
    print(f"\nSaved -> {OUT}")


if __name__ == "__main__":
    main()
