# City Data Pipeline — a steady stream for a statistical-data channel

Free, real, reproducible data on **cities**, **what people search for**, and
**business activity by location**. The idea: don't collect a one-time dump —
run a script and regenerate fresh data whenever you need a new topic.

## What's here

```
data/
  us_top_cities_starter.csv   # ready now: 40 largest US cities, 2020 Census pop
scripts/
  fetch_census_cities.py      # city stats: pop, income, rent, home value, age
  fetch_wikipedia_pageviews.py# "what people are interested in" (daily views)
  fetch_google_trends.py      # "what people search for" (interest over time)
  requirements.txt
docs/
  SOURCES.md                  # full catalog of free data sources + content ideas
```

## Quick start

```bash
# 1. City statistics from the US Census (no key needed for light use)
python scripts/fetch_census_cities.py --year 2023 --top 200 \
    --out data/us_cities_acs.csv

# 2. Wikipedia pageviews — interest in any set of topics/cities
python scripts/fetch_wikipedia_pageviews.py --start 20260101 --end 20260131 \
    --articles New_York_City Chicago Tokyo Lagos --out data/wiki_pageviews.csv

# 3. Google Trends — search interest (needs: pip install -r scripts/requirements.txt)
python scripts/fetch_google_trends.py \
    --terms "cost of living" "moving to Texas" "remote jobs" \
    --timeframe "today 12-m" --geo US --out data/google_trends.csv
```

> **Note on running these here:** this Claude Code cloud sandbox blocks outbound
> API calls, so the scripts are meant to run in a normal-internet environment —
> your laptop, Google Colab, or a scheduled GitHub Action. They only need
> Python 3.11+ (Google Trends also needs `pytrends` + `pandas`).

## Get a free Census API key (optional but recommended)

The large `place:*` query runs faster and without the 500-calls/day cap once you
set a key: https://api.census.gov/data/key_signup.html

```bash
export CENSUS_API_KEY=your_key_here
```

## Automate it (never run out)

Add a GitHub Action on a weekly cron that runs the scripts and commits the CSVs,
so fresh data lands in `data/` on a schedule. Ask and I'll write the workflow.

See **docs/SOURCES.md** for the full list of free sources and 20+ content ideas.
