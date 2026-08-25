#!/usr/bin/env python3
"""
Fetch Google Trends "interest over time" for a set of search terms.

Uses the community `pytrends` client (pip install pytrends). This is the
engine for "what people search for" content - trends by term, over time, and
by US metro/region.

Usage:
    pip install pytrends
    python scripts/fetch_google_trends.py \
        --terms "cost of living" "moving to Texas" "remote jobs" \
        --timeframe "today 12-m" --geo US \
        --out data/google_trends.csv

Notes:
- Max 5 terms per request (Google limit). The script batches automatically.
- Google rate-limits aggressively; add --sleep to slow down if you get 429s.
- For interest BY city/region instead of over time, see interest_by_region()
  in the pytrends docs.
"""
import argparse
import csv
import os
import sys
import time


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--terms", nargs="+", required=True)
    ap.add_argument("--timeframe", default="today 12-m")
    ap.add_argument("--geo", default="US")
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--out", default="data/google_trends.csv")
    args = ap.parse_args()

    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("Missing dependency. Run: pip install pytrends", file=sys.stderr)
        return 1

    pytrends = TrendReq(hl="en-US", tz=360)
    frames = []
    # Batch terms in groups of 5 (Google's per-request cap).
    for i in range(0, len(args.terms), 5):
        batch = args.terms[i:i + 5]
        pytrends.build_payload(batch, timeframe=args.timeframe, geo=args.geo)
        df = pytrends.interest_over_time()
        if not df.empty:
            frames.append(df.drop(columns=[c for c in ("isPartial",) if c in df]))
        time.sleep(args.sleep)

    if not frames:
        print("No data returned.", file=sys.stderr)
        return 1

    import pandas as pd
    merged = pd.concat(frames, axis=1)
    merged.index.name = "date"

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    merged.to_csv(args.out)
    print(f"Wrote {len(merged)} rows x {merged.shape[1]} terms -> {args.out}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
