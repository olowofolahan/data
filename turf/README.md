# Turf

A top-down browser crime-management sim built from the **Turf Game Design
Document**. Start broke in a city and climb from small-time hustler to kingpin
through jobs, crew, property and territory — in the spirit of Mob Wars, wrapped
in a life-sim clock.

**No build step, no install, no external assets.** Open `index.html` in any
browser (desktop or mobile) and play.

> Note: the real-time **Street mode** (top-down driving/shooting) was removed by
> request — the game is now the **Empire dashboard** only. Its weapons live on as
> the Arsenal (they boost fight strength), and the Pastor's born-again converts
> now visit you on the dashboard.

## Play

- **Locally:** double-click `index.html`, or serve the folder
  (`python3 -m http.server` then open `http://localhost:8000/`).
- **Deploy:** upload the `turf/` folder to any static host (Netlify, Vercel,
  Cloudflare Pages, GitHub Pages).

## What's implemented

One state store (`localStorage` save, with export/import codes) drives the
Empire dashboard.

- **Jobs** with tiers unlocked by rank, including the high-risk **Political
  thug** sabotage job — swing an election for your backer for a big payout, but
  it can **backfire** (a property is seized, Respect drops). Crew and low Heat
  improve the odds.
- **Crew** (4 roles, loyalty, wages, district assignment) — gift, **raise wages
  to boost loyalty**, or **fire** a member.
- **Properties** (buy/upgrade, timed income), **Districts** (0–100% control,
  takeover, and **turf wars** resolved with your strength), **Fight** (attack
  rival gangs).
- **Arsenal:** buy & equip melee (fists → bat → machete) and firearms (pistol →
  SMG → shotgun), unlocked by rank. The equipped weapon **adds to your strength**
  in fights and turf wars.
- **Friends:** add friends by email and **invite them by email** — the invite
  opens your own mail app with the message and game link ready (the list is saved
  on your device).
- **Born-again converts:** now and then a reformed gang member visits the
  dashboard to say they're **born again** and quotes a verse of Scripture (KJV).
  Bless them (eases Heat) or wave them off.
- **Energy:** the bar holds **100** and refills **40 per hour** (1 point every
  90s); jobs spend it.
- **Sim systems:** game clock with day/night (affects lighting, crowds, police,
  night-only jobs), Heat / Respect / Loyalty meters, energy & stamina regen over
  real time, **offline progress** ("While you were away"), **weekly upkeep**, and
  daily **random events**.
- **In-game ads:** a dashboard **banner** and **rewarded full-screen flyers**
  (closable after 2s, capped at 3 rewards/day, kept in the inventory) that turn
  up on the dashboard now and then. Paid ads come from an ad manifest; when none
  match the player's country/slot, an in-game **parody ad** is shown. Impression
  / view / click events are queued and batched (logged to the console until an
  endpoint is set). Premium turns the banner into parody.
- **Country packs:** the engine never changes between countries — each is a data
  pack. Two ship: **Lagos (Nigeria)** and **Fort Prairie (Canada)**, chosen on
  first launch (guessed from the browser).

## Where to tune things ("balance in data, not code")

Everything a designer tunes lives in [`js/data.js`](js/data.js):

- `COUNTRY_PACKS` — add a country by adding an entry (city, currency, price
  scale, districts, rivals, vehicles, shops, parody ads, NPC names/lines).
- `JOBS` (incl. the `special: "sabotage"` political-thug job), `PROPERTIES`,
  `CREW_ROLES`, `RANKS`, `EVENTS`, `WEAPONS`, `SCRIPTURES`.
- `ADS` — the ad manifest (the `ads.json` stand-in). Add booked ads here, or
  point `TURF.ads.endpoint` at a tracking URL.

## Files

| File | Role |
| --- | --- |
| `index.html` | shell + dashboard markup |
| `css/styles.css` | all styling, mobile layout, overlays |
| `js/data.js` | country packs, ads, jobs, props, crew, ranks (tuning) |
| `js/game.js` | state store, save/load, sim, ads, Empire dashboard, friends |
| `js/ui.js` | overlays (country select, flyers, upkeep, events, converts) |
| `js/main.js` | bootstrap + main loop |

## Not yet (v2, per the design doc)

Ad admin page + real tracking endpoint, cloud saves/accounts, more country
packs, real-money payments, and player-vs-player fights.

## Content & rating

All gangs, businesses and police forces are invented; cartoon violence only
(no blood/gore); illegal goods stay vague. Target rating: teen.
