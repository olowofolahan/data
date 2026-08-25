# Free data sources for a city / search-trends / business-data channel

Everything below is free and, where noted, scriptable. Grouped by your three
themes. Endpoints are given so you (or a script) can pull fresh data anytime.

---

## 1. What people search for / are interested in

| Source | What you get | Access |
|---|---|---|
| **Google Trends** | Search interest over time, by US metro, rising queries | `pytrends` (see `scripts/fetch_google_trends.py`) |
| **Wikipedia Pageviews** | Daily views for any topic/city — a clean interest proxy | REST API, no key (`scripts/fetch_wikipedia_pageviews.py`) |
| **Reddit** | Trending posts in city subreddits (r/nyc, r/chicago, …) | Reddit API / PRAW |
| **Google Keyword Planner** | Search volume for keywords | Free Google Ads account |
| **Exploding Topics** | Rising/emerging search terms | Web (some free) |

**Content angles:** "What each US state Googled most this month" • "Wikipedia's
most-read cities of the year" • "Search interest in 'moving to ___' by state."

---

## 2. City data (demographics, housing, cost, crime, jobs)

| Source | What you get | Access |
|---|---|---|
| **US Census Bureau — ACS** | Population, income, rent, home value, age, commute, education by city/metro | API, free key (`scripts/fetch_census_cities.py`) |
| **Bureau of Labor Statistics (BLS)** | Employment, wages, unemployment by metro | Public API, free key |
| **Zillow Research** | Home prices & rents by metro (ZHVI/ZORI) | Free CSV downloads |
| **FBI Crime Data Explorer** | Crime rates by city/agency | API, free key |
| **City open-data portals** | Millions of rows: 311, permits, transit, crime | NYC Open Data, Chicago, LA, Austin, London Datastore, etc. |
| **Numbeo** | Cost of living, quality of life index | Web / API |
| **World Bank / OECD / Eurostat** | Global city & country indicators | Free APIs |

**Content angles:** "Cheapest vs. priciest big cities to rent in" • "Which
metros gained/lost the most people" • "Income vs. rent — where does a paycheck
go furthest?"

---

## 3. Business data by city

| Source | What you get | Access |
|---|---|---|
| **Census County Business Patterns** | # of businesses & employment by industry & area | Census API |
| **BLS QCEW** | Establishment counts, wages by county & industry | Public API |
| **Yelp Fusion API** | Businesses, categories, ratings per city | Free tier, key |
| **Google Places API** | Business listings, ratings, density | Paid, has free credits |
| **OpenCorporates** | Company registrations | API |
| **SBA / data.gov** | Small-business & federal datasets | Free |

**Content angles:** "Coffee shops per capita by city" • "Where new businesses
are opening fastest" • "Restaurant density vs. population."

---

## Reliability notes for a data channel

- **Cite the source and year on every chart** (e.g. "ACS 2023 5-year"). Mixing
  vintages is the #1 way stats content gets called out.
- **City proper ≠ metro area.** Census "place" = city limits; "CBSA/metro" =
  the wider region. Pick one and label it.
- **Prefer official APIs over scraped article numbers** — the scripts here pull
  from the primary source so your figures are defensible.
