# Turf

A top-down browser crime sim built from the **Turf Game Design Document**. Start
broke in a city and climb from small-time hustler to kingpin. It blends the
free-roaming street action of early top-down GTA with the jobs / crew / property
systems of Mob Wars, wrapped in a life-sim clock.

**No build step, no install, no external assets.** Open `index.html` in any
browser (desktop or mobile) and play. All art is drawn procedurally on a canvas.

## Play

- **Locally:** double-click `index.html`, or serve the folder
  (`python3 -m http.server` then open `http://localhost:8000/`).
- **Deploy:** upload the `turf/` folder to any static host (Netlify, Vercel,
  Cloudflare Pages, GitHub Pages).

### Controls (Street mode)
- **WASD / arrows** — move on foot or drive
- **E** — enter or steal the nearest car (pulling a driver out raises Heat)
- **Space** — attack
- Drive onto the coloured spots: **Safehouse** (green, heal + save),
  **Chop shop** (orange, sell a car), **Respray** (blue, shake Heat),
  **Clinic** (red, patch up).
- On touch devices: on-screen joystick + **Car** / **Hit** buttons.

## What's implemented

Both modes share one state store (`localStorage` save, with export/import codes).

- **Empire mode** (dashboard): Jobs with tiers unlocked by rank, Crew (4 roles,
  loyalty, wages, district assignment — gift, **raise wages to boost loyalty**,
  or **fire** a member), Properties (buy/upgrade, timed income),
  Districts (0–100% control, takeover), Fight (attack rival gangs), Inventory +
  Flyers, Profile (save tools, premium toggle, prestige at Kingpin).
- **Street mode** (canvas): generated tile city with district regions, on-foot &
  driving movement with collisions, parked + moving traffic, pedestrians that
  flee, police with a 0–5 Heat-star system (chase, arrest, respray/evade to
  lose stars), and the five mission types — **delivery, getaway/collection,
  turf fight, car-theft order** — linked to Empire jobs via "Do it yourself".
- **Weapons:** an Arsenal (Empire tab) and a street **gun shop** sell melee
  (fists → bat → machete) and firearms (pistol → SMG → shotgun), unlocked by
  rank, with ammo. Guns fire by hitscan with tracers and auto-aim; firing is
  loud, so it spikes Heat. Equip anywhere; **Q** cycles weapons in the street.
- **The Pastor & converts:** a Pastor roams the streets preaching the gospel in
  speech bubbles. Every so often a reformed gang member walks up to the boss to
  say they're **born again** and quotes a verse of Scripture (KJV). You can
  bless them (eases Heat) or wave them off.
- **Energy:** the bar holds **100** and refills **40 per hour** (1 point every
  90s), capped at the bar; jobs spend it.
- **Sim systems:** game clock with day/night (affects lighting, crowds, police,
  night-only jobs), Heat / Respect / Loyalty meters, energy & stamina regen over
  real time, **offline progress** ("While you were away"), **weekly upkeep**, and
  daily **random events**.
- **In-game ads:** billboards (price tiers A/B/C placed in the world), a dashboard
  banner, and **rewarded full-screen flyers** (closable after 2s, capped at 3
  rewards/day, kept in the inventory). Paid ads come from an ad manifest; when
  none match the player's country/slot, an in-game **parody ad** is shown.
  Impression / view / click events are queued and batched (logged to the console
  until an endpoint is set). Premium turns paid billboards into parody.
- **Country packs:** the engine never changes between countries — each is a data
  pack. Two ship: **Lagos (Nigeria)** and **Fort Prairie (Canada)**, chosen on
  first launch (guessed from the browser).

## Where to tune things ("balance in data, not code")

Everything a designer tunes lives in [`js/data.js`](js/data.js):

- `COUNTRY_PACKS` — add a country by adding an entry (city, currency, price
  scale, districts, rivals, vehicles, shops, parody ads, NPC names/lines).
- `JOBS`, `PROPERTIES`, `CREW_ROLES`, `RANKS`, `EVENTS`, `MISSIONS`.
- `ADS` — the ad manifest (the `ads.json` stand-in). Add booked ads here, or
  point `TURF.ads.endpoint` at a tracking URL.

## Files

| File | Role |
| --- | --- |
| `index.html` | shell + HUD markup |
| `css/styles.css` | all styling, mobile layout, overlays |
| `js/data.js` | country packs, ads, jobs, props, crew, ranks (tuning) |
| `js/game.js` | state store, save/load, sim, ads, Empire dashboard |
| `js/street.js` | Street mode canvas engine (world, cars, police, missions) |
| `js/ui.js` | overlays (country select, flyers, upkeep, events, screens) |
| `js/main.js` | bootstrap + main loop |

## Not yet (v2, per the design doc)

Ad admin page + real tracking endpoint, cloud saves/accounts, more country
packs, real-money payments, and player-vs-player fights.

## Content & rating

All gangs, businesses and police forces are invented; cartoon violence only
(no blood/gore); illegal goods stay vague. Target rating: teen.
