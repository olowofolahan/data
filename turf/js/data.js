/* ==========================================================================
 * Turf — data packs
 * --------------------------------------------------------------------------
 * "Balance in data, not code." Everything the designer tunes lives here:
 * country packs, the ad manifest, jobs, properties, crew roles and ranks.
 * Adding a country means adding an entry to COUNTRY_PACKS — no engine change.
 * Loaded as a plain script so the game runs straight from file:// with no
 * build step and no fetch(). Exposed on the global TURF namespace.
 * ========================================================================== */
window.TURF = window.TURF || {};

/* -------------------------------------------------------------------------- */
/* Ranks (6 for version 1)                                                    */
/* -------------------------------------------------------------------------- */
TURF.RANKS = [
  { name: "Hustler",    min: 1,  max: 5,  unlock: "Basic jobs, melee, stealing parked cars" },
  { name: "Runner",     min: 6,  max: 12, unlock: "Delivery missions, first property, Driver crew" },
  { name: "Enforcer",   min: 13, max: 20, unlock: "Pistols, collections, first district takeover" },
  { name: "Lieutenant", min: 21, max: 30, unlock: "Fixer and Hacker crew, upgrades, turf wars" },
  { name: "Boss",       min: 31, max: 40, unlock: "Heists, rich district, bigger properties" },
  { name: "Kingpin",    min: 41, max: 50, unlock: "Whole-city control, prestige option" }
];

/* XP needed to reach the NEXT level = 100 * level^1.5 (rounded). */
TURF.xpForLevel = function (level) { return Math.round(100 * Math.pow(level, 1.5)); };

TURF.rankForLevel = function (level) {
  for (var i = TURF.RANKS.length - 1; i >= 0; i--) {
    if (level >= TURF.RANKS[i].min) return TURF.RANKS[i];
  }
  return TURF.RANKS[0];
};

/* -------------------------------------------------------------------------- */
/* Crew roles                                                                 */
/* -------------------------------------------------------------------------- */
TURF.CREW_ROLES = {
  muscle: { label: "Muscle", desc: "Raises attack in fights.",            atk: 8, def: 5, wage: 3,  hireRespect: 0  },
  driver: { label: "Driver", desc: "Faster getaways and deliveries.",     atk: 3, def: 4, wage: 3,  hireRespect: 10 },
  hacker: { label: "Hacker", desc: "Lowers Heat, unlocks heists.",        atk: 2, def: 3, wage: 5,  hireRespect: 40 },
  fixer:  { label: "Fixer",  desc: "Cheaper bribes and better prices.",   atk: 2, def: 6, wage: 5,  hireRespect: 40 }
};

/* -------------------------------------------------------------------------- */
/* Jobs (grouped into tiers that unlock by rank)                              */
/*   tier = minimum rank index (0 = Hustler ... 5 = Kingpin)                  */
/* -------------------------------------------------------------------------- */
TURF.JOBS = [
  { id: "j_lookout",   tier: 0, name: "Stand lookout",        energy: 2,  cashMin: 40,   cashMax: 90,   xp: 6,  heat: 2 },
  { id: "j_pickpkt",   tier: 0, name: "Pick a pocket",        energy: 2,  cashMin: 30,   cashMax: 120,  xp: 8,  heat: 5 },
  { id: "j_boost",     tier: 0, name: "Boost a parked car",   energy: 3,  cashMin: 80,   cashMax: 160,  xp: 12, heat: 8,  streetMissionId: "m_cartheft" },
  { id: "j_deliver",   tier: 1, name: "Run a package",        energy: 4,  cashMin: 140,  cashMax: 240,  xp: 18, heat: 6,  streetMissionId: "m_delivery", requires: { crew: 0 } },
  { id: "j_fuelrun",   tier: 1, name: "Fuel run",             energy: 4,  cashMin: 160,  cashMax: 260,  xp: 20, heat: 7 },
  { id: "j_collect",   tier: 2, name: "Collect protection",   energy: 5,  cashMin: 220,  cashMax: 380,  xp: 28, heat: 10, streetMissionId: "m_collection" },
  { id: "j_enforce",   tier: 2, name: "Lean on a debtor",     energy: 5,  cashMin: 260,  cashMax: 420,  xp: 30, heat: 14 },
  { id: "j_turf",      tier: 2, name: "Clear a block",        energy: 6,  cashMin: 300,  cashMax: 520,  xp: 40, heat: 18, streetMissionId: "m_turf", requires: { crew: 1 } },
  { id: "j_smuggle",   tier: 3, name: "Smuggle goods",        energy: 7,  cashMin: 420,  cashMax: 760,  xp: 55, heat: 16, nightOnly: true },
  { id: "j_gendeal",   tier: 3, name: "Generator deal",       energy: 7,  cashMin: 480,  cashMax: 820,  xp: 60, heat: 12, requires: { crew: 2 } },
  { id: "j_heist",     tier: 4, name: "Warehouse heist",      energy: 10, cashMin: 900,  cashMax: 1600, xp: 120,heat: 28, requires: { crew: 3 }, nightOnly: true },
  { id: "j_kidnap",    tier: 4, name: "Snatch a rival",       energy: 10, cashMin: 1100, cashMax: 1800, xp: 140,heat: 34, requires: { crew: 3 } },
  { id: "j_citywide",  tier: 5, name: "Citywide operation",   energy: 14, cashMin: 2200, cashMax: 3600, xp: 300,heat: 40, requires: { crew: 4 } }
];

/* -------------------------------------------------------------------------- */
/* Property templates (country pack can rename & rescale)                     */
/* -------------------------------------------------------------------------- */
TURF.PROPERTIES = [
  { id: "p_kiosk",   name: "Phone kiosk",     cost: 500,   income: 30,  everySec: 120, minRank: 1 },
  { id: "p_barber",  name: "Barber shop",     cost: 1200,  income: 70,  everySec: 180, minRank: 1 },
  { id: "p_carwash", name: "Car wash",        cost: 2600,  income: 150, everySec: 240, minRank: 2 },
  { id: "p_bar",     name: "Bar",             cost: 5200,  income: 320, everySec: 300, minRank: 3 },
  { id: "p_club",    name: "Night club",      cost: 12000, income: 760, everySec: 420, minRank: 4 }
];

/* -------------------------------------------------------------------------- */
/* Random event table (weighted). Resolved in sim.js.                         */
/* -------------------------------------------------------------------------- */
TURF.EVENTS = [
  { id: "e_crackdown", weight: 3, title: "Police crackdown", text: "The force is sweeping the city. Heat climbs and raids are likelier today." },
  { id: "e_raid",      weight: 3, title: "Rival raid",       text: "A rival gang hit one of your fronts. You lost a little cash." },
  { id: "e_raise",     weight: 2, title: "Crew wants a raise", text: "One of your crew is grumbling about pay. Loyalty slips a touch." },
  { id: "e_festival",  weight: 3, title: "Market day",       text: "A street festival packs the market. Shops pay extra protection today." },
  { id: "e_tip",       weight: 3, title: "A hot tip",        text: "Word of an easy score. Your next job pays more — move fast." }
];

/* -------------------------------------------------------------------------- */
/* Country packs. The engine never changes between countries.                 */
/* -------------------------------------------------------------------------- */
TURF.COUNTRY_PACKS = {
  lagos: {
    code: "NG",
    country: "Nigeria",
    city: "Lagos (fictionalised)",
    currency: { name: "Naira", symbol: "₦" },
    priceScale: 1000,
    police: "The Task Force",
    weather: "Hot, with rainy-season floods",
    radio: "Royalty-free afrobeat and highlife",
    language: "English with local flavour",
    characterLooks: ["Agbada", "Tracksuit", "Jersey", "Kaftan", "Denim", "Street"],
    vehicles: [
      { id: "danfo",  name: "Danfo bus", color: "#f6c945", speed: 2.1, handling: 0.80, value: 90 },
      { id: "keke",   name: "Keke",      color: "#ffd24d", speed: 2.4, handling: 0.95, value: 60 },
      { id: "okada",  name: "Okada",     color: "#d64545", speed: 3.2, handling: 1.15, value: 40 },
      { id: "saloon", name: "Saloon car",color: "#6aa9e0", speed: 2.8, handling: 1.00, value: 150 },
      { id: "jeep",   name: "Big jeep",  color: "#2f2f3a", speed: 3.0, handling: 0.90, value: 400 }
    ],
    districts: [
      { id: "balogun",  name: "Balogun Market", type: "market",    income: 90,  danger: 2, color: "#e07a3f" },
      { id: "apapa",    name: "Apapa Port",     type: "port",      income: 120, danger: 3, color: "#3f7fe0" },
      { id: "ikoyi",    name: "Ikoyi Heights",  type: "rich",      income: 160, danger: 4, color: "#39b37a" },
      { id: "marina",   name: "Marina Central", type: "downtown",  income: 140, danger: 3, color: "#c9a13f" },
      { id: "ajegunle", name: "Ajegunle",       type: "lowincome", income: 60,  danger: 4, color: "#9b59b6" },
      { id: "oshodi",   name: "Oshodi Hub",     type: "transport", income: 100, danger: 3, color: "#e05a7a" }
    ],
    rivals: [
      { id: "eko_boys",   name: "Eko Boys",      color: "#c0392b" },
      { id: "lagoon_set", name: "Lagoon Set",    color: "#2980b9" },
      { id: "area_fathers", name: "Area Fathers",color: "#8e44ad" }
    ],
    npcNames: ["Tunde", "Ngozi", "Emeka", "Bisi", "Chidi", "Funke", "Segun", "Amaka", "Kola", "Yemi"],
    npcLines: ["How far?", "No wahala.", "Abeg shift!", "Na who be this?", "Make we dey go.", "Chop knuckle!"],
    shops: ["Buka", "Suya spot", "Phone stall", "Provision store"],
    parody: [
      { brand: "Jollof King",   tag: "Rice so good it's a crime", bg: "#e07a3f", fg: "#fff" },
      { brand: "NEPA Light",    tag: "We promise power. Probably.", bg: "#243b6b", fg: "#ffd24d" },
      { brand: "Okada Express", tag: "Beat the traffic. Maybe.", bg: "#d64545", fg: "#fff" },
      { brand: "Gidi Cola",     tag: "The taste of the city", bg: "#2e8b57", fg: "#fff" }
    ]
  },

  prairie: {
    code: "CA",
    country: "Canada",
    city: "Fort Prairie (fictional)",
    currency: { name: "Dollar", symbol: "$" },
    priceScale: 1,
    police: "City Patrol",
    weather: "Snow and ice that affect handling",
    radio: "Royalty-free country and synth",
    language: "English and French strings ready",
    characterLooks: ["Parka", "Flannel", "Hoodie", "Toque", "Denim", "Puffer"],
    vehicles: [
      { id: "pickup",  name: "Pickup",     color: "#c0392b", speed: 2.9, handling: 0.95, value: 180 },
      { id: "sedan",   name: "Sedan",      color: "#5d6d7e", speed: 2.8, handling: 1.00, value: 150 },
      { id: "plow",    name: "Snowplough", color: "#f39c12", speed: 2.0, handling: 0.70, value: 260 },
      { id: "citybus", name: "City bus",   color: "#2874a6", speed: 2.0, handling: 0.75, value: 120 },
      { id: "suv",     name: "SUV",        color: "#17202a", speed: 3.0, handling: 0.90, value: 360 }
    ],
    districts: [
      { id: "market",   name: "Market Square",  type: "market",    income: 90,  danger: 2, color: "#e07a3f" },
      { id: "railyard", name: "Rail Yard",      type: "port",      income: 120, danger: 3, color: "#3f7fe0" },
      { id: "hillcrest",name: "Hillcrest",      type: "rich",      income: 160, danger: 4, color: "#39b37a" },
      { id: "downtown", name: "Downtown Core",  type: "downtown",  income: 140, danger: 3, color: "#c9a13f" },
      { id: "flats",    name: "River Flats",    type: "lowincome", income: 60,  danger: 4, color: "#9b59b6" },
      { id: "station",  name: "Union Station",  type: "transport", income: 100, danger: 3, color: "#e05a7a" }
    ],
    rivals: [
      { id: "northside", name: "Northside Crew", color: "#c0392b" },
      { id: "rivermen",  name: "The Rivermen",   color: "#2980b9" },
      { id: "frost_kings",name: "Frost Kings",   color: "#8e44ad" }
    ],
    npcNames: ["Dylan", "Marie", "Chase", "Nicole", "Brett", "Chantal", "Kyle", "Amber", "Shane", "Josee"],
    npcLines: ["How's it goin', eh?", "Cold out.", "Watch the ice.", "Take off.", "Beauty.", "No worries."],
    shops: ["Coffee shop", "Diner", "Hardware store", "Gas bar"],
    parody: [
      { brand: "Double Moose", tag: "Coffee that keeps you up north", bg: "#6f4e37", fg: "#fff" },
      { brand: "IceCo",        tag: "We make winter colder", bg: "#2874a6", fg: "#fff" },
      { brand: "Prairie Pete", tag: "Trucks for real folks", bg: "#c0392b", fg: "#fff" },
      { brand: "MapleJuice",   tag: "Sweet enough to arrest", bg: "#b9770e", fg: "#fff" }
    ]
  }
};

/* -------------------------------------------------------------------------- */
/* Ad manifest (ads.json stand-in). In production this is fetched from a       */
/* static host every 15 minutes. Here it is embedded so the game runs offline. */
/* When no paid ad matches a slot/country, a parody ad is shown instead.       */
/* -------------------------------------------------------------------------- */
TURF.ADS = {
  updatedAt: "2026-10-26",
  ads: [
    // Example of a "booked" ad. Leave empty to see parody fallbacks everywhere.
    // {
    //   id: "ad_demo", kind: "billboard", countries: ["NG"], tiers: ["A","B"],
    //   start: "2026-01-01", end: "2027-01-01", weight: 5,
    //   image: null, text: "Your Brand Here", bg: "#111", fg: "#0f0", url: "https://example.com"
    // }
  ]
};

/* Street missions (linked to Empire jobs via streetMissionId). */
TURF.MISSIONS = {
  m_cartheft:  { kind: "cartheft",  label: "Boost a car and reach the chop shop" },
  m_delivery:  { kind: "delivery",  label: "Deliver the package before the timer" },
  m_collection:{ kind: "collection",label: "Collect from 3 shops in the district" },
  m_turf:      { kind: "turf",      label: "Clear the rival gang from the block" }
};
