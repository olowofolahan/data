# Turf

A top-down browser crime-management sim built from the **Turf Game Design
Document**. Start broke in a city and climb from small-time hustler to kingpin
through jobs, crew, property and territory — in the spirit of Mob Wars, wrapped
in a life-sim clock.

**No build step, no install, no external assets.** Open `index.html` in any
browser (desktop or mobile) and play.

> Note: the real-time **Street mode** (top-down driving/shooting) was removed by
> request — the game is now the **Empire dashboard** only. Its weapons live on as
> the Arsenal (they boost fight strength).

## Play

- **Locally:** double-click `index.html`, or serve the folder
  (`python3 -m http.server` then open `http://localhost:8000/`).
- **Deploy:** upload the `turf/` folder to any static host (Netlify, Vercel,
  Cloudflare Pages, GitHub Pages).

## What's implemented

One state store (`localStorage` save, with export/import codes) drives the
Empire dashboard.

- **Jobs** with tiers unlocked by rank (above-rank jobs show as locked cards so
  you can see what's coming), including two specials:
  - **Political thug** — swing an election for your backer for a big payout, but
    it can **backfire** (a property is seized, Respect drops). Crew and low Heat
    improve the odds.
  - **Bribe a local cop** — pay a cop to **cool your Heat (−60%)**, or **sic them
    on a rival crew** (the cops raid a rival-held district and cut their control,
    sometimes clearing it for you to take). **Small risk it backfires** — a greedy
    cop pockets the money, or a dirty one tips the rival off (a Fixer or political
    clout lowers the odds).
  - **Whistle-blow on rivals** (available from the start) — tip the law for an
    informant fee and chip at a rival's turf, with a small chance a rival learns
    you snitched and retaliates.
- **Crew** (5 roles: Muscle, Driver, Hacker, Fixer, and a **Gov't official** who
  expands business — **+25% property/district income and +15% job payouts**;
  loyalty, wages, district assignment) — gift, **raise wages to boost loyalty**,
  or **fire** a member.
- **Properties** (buy/upgrade, timed income), **Districts** (0–100% control,
  takeover, and **turf wars** resolved with your strength). When a district is
  slipping, the card and the alert **tell you why** (which rival raided it, no
  crew defending, high-danger area, high Heat). **Fight** (attack rival gangs).
- **Rival gangs grow with you:** each city has **9 gangs**, and more **emerge as
  you level up** (3 at the start, up to all 9 by Lv 45) — shown as locked
  "Emerges at Lv N" cards until they appear.
- **Wear gangs down:** every hit in the Fight tab drains the target gang's
  **stamina**; drain it to 0 and they're **exhausted** — they can't raid your
  districts and need **6 hours** to recover (shown as a bar + countdown).
- **Rating vs rival power:** your rating is **Attack + Defence + Respect**; each
  gang has a Power that scales with its rank and your level. **When you outrank a
  gang they can't take your district and can't beat you in a fight — and they
  take a loss for trying** (their own turf gets hit). The Fight tab shows both
  numbers and flags whether you outrank each gang.
- **Arsenal:** two equip slots — a **weapon** (Attack) and a piece of **gear**
  (Defence, some also Attack).
  - Weapons: melee (fists → bat → machete), firearms (pistol → SMG → shotgun),
    heavy ordnance (**Grenades**, **RPG / missiles**) and, at Kingpin, **Political
    influence** (also lowers job Heat and bribe risk). Each shows its unlock rank.
  - Gear: Light vest, Brass knuckles, Kevlar vest, Attack dog, Bodyguard,
    Armoured SUV raise your **Defence** (some also Attack). The heavy gear —
    **Armoured truck, Attack helicopter, Private militia** — adds **district
    defence** that shields *all* your districts from rival raids while equipped.
  - **Upgrade gear** up to Lv 5: each level adds +40% of its bonuses (cost rises
    per level), like upgrading a property.
  - Every shop shows the required **rank** (name + level) to unlock, and your
    current rank/number is in the header.
- **Friends:** add friends by email and **invite them** — Send invite opens a
  ready-made message you can **copy** (email, WhatsApp, SMS) or open in your mail
  app. Because the game runs on a **private** link, you first make it shareable
  via the page's **Share** menu and **paste that link** into the invite (it's
  remembered after that); otherwise friends get "page not found." The sandboxed
  page can't send mail itself, and your list is saved on your device. You can
  also **Recruit a friend as a lackey** — a loyal crew member named after them
  (single-player, so it's a local crew member, not live co-op).
- **Energy & stamina:** energy holds **100** and refills **40 per hour** (1 every
  90s); stamina holds **50** and regenerates over time. In the **Fight** tab you
  can also buy **street food** (+12) or a **romantic indulgence** (+45) to top up
  stamina for fights and turf wars. Economy is tuned to realistic Lagos naira (lookout
  ≈ ₦4k–9k, a protection round ≈ ₦22k–38k, a kiosk ₦50k, a club ₦1.2M).
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
| `js/ui.js` | overlays (country select, flyers, upkeep, events, choices) |
| `js/main.js` | bootstrap + main loop |

## Online (async multiplayer)

When the game is opened on its **shared** claude.ai link, a **World** tab lights
up using the artifact's shared database:
- your empire is posted to a **global leaderboard** (rating, respect, rank,
  districts);
- you can **raid** other players' saved empires (resolved with the rating
  system); the defender applies the consequence the next time they load, and
  sees a "raids while you were away" summary.

Two backends power the World tab (see `js/online.js`):

**1. Supabase — OPEN multiplayer (recommended for real play).** Every player on
the shared link posts and raids, using one Supabase project's public anon key.
Set it up once:
1. Create a free project at [supabase.com](https://supabase.com).
2. In the project's **SQL Editor**, run [`turf/supabase/schema.sql`](supabase/schema.sql)
   (creates the `players` + `raids` tables and opens them to the anon key via RLS).
3. In **Project Settings → API**, copy the **Project URL** and the **anon public**
   key (both are safe to ship in client code — the anon key is meant to be public).
4. Put them in [`js/config.js`](js/config.js) (`supabaseUrl`, `supabaseAnonKey`) and
   republish/redeploy so **all** players use them. (The World tab also has a field
   to paste them for a quick per-device test.)

When configured, the World tab's backend reads "Supabase (open multiplayer)" and
anyone — public-link visitors included — appears on the board and can raid.

**2. Artifact shared database (fallback, no setup).** Uses the `db` + `user`
runtime capabilities. The owner and invited **Contributors/Editors** (and
same-workspace members) can post and raid; a plain **public link** from outside
the workspace is **read-only** — which is why a second player on a public link
won't show on that board. On a local file, online stays off and single-player
works normally.

## Not yet (v2, per the design doc)

Ad admin page + real tracking endpoint, cloud saves/accounts, more country
packs, real-money payments, and player-vs-player fights.

## Content & rating

All gangs, businesses and police forces are invented; cartoon violence only
(no blood/gore); illegal goods stay vague. Target rating: teen.
