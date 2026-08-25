#!/usr/bin/env python3
"""
Fetch daily Wikipedia pageviews for a list of topics/cities.

Great proxy for "what people are interested in" - free, official, no API key.
Docs: https://wikimedia.org/api/rest_v1/  (metrics/pageviews endpoint)

Usage:
    python scripts/fetch_wikipedia_pageviews.py \
        --start 20260101 --end 20260131 \
        --articles "New_York_City" "Chicago" "Tokyo" \
        --out data/wiki_pageviews.csv
"""
import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

REST = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
# A descriptive User-Agent is required by the Wikimedia API policy.
UA = "city-stats-channel/1.0 (contact: you@example.com)"


def fetch_article(project, article, start, end):
    art = urllib.parse.quote(article, safe="")
    url = f"{REST}/{project}/all-access/all-agents/{art}/daily/{start}/{end}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp).get("items", [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default="en.wikipedia")
    ap.add_argument("--start", required=True, help="YYYYMMDD")
    ap.add_argument("--end", required=True, help="YYYYMMDD")
    ap.add_argument("--articles", nargs="+", required=True,
                    help="Article titles with underscores, e.g. New_York_City")
    ap.add_argument("--out", default="data/wiki_pageviews.csv")
    args = ap.parse_args()

    out_rows = []
    for article in args.articles:
        try:
            items = fetch_article(args.project, article, args.start, args.end)
        except Exception as e:  # noqa: BLE001 - keep going on a bad title
            print(f"! {article}: {e}", file=sys.stderr)
            continue
        for it in items:
            out_rows.append({
                "article": it["article"],
                "date": it["timestamp"][:8],
                "views": it["views"],
            })
        print(f"  {article}: {len(items)} days", file=sys.stderr)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["article", "date", "views"])
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {len(out_rows)} rows -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
