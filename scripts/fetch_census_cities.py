#!/usr/bin/env python3
"""
Fetch city-level statistics from the US Census Bureau ACS 5-year API.

Pulls population, median household income, median gross rent, median home
value, and median age for every "place" (city/town) in the US, then keeps the
largest N by population and writes a clean CSV.

Source : https://www.census.gov/data/developers/data-sets/acs-5year.html
API key: optional for light use. Get a free one at
         https://api.census.gov/data/key_signup.html and set CENSUS_API_KEY.

Usage:
    python scripts/fetch_census_cities.py --year 2023 --top 200 \
        --out data/us_cities_acs.csv
"""
import argparse
import csv
import os
import sys
import urllib.parse
import urllib.request

# ACS detail-table variable codes -> friendly column names.
VARIABLES = {
    "B01003_001E": "population",
    "B19013_001E": "median_household_income",
    "B25064_001E": "median_gross_rent",
    "B25077_001E": "median_home_value",
    "B01002_001E": "median_age",
}


def fetch(year: int, api_key: str | None) -> list[list[str]]:
    base = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        "get": "NAME," + ",".join(VARIABLES),
        "for": "place:*",
        "in": "state:*",
    }
    if api_key:
        params["key"] = api_key
    url = base + "?" + urllib.parse.urlencode(params, safe=":*,")
    print(f"GET {url.split('?')[0]} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as resp:
        import json

        return json.load(resp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--year", type=int, default=2023, help="ACS 5-year vintage")
    ap.add_argument("--top", type=int, default=200, help="keep N largest cities")
    ap.add_argument("--out", default="data/us_cities_acs.csv")
    args = ap.parse_args()

    api_key = os.environ.get("CENSUS_API_KEY")
    rows = fetch(args.year, api_key)
    header, *data = rows

    # Map raw column order to our friendly names.
    idx = {name: header.index(code) for code, name in VARIABLES.items()}
    name_i = header.index("NAME")

    records = []
    for r in data:
        try:
            pop = int(r[idx["population"]])
        except (ValueError, TypeError):
            continue
        # Census uses large negative sentinels (e.g. -666666666) for "no data".
        def clean(v):
            try:
                n = float(v)
                return "" if n < 0 else (int(n) if n.is_integer() else n)
            except (ValueError, TypeError):
                return ""

        city_state = r[name_i]
        records.append(
            {
                "city_state": city_state,
                "population": pop,
                "median_household_income": clean(r[idx["median_household_income"]]),
                "median_gross_rent": clean(r[idx["median_gross_rent"]]),
                "median_home_value": clean(r[idx["median_home_value"]]),
                "median_age": clean(r[idx["median_age"]]),
                "acs_year": args.year,
            }
        )

    records.sort(key=lambda x: x["population"], reverse=True)
    records = records[: args.top]
    for i, rec in enumerate(records, 1):
        rec["rank"] = i

    fields = [
        "rank",
        "city_state",
        "population",
        "median_household_income",
        "median_gross_rent",
        "median_home_value",
        "median_age",
        "acs_year",
    ]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)

    print(f"Wrote {len(records)} rows -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
