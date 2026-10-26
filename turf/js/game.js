/* ==========================================================================
 * Turf — engine
 * --------------------------------------------------------------------------
 * A no-build, single-page implementation of the Turf design. Two modes share
 * one state store:
 *   - Empire mode : a DOM dashboard (jobs, crew, properties, districts, fight)
 *   - Street mode : a top-down canvas city (walk, steal & drive cars, police,
 *                   Heat, and the five street-mission types)
 * Sim systems (clock, energy/stamina regen, offline progress, weekly upkeep,
 * random events, Heat/Respect/Loyalty) run regardless of mode.
 * The in-game ad system (billboards + flyers, parody fallback, tracking) is
 * wired through TURF.ads.
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;

/* ====================== small helpers ===================================== */
var SAVE_KEY = "turf.save.v1";
var now = function () { return Date.now(); };
var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
var rand = function (a, b) { return a + Math.random() * (b - a); };
var randint = function (a, b) { return Math.floor(rand(a, b + 1)); };
var pick = function (arr) { return arr[randint(0, arr.length - 1)]; };
var $ = function (sel) { return document.querySelector(sel); };
var el = function (tag, cls, html) {
  var e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};
T.pack = function () { return T.COUNTRY_PACKS[T.state.country]; };
T.money = function (n) {
  var p = T.pack();
  return p.currency.symbol + Math.round(n).toLocaleString("en-US");
};
T.toast = function (msg, kind) {
  var host = $("#toasts");
  var t = el("div", "toast" + (kind ? " toast--" + kind : ""), msg);
  host.appendChild(t);
  setTimeout(function () { t.classList.add("toast--in"); }, 10);
  setTimeout(function () {
    t.classList.remove("toast--in");
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
  }, 2600);
};

/* ====================== state store ======================================= */
T.state = null;

T.newGame = function (country, name, look) {
  var pk = T.COUNTRY_PACKS[country];
  var districts = {};
  pk.districts.forEach(function (d, i) {
    // Start: player owns a toehold in the first district; rivals hold a couple.
    if (i === 0) districts[d.id] = { owner: "player", control: 100 };
    else if (i <= 2) districts[d.id] = { owner: pk.rivals[i - 1].id, control: 100 };
    else districts[d.id] = { owner: null, control: randint(0, 30) };
  });
  var t = now();
  T.state = {
    version: 1,
    country: country,
    player: { name: name || "Newcomer", look: look || pk.characterLooks[0],
              level: 1, xp: 0, cash: 200 * pk.priceScale,
              respect: 0, heat: 0 },
    resources: { energy: 20, energyMax: 20, stamina: 10, staminaMax: 10, health: 100, healthMax: 100 },
    resUpdated: t,
    crew: [],
    properties: [],
    districts: districts,
    inventory: { items: [], flyers: [] },
    flyersToday: 0, lastFlyerDay: 0,
    premium: false,
    gameMinutes: 8 * 60,          // start at 08:00 on day 0
    lastSeen: t,
    lastUpkeepDay: 0,
    lastEventDay: 0, eventToday: null,
    lastRivalTick: t,
    bonusNextJob: 0,              // from "hot tip" event
    protectionBonus: 1,          // from "market day" event
    stats: { jobsDone: 0, mastery: {}, fights: 0 },
    tutorialStep: 0,
    createdAt: t
  };
  T.save();
};

T.save = function () {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(T.state)); }
  catch (e) { /* storage may be blocked; game still runs this session */ }
};
T.hasSave = function () {
  try { return !!localStorage.getItem(SAVE_KEY); } catch (e) { return false; }
};
T.load = function () {
  try {
    var raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return false;
    T.state = JSON.parse(raw);
    return !!(T.state && T.state.country && T.COUNTRY_PACKS[T.state.country]);
  } catch (e) { return false; }
};
T.exportCode = function () {
  try { return btoa(unescape(encodeURIComponent(JSON.stringify(T.state)))); }
  catch (e) { return ""; }
};
T.importCode = function (code) {
  try {
    var s = JSON.parse(decodeURIComponent(escape(atob(code.trim()))));
    if (!s.country || !T.COUNTRY_PACKS[s.country]) return false;
    T.state = s; T.save(); return true;
  } catch (e) { return false; }
};

/* ====================== sim ============================================== */
T.sim = {};
var DAY = 1440; // game minutes per day

T.sim.gameDay  = function () { return Math.floor(T.state.gameMinutes / DAY); };
T.sim.gameHour = function () { return Math.floor((T.state.gameMinutes % DAY) / 60); };
T.sim.isNight  = function () { var h = T.sim.gameHour(); return h >= 20 || h < 6; };
T.sim.clockStr = function () {
  var h = T.sim.gameHour(), m = Math.floor(T.state.gameMinutes % 60);
  return ("0" + h).slice(-2) + ":" + ("0" + m).slice(-2);
};

/* Regen resources from elapsed real time (also covers offline). */
T.sim.regen = function () {
  var r = T.state.resources, dt = now() - T.state.resUpdated;
  if (dt <= 0) return;
  var eGain = Math.floor(dt / (3 * 60 * 1000));
  var sGain = Math.floor(dt / (4 * 60 * 1000));
  var hGain = Math.floor(dt / (90 * 1000)); // slow health regen ~1 / 90s
  if (eGain > 0) r.energy  = clamp(r.energy  + eGain, 0, r.energyMax);
  if (sGain > 0) r.stamina = clamp(r.stamina + sGain, 0, r.staminaMax);
  if (hGain > 0) r.health  = clamp(r.health  + hGain, 0, r.healthMax);
  // Advance resUpdated only by whole consumed intervals to avoid losing remainder.
  var used = Math.min(
    eGain > 0 ? eGain * 3 * 60 * 1000 : dt,
    sGain > 0 ? sGain * 4 * 60 * 1000 : dt
  );
  // Simpler & safe: keep remainder for the fastest timer (energy).
  T.state.resUpdated += eGain * 3 * 60 * 1000;
  if (eGain === 0) T.state.resUpdated = now() - (dt % (3 * 60 * 1000));
};

/* Pending passive income from properties + owned districts. */
T.sim.pendingIncome = function () {
  var total = 0, t = now();
  T.state.properties.forEach(function (p) {
    var tpl = T.PROPERTIES.filter(function (x) { return x.id === p.tplId; })[0];
    if (!tpl) return;
    var periods = Math.floor((t - p.lastCollect) / (tpl.everySec * 1000));
    var districtBonus = (T.state.districts[p.districtId] &&
                         T.state.districts[p.districtId].owner === "player") ? 1.25 : 1;
    total += periods * tpl.income * (p.level) * districtBonus * T.state.protectionBonus;
  });
  // District passive income: pay per real minute of ownership since lastSeen handled at collect.
  return Math.floor(total);
};
T.sim.districtIncomePerMin = function () {
  var pk = T.pack(), per = 0;
  pk.districts.forEach(function (d) {
    var st = T.state.districts[d.id];
    if (st && st.owner === "player") per += d.income * (st.control / 100);
  });
  return per; // per game-day-ish; applied in collect below
};
T.sim.collect = function () {
  var t = now(), gained = 0;
  T.state.properties.forEach(function (p) {
    var tpl = T.PROPERTIES.filter(function (x) { return x.id === p.tplId; })[0];
    if (!tpl) return;
    var periods = Math.floor((t - p.lastCollect) / (tpl.everySec * 1000));
    if (periods <= 0) return;
    var districtBonus = (T.state.districts[p.districtId] &&
                         T.state.districts[p.districtId].owner === "player") ? 1.25 : 1;
    gained += periods * tpl.income * p.level * districtBonus * T.state.protectionBonus;
    p.lastCollect += periods * tpl.everySec * 1000;
  });
  gained = Math.floor(gained);
  if (gained > 0) { T.state.player.cash += gained; }
  return gained;
};

/* Offline catch-up on load: advance clock, regen, accrue income, cool Heat. */
T.sim.catchUp = function () {
  var t = now();
  var dtMs = clamp(t - T.state.lastSeen, 0, 12 * 3600 * 1000);
  var gameMinGained = Math.floor(dtMs / 1000); // 1 real sec = 1 game min
  T.state.gameMinutes += gameMinGained;
  T.sim.regen();
  // District passive income while away: income per game-day * fraction of a day elapsed.
  var dayFrac = gameMinGained / DAY;
  var dIncome = Math.floor(T.sim.districtIncomePerMin() * dayFrac);
  var propIncome = T.sim.collect();
  // Heat cools over time offline.
  var cooled = Math.floor(dtMs / (60 * 1000)) * 1; // ~1 per real minute
  var before = T.state.player.heat;
  T.state.player.heat = clamp(T.state.player.heat - cooled, 0, 100);
  if (dIncome > 0) T.state.player.cash += dIncome;
  T.state.lastSeen = t;
  return { ms: dtMs, propIncome: propIncome, districtIncome: dIncome,
           heatCooled: before - T.state.player.heat };
};

/* Weekly upkeep: every 7 game days. */
T.sim.upkeepDue = function () { return T.sim.gameDay() >= T.state.lastUpkeepDay + 7; };
T.sim.upkeepBill = function () {
  var wages = T.state.crew.reduce(function (s, c) { return s + c.wage; }, 0) * T.pack().priceScale;
  var maint = T.state.properties.reduce(function (s, p) {
    var tpl = T.PROPERTIES.filter(function (x) { return x.id === p.tplId; })[0];
    return s + (tpl ? Math.round(tpl.cost * 0.02) * p.level : 0);
  }, 0);
  var bribes = Math.round(T.state.player.heat * 3) * T.pack().priceScale;
  return { wages: wages, maint: maint, bribes: bribes, total: wages + maint + bribes };
};
T.sim.payUpkeep = function () {
  var bill = T.sim.upkeepBill();
  T.state.lastUpkeepDay = T.sim.gameDay();
  if (T.state.player.cash >= bill.total) {
    T.state.player.cash -= bill.total;
    return { paid: true, bill: bill, lost: [] };
  }
  // Can't pay: loyalty drops; least loyal leave.
  var lost = [];
  T.state.crew.forEach(function (c) { c.loyalty = clamp(c.loyalty - 25, 0, 100); });
  T.state.crew.sort(function (a, b) { return a.loyalty - b.loyalty; });
  while (T.state.crew.length && T.state.crew[0].loyalty < 30 && lost.length < 2) {
    lost.push(T.state.crew.shift().name);
  }
  T.state.player.cash = Math.max(0, T.state.player.cash);
  return { paid: false, bill: bill, lost: lost };
};

/* Daily random event. */
T.sim.rollEvent = function () {
  var day = T.sim.gameDay();
  if (day === T.state.lastEventDay) return null;
  T.state.lastEventDay = day;
  T.state.protectionBonus = 1;            // reset day modifiers
  var totalW = T.EVENTS.reduce(function (s, e) { return s + e.weight; }, 0);
  var r = rand(0, totalW), acc = 0, ev = T.EVENTS[0];
  for (var i = 0; i < T.EVENTS.length; i++) { acc += T.EVENTS[i].weight; if (r <= acc) { ev = T.EVENTS[i]; break; } }
  T.state.eventToday = ev.id;
  switch (ev.id) {
    case "e_crackdown": T.state.player.heat = clamp(T.state.player.heat + 15, 0, 100); break;
    case "e_raid":
      var loss = Math.min(T.state.player.cash, randint(50, 300) * T.pack().priceScale);
      T.state.player.cash -= loss; ev = Object.assign({}, ev, { text: ev.text + " (-" + T.money(loss) + ")" }); break;
    case "e_raise": if (T.state.crew.length) pick(T.state.crew).loyalty = clamp(pick(T.state.crew).loyalty - 15, 0, 100); break;
    case "e_festival": T.state.protectionBonus = 2; break;
    case "e_tip": T.state.bonusNextJob = 0.5; break;
  }
  return ev;
};

/* Rivals periodically attack the player's weakest district. */
T.sim.rivalTick = function () {
  var t = now();
  if (t - T.state.lastRivalTick < 90 * 1000) return; // every ~90s of play
  T.state.lastRivalTick = t;
  var owned = Object.keys(T.state.districts).filter(function (id) {
    return T.state.districts[id].owner === "player";
  });
  if (!owned.length) return;
  owned.sort(function (a, b) {
    var ca = T.state.districts[a].control + crewIn(a) * 20;
    var cb = T.state.districts[b].control + crewIn(b) * 20;
    return ca - cb;
  });
  var weakest = owned[0];
  var defended = crewIn(weakest) > 0;
  var drop = defended ? randint(2, 6) : randint(8, 18);
  T.state.districts[weakest].control = clamp(T.state.districts[weakest].control - drop, 0, 100);
  var dName = T.pack().districts.filter(function (d) { return d.id === weakest; })[0].name;
  if (T.state.districts[weakest].control <= 0) {
    T.state.districts[weakest].owner = pick(T.pack().rivals).id;
    T.state.districts[weakest].control = 60;
    T.state.player.respect = Math.max(0, T.state.player.respect - 20);
    T.toast("Lost " + dName + " to a rival!", "bad");
  } else if (!defended) {
    T.toast("Rivals pressing " + dName + " (-" + drop + "% control)", "warn");
  }
};
function crewIn(districtId) {
  return T.state.crew.filter(function (c) { return c.assignedDistrict === districtId; }).length;
}

/* XP / level up. */
T.sim.addXp = function (xp) {
  T.state.player.xp += xp;
  var leveled = false;
  while (T.state.player.xp >= T.xpForLevel(T.state.player.level) && T.state.player.level < 50) {
    T.state.player.xp -= T.xpForLevel(T.state.player.level);
    T.state.player.level++;
    T.state.resources.energyMax += 2;
    T.state.resources.staminaMax += 1;
    leveled = true;
  }
  if (leveled) {
    var rk = T.rankForLevel(T.state.player.level);
    T.toast("Level " + T.state.player.level + " — " + rk.name, "good");
  }
};

/* ====================== ads ============================================== */
T.ads = { queue: [], lastImpression: {} };
T.ads.endpoint = null; // set to a URL to POST events; otherwise logged to console

T.ads.parodyFor = function (slotId) {
  var list = T.pack().parody;
  // Deterministic per slot so a billboard keeps its parody between frames.
  var h = 0; for (var i = 0; i < slotId.length; i++) h = (h * 31 + slotId.charCodeAt(i)) | 0;
  var p = list[Math.abs(h) % list.length];
  return { parody: true, brand: p.brand, text: p.tag, bg: p.bg, fg: p.fg, url: null };
};
T.ads.pick = function (kind, tier, slotId) {
  var code = T.pack().code, today = new Date().toISOString().slice(0, 10);
  var matches = (T.ADS.ads || []).filter(function (a) {
    return a.kind === kind &&
           (!a.countries || a.countries.indexOf(code) >= 0) &&
           (!a.tiers || !tier || a.tiers.indexOf(tier) >= 0) &&
           (!a.start || a.start <= today) && (!a.end || a.end >= today);
  });
  if (T.state && T.state.premium && kind !== "flyer") return T.ads.parodyFor(slotId);
  if (!matches.length) return T.ads.parodyFor(slotId);
  var totalW = matches.reduce(function (s, a) { return s + (a.weight || 1); }, 0);
  var r = rand(0, totalW), acc = 0, chosen = matches[0];
  for (var i = 0; i < matches.length; i++) { acc += (matches[i].weight || 1); if (r <= acc) { chosen = matches[i]; break; } }
  return Object.assign({ parody: false, url: chosen.url || null }, chosen);
};
T.ads.track = function (adId, slotId, kind) {
  if (kind === "impression") {
    var key = slotId, last = T.ads.lastImpression[key] || 0;
    if (now() - last < 60 * 1000) return; // once per slot per minute per player
    T.ads.lastImpression[key] = now();
  }
  T.ads.queue.push({
    adId: adId || "parody", slotId: slotId, country: T.pack().code,
    kind: kind, ts: now(), playerId: T.ads.playerId()
  });
};
T.ads.playerId = function () {
  var id = null;
  try { id = localStorage.getItem("turf.pid"); } catch (e) {}
  if (!id) { id = "p_" + Math.random().toString(36).slice(2, 10); try { localStorage.setItem("turf.pid", id); } catch (e) {} }
  return id;
};
T.ads.flush = function () {
  if (!T.ads.queue.length) return;
  var batch = T.ads.queue.splice(0, T.ads.queue.length);
  if (T.ads.endpoint) {
    try { fetch(T.ads.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(batch) }); }
    catch (e) { T.ads.queue = batch.concat(T.ads.queue); } // keep for later if offline
  } else {
    console.log("[ads] batch of " + batch.length + " events:", batch);
  }
};
setInterval(function () { T.ads.flush(); }, 60 * 1000);

/* ====================== game controller ================================== */
T.game = { mode: "empire", raf: null };

T.game.setMode = function (mode) {
  T.game.mode = mode;
  $("#empire").style.display = mode === "empire" ? "" : "none";
  $("#street").style.display = mode === "street" ? "" : "none";
  if (mode === "empire") { T.empire.render(); }
  if (mode === "street") { T.street.onShow(); }
};

/* One-second sim heartbeat (runs in any mode). */
T.game.heartbeat = function () {
  // advance clock by elapsed real time (1 real sec = 1 game min)
  var t = now();
  if (!T.game._lastTick) T.game._lastTick = t;
  var mins = (t - T.game._lastTick) / 1000;
  T.state.gameMinutes += mins;
  T.game._lastTick = t;
  T.sim.regen();
  T.sim.rivalTick();
  T.state.lastSeen = t;

  // Daily event & weekly upkeep are surfaced in Empire mode only, so they
  // never interrupt a Street-mode chase. They stay pending until the player
  // returns to the dashboard.
  if (T.game.mode === "empire") {
    var ev = T.sim.rollEvent();
    if (ev) T.ui.event(ev);
    if (T.sim.upkeepDue()) T.ui.upkeep();
    T.empire.refreshHeader();
  }
  T.save();
};

/* ====================== EMPIRE MODE ====================================== */
T.empire = { tab: "jobs" };

T.empire.refreshHeader = function () {
  var s = T.state, r = s.resources, rk = T.rankForLevel(s.player.level);
  var need = T.xpForLevel(s.player.level);
  var set = function (sel, v) { var e = $(sel); if (e) e.textContent = v; };
  set("#hd-name", s.player.name);
  set("#hd-rank", rk.name + " · Lv " + s.player.level);
  set("#hd-cash", T.money(s.player.cash));
  set("#hd-energy", Math.floor(r.energy) + "/" + r.energyMax);
  set("#hd-stamina", Math.floor(r.stamina) + "/" + r.staminaMax);
  set("#hd-health", Math.floor(r.health) + "/" + r.healthMax);
  set("#hd-respect", Math.floor(s.player.respect));
  set("#hd-heat", Math.floor(s.player.heat) + "%");
  set("#hd-clock", T.sim.clockStr() + (T.sim.isNight() ? " 🌙" : " ☀️") + " · Day " + (T.sim.gameDay() + 1));
  var xpbar = $("#hd-xpbar"); if (xpbar) xpbar.style.width = clamp((s.player.xp / need) * 100, 0, 100) + "%";
  var heatbar = $("#hd-heatbar"); if (heatbar) heatbar.style.width = s.player.heat + "%";
  // banner ad
  var banner = $("#hd-banner");
  if (banner && !banner.dataset.filled) { T.empire.fillBanner(banner); }
};
T.empire.fillBanner = function (banner) {
  var ad = T.ads.pick("banner", null, "banner_header");
  banner.style.background = ad.bg; banner.style.color = ad.fg;
  banner.innerHTML = "<strong>" + (ad.brand || "Ad") + "</strong> " + (ad.text || "") +
    (ad.parody ? " <span class='ad-tag'>parody</span>" : "");
  banner.dataset.filled = "1";
  banner.onclick = function () { if (ad.url) { T.ads.track(ad.id, "banner_header", "click"); window.open(ad.url, "_blank"); } };
  T.ads.track(ad.id, "banner_header", "impression");
};

T.empire.render = function () {
  T.empire.refreshHeader();
  var tabs = $("#emp-tabs");
  tabs.innerHTML = "";
  var defs = [["jobs", "Jobs"], ["crew", "Crew"], ["properties", "Properties"],
              ["districts", "Districts"], ["fight", "Fight"], ["inventory", "Inventory"], ["profile", "Profile"]];
  defs.forEach(function (d) {
    var b = el("button", "tab" + (T.empire.tab === d[0] ? " tab--on" : ""), d[1]);
    b.onclick = function () { T.empire.tab = d[0]; T.empire.render(); };
    tabs.appendChild(b);
  });
  var body = $("#emp-body");
  body.innerHTML = "";
  ({ jobs: T.empire.tabJobs, crew: T.empire.tabCrew, properties: T.empire.tabProps,
     districts: T.empire.tabDistricts, fight: T.empire.tabFight,
     inventory: T.empire.tabInventory, profile: T.empire.tabProfile })[T.empire.tab](body);
};

T.empire.tabJobs = function (body) {
  var s = T.state, rankIdx = T.RANKS.indexOf(T.rankForLevel(s.player.level));
  var intro = el("p", "muted", "Jobs cost energy and pay cash + XP. Some open as a Street mission for a bigger payout.");
  body.appendChild(intro);
  var grid = el("div", "cards");
  T.JOBS.forEach(function (job) {
    if (job.tier > rankIdx) return;
    var locked = false, reason = "";
    if (job.nightOnly && !T.sim.isNight()) { locked = true; reason = "Night only"; }
    if (job.requires && job.requires.crew && s.crew.length < job.requires.crew) { locked = true; reason = "Needs " + job.requires.crew + " crew"; }
    if (s.resources.energy < job.energy) { locked = true; reason = "Low energy"; }
    var card = el("div", "card");
    var mastery = s.stats.mastery[job.id] || 0;
    card.innerHTML =
      "<h4>" + job.name + "</h4>" +
      "<div class='row'><span>⚡ " + job.energy + "</span>" +
      "<span>" + T.money(job.cashMin * T.pack().priceScale) + "–" + T.money(job.cashMax * T.pack().priceScale) + "</span></div>" +
      "<div class='row muted'><span>+" + job.xp + " XP</span><span>+Heat " + job.heat + "</span></div>" +
      "<div class='muted small'>Done " + mastery + "×" + (mastery >= 5 ? " ★ mastered" : "") + "</div>";
    var btns = el("div", "row");
    var go = el("button", "btn", "Do job");
    go.disabled = locked; if (locked) go.title = reason;
    go.onclick = function () { T.empire.doJob(job); };
    btns.appendChild(go);
    if (job.streetMissionId) {
      var diy = el("button", "btn btn--ghost", "Do it yourself");
      diy.disabled = s.resources.energy < job.energy;
      diy.onclick = function () { T.street.startMission(job.streetMissionId, job); };
      btns.appendChild(diy);
    }
    card.appendChild(btns);
    if (locked) card.classList.add("card--locked");
    grid.appendChild(card);
  });
  body.appendChild(grid);
};

T.empire.doJob = function (job) {
  var s = T.state;
  if (s.resources.energy < job.energy) { T.toast("Not enough energy", "warn"); return; }
  s.resources.energy -= job.energy;
  var pay = randint(job.cashMin, job.cashMax) * T.pack().priceScale;
  if (s.bonusNextJob) { pay = Math.round(pay * (1 + s.bonusNextJob)); s.bonusNextJob = 0; T.toast("Hot tip paid off!", "good"); }
  // Fixer crew improves prices.
  if (s.crew.some(function (c) { return c.role === "fixer"; })) pay = Math.round(pay * 1.1);
  s.player.cash += pay;
  T.sim.addXp(job.xp);
  s.player.respect += Math.round(job.xp / 4);
  // Hacker crew dampens heat.
  var heat = job.heat;
  if (s.crew.some(function (c) { return c.role === "hacker"; })) heat = Math.round(heat * 0.7);
  s.player.heat = clamp(s.player.heat + heat, 0, 100);
  s.stats.jobsDone++;
  s.stats.mastery[job.id] = (s.stats.mastery[job.id] || 0) + 1;
  if (s.stats.mastery[job.id] === 5) { s.player.respect += 25; T.toast(job.name + " mastered! +25 Respect", "good"); }
  // nudge control up in a random owned/contested district
  var ids = Object.keys(s.districts);
  var d = s.districts[pick(ids)];
  if (d.owner === "player" || d.owner === null) d.control = clamp(d.control + 2, 0, 100);
  T.toast("+" + T.money(pay) + " · +" + job.xp + " XP", "good");
  T.save();
  T.empire.render();
};

T.empire.tabCrew = function (body) {
  var s = T.state;
  body.appendChild(el("p", "muted", "Crew add attack & defence in fights and can be assigned to defend districts. They draw a weekly wage at upkeep."));
  // hire options
  var hire = el("div", "cards");
  Object.keys(T.CREW_ROLES).forEach(function (roleKey) {
    var role = T.CREW_ROLES[roleKey];
    var cost = (role.wage * 60) * T.pack().priceScale;
    var card = el("div", "card");
    var affordable = s.player.cash >= cost && s.player.respect >= role.hireRespect;
    card.innerHTML = "<h4>" + role.label + "</h4><div class='muted small'>" + role.desc + "</div>" +
      "<div class='row muted'><span>ATK " + role.atk + " · DEF " + role.def + "</span></div>" +
      "<div class='row'><span>Hire " + T.money(cost) + "</span><span class='muted'>" +
      (role.hireRespect ? role.hireRespect + " Respect" : "") + "</span></div>";
    var b = el("button", "btn", "Recruit");
    b.disabled = !affordable;
    b.onclick = function () {
      s.player.cash -= cost;
      s.crew.push({ id: "c_" + Math.random().toString(36).slice(2, 7),
        name: pick(T.pack().npcNames), role: roleKey, attack: role.atk, defense: role.def,
        loyalty: 70, wage: role.wage, assignedDistrict: null });
      T.toast("Recruited a " + role.label, "good"); T.save(); T.empire.render();
    };
    card.appendChild(b);
    hire.appendChild(card);
  });
  body.appendChild(el("h3", null, "Recruit"));
  body.appendChild(hire);

  body.appendChild(el("h3", null, "Your crew (" + s.crew.length + ")"));
  if (!s.crew.length) { body.appendChild(el("p", "muted", "No crew yet.")); return; }
  var list = el("div", "cards");
  s.crew.forEach(function (c) {
    var role = T.CREW_ROLES[c.role];
    var card = el("div", "card");
    card.innerHTML = "<h4>" + c.name + " <span class='muted small'>" + role.label + "</span></h4>" +
      "<div class='row muted'><span>ATK " + c.attack + " · DEF " + c.defense + "</span><span>Wage " + T.money(c.wage * T.pack().priceScale) + "/wk</span></div>" +
      "<div class='meter'><div class='meter-fill' style='width:" + c.loyalty + "%;background:" + (c.loyalty < 30 ? "#c0392b" : "#39b37a") + "'></div></div>" +
      "<div class='muted small'>Loyalty " + c.loyalty + (c.loyalty < 30 ? " — may quit or snitch!" : "") + "</div>";
    // assign to district
    var sel = el("select", "select");
    sel.appendChild(el("option", null, "— unassigned —"));
    T.pack().districts.forEach(function (d) {
      if (s.districts[d.id].owner === "player") {
        var o = el("option", null, d.name); o.value = d.id;
        if (c.assignedDistrict === d.id) o.selected = true;
        sel.appendChild(o);
      }
    });
    sel.onchange = function () { c.assignedDistrict = sel.value || null; T.save(); };
    var gift = el("button", "btn btn--ghost", "Gift (" + T.money(50 * T.pack().priceScale) + ") +Loyalty");
    gift.disabled = s.player.cash < 50 * T.pack().priceScale;
    gift.onclick = function () { s.player.cash -= 50 * T.pack().priceScale; c.loyalty = clamp(c.loyalty + 15, 0, 100); T.save(); T.empire.render(); };
    card.appendChild(sel); card.appendChild(gift);
    list.appendChild(card);
  });
  body.appendChild(list);
};

T.empire.tabProps = function (body) {
  var s = T.state, rankIdx = T.RANKS.indexOf(T.rankForLevel(s.player.level)) + 1;
  var pending = T.sim.pendingIncome();
  var collect = el("div", "banner-collect");
  collect.innerHTML = "<span>Uncollected income: <strong>" + T.money(pending) + "</strong></span>";
  var cb = el("button", "btn", "Collect all");
  cb.onclick = function () { var g = T.sim.collect(); T.toast(g > 0 ? "Collected " + T.money(g) : "Nothing to collect", g > 0 ? "good" : "warn"); T.empire.render(); };
  collect.appendChild(cb);
  body.appendChild(collect);

  body.appendChild(el("h3", null, "Buy a front"));
  var shop = el("div", "cards");
  T.PROPERTIES.forEach(function (tpl) {
    var cost = tpl.cost * T.pack().priceScale;
    var card = el("div", "card");
    var locked = rankIdx < tpl.minRank;
    card.innerHTML = "<h4>" + tpl.name + "</h4>" +
      "<div class='row muted'><span>" + T.money(tpl.income * T.pack().priceScale) + " / " + tpl.everySec + "s</span></div>" +
      "<div class='row'><span>" + T.money(cost) + "</span><span class='muted'>" + (locked ? "Rank " + tpl.minRank : "") + "</span></div>";
    var b = el("button", "btn", "Buy");
    b.disabled = locked || s.player.cash < cost;
    b.onclick = function () {
      s.player.cash -= cost;
      // place it in a district the player owns, else the starter district
      var owned = T.pack().districts.filter(function (d) { return s.districts[d.id].owner === "player"; });
      var dist = (owned[0] || T.pack().districts[0]).id;
      s.properties.push({ tplId: tpl.id, districtId: dist, level: 1, lastCollect: now() });
      T.toast("Bought a " + tpl.name, "good"); T.save(); T.empire.render();
    };
    card.appendChild(b);
    if (locked) card.classList.add("card--locked");
    shop.appendChild(card);
  });
  body.appendChild(shop);

  body.appendChild(el("h3", null, "Owned (" + s.properties.length + ")"));
  if (!s.properties.length) { body.appendChild(el("p", "muted", "You own no property yet.")); return; }
  var list = el("div", "cards");
  s.properties.forEach(function (p, i) {
    var tpl = T.PROPERTIES.filter(function (x) { return x.id === p.tplId; })[0];
    var dName = T.pack().districts.filter(function (d) { return d.id === p.districtId; })[0].name;
    var card = el("div", "card");
    card.innerHTML = "<h4>" + tpl.name + " <span class='muted small'>Lv " + p.level + "</span></h4>" +
      "<div class='muted small'>" + dName + " · " + T.money(tpl.income * p.level * T.pack().priceScale) + " / " + tpl.everySec + "s</div>";
    var up = el("button", "btn btn--ghost", "Upgrade " + T.money(Math.round(tpl.cost * 0.6 * p.level) * T.pack().priceScale));
    var upCost = Math.round(tpl.cost * 0.6 * p.level) * T.pack().priceScale;
    up.disabled = s.player.cash < upCost;
    up.onclick = function () { s.player.cash -= upCost; p.level++; T.save(); T.empire.render(); };
    card.appendChild(up);
    list.appendChild(card);
  });
  body.appendChild(list);
};

T.empire.tabDistricts = function (body) {
  var s = T.state, pk = T.pack();
  body.appendChild(el("p", "muted", "Push control to 100% to own a district. Jobs and collections raise it; rivals push it down. Assign crew (Crew tab) to defend."));
  var list = el("div", "cards");
  pk.districts.forEach(function (d) {
    var st = s.districts[d.id];
    var ownerName = st.owner === "player" ? "You" :
      st.owner === null ? "Unclaimed" :
      (pk.rivals.filter(function (r) { return r.id === st.owner; })[0] || { name: "Rival" }).name;
    var card = el("div", "card");
    card.innerHTML = "<h4><span class='dot' style='background:" + d.color + "'></span>" + d.name + "</h4>" +
      "<div class='muted small'>" + d.type + " · income " + T.money(d.income * T.pack().priceScale) + "/day · owner: " + ownerName + "</div>" +
      "<div class='meter'><div class='meter-fill' style='width:" + st.control + "%;background:" + (st.owner === "player" ? "#39b37a" : "#c0392b") + "'></div></div>" +
      "<div class='muted small'>Control " + Math.round(st.control) + "% · crew here: " + crewIn(d.id) + "</div>";
    if (st.owner !== "player") {
      var push = el("button", "btn", "Move in (5 ⚡)");
      push.disabled = s.resources.energy < 5;
      push.onclick = function () {
        s.resources.energy -= 5;
        st.control = clamp(st.control + randint(8, 16), 0, 100);
        s.player.heat = clamp(s.player.heat + 4, 0, 100);
        if (st.control >= 100) { st.owner = "player"; st.control = 100; s.player.respect += 40; T.toast("Took over " + d.name + "!", "good"); }
        else T.toast(d.name + " control " + Math.round(st.control) + "%", "good");
        T.save(); T.empire.render();
      };
      card.appendChild(push);
      var war = el("button", "btn btn--ghost", "Turf war (fight it)");
      war.disabled = s.resources.stamina < 3;
      war.onclick = function () { T.street.startMission("m_turf", { districtId: d.id, name: "Turf war: " + d.name }); };
      card.appendChild(war);
    }
    list.appendChild(card);
  });
  body.appendChild(list);
};

T.empire.tabFight = function (body) {
  var s = T.state, pk = T.pack();
  body.appendChild(el("p", "muted", "Attack a rival crew. Outcome = your attack+crew vs their defence, plus a little luck. Costs stamina."));
  var myAtk = 10 + s.crew.reduce(function (a, c) { return a + c.attack; }, 0) + s.player.level * 2;
  body.appendChild(el("div", "kpi", "Your strength: <strong>" + myAtk + "</strong> · Stamina " + Math.floor(s.resources.stamina) + "/" + s.resources.staminaMax));
  var list = el("div", "cards");
  pk.rivals.forEach(function (r, i) {
    var def = 12 + i * 10 + s.player.level * 2;
    var card = el("div", "card");
    card.innerHTML = "<h4><span class='dot' style='background:" + r.color + "'></span>" + r.name + "</h4>" +
      "<div class='muted small'>Defence ~" + def + "</div>";
    var b = el("button", "btn", "Attack (3 stamina)");
    b.disabled = s.resources.stamina < 3;
    b.onclick = function () {
      s.resources.stamina -= 3; s.stats.fights++;
      var roll = myAtk + rand(-8, 8) - def;
      if (roll > 0) {
        var loot = randint(100, 400) * T.pack().priceScale + def * 3 * T.pack().priceScale;
        s.player.cash += loot; s.player.respect += 15; s.player.heat = clamp(s.player.heat + 8, 0, 100);
        T.sim.addXp(20);
        T.toast("Beat " + r.name + "! +" + T.money(loot) + ", +15 Respect", "good");
      } else {
        s.resources.health = clamp(s.resources.health - randint(10, 30), 0, s.resources.healthMax);
        s.player.respect = Math.max(0, s.player.respect - 8);
        T.toast("Lost the fight with " + r.name, "bad");
        if (s.resources.health <= 0) T.ui.clinic();
      }
      T.save(); T.empire.render();
    };
    card.appendChild(b);
    list.appendChild(card);
  });
  body.appendChild(list);
};

T.empire.tabInventory = function (body) {
  var s = T.state;
  body.appendChild(el("h3", null, "Items"));
  if (!s.inventory.items.length) body.appendChild(el("p", "muted", "No items. Steal cars in Street mode to sell at the chop shop."));
  else {
    var il = el("div", "cards");
    s.inventory.items.forEach(function (it) { il.appendChild(el("div", "card", "<h4>" + it + "</h4>")); });
    body.appendChild(il);
  }
  body.appendChild(el("h3", null, "Flyers (" + s.inventory.flyers.length + ")"));
  body.appendChild(el("p", "muted", "Flyers you picked up. Tap to view the ad again. Daily reward cap: " + s.flyersToday + "/3."));
  if (!s.inventory.flyers.length) { body.appendChild(el("p", "muted", "No flyers yet — pick them up in Street mode.")); }
  else {
    var fl = el("div", "cards");
    s.inventory.flyers.forEach(function (f) {
      var ad = JSON.parse(f);
      var card = el("div", "card flyer-card");
      card.style.background = ad.bg; card.style.color = ad.fg;
      card.innerHTML = "<h4>" + (ad.brand || "Flyer") + "</h4><div class='small'>" + (ad.text || "") + "</div>";
      card.onclick = function () { T.ui.flyer(ad, true); };
      fl.appendChild(card);
    });
    body.appendChild(fl);
  }
};

T.empire.tabProfile = function (body) {
  var s = T.state, rk = T.rankForLevel(s.player.level);
  body.appendChild(el("div", "card",
    "<h4>" + s.player.name + "</h4>" +
    "<div class='muted'>" + s.player.look + " · " + T.pack().city + " (" + T.pack().country + ")</div>" +
    "<div class='muted small'>Rank: " + rk.name + " — " + rk.unlock + "</div>" +
    "<div class='muted small'>Jobs done: " + s.stats.jobsDone + " · Fights: " + s.stats.fights + "</div>"));
  var owned = Object.keys(s.districts).filter(function (id) { return s.districts[id].owner === "player"; }).length;
  body.appendChild(el("div", "kpi", "Districts owned: <strong>" + owned + "/" + T.pack().districts.length + "</strong>"));

  if (owned === T.pack().districts.length && s.player.level >= 41) {
    var prestige = el("button", "btn", "Prestige (retire & restart with a bonus)");
    prestige.onclick = function () { if (confirm("Retire as Kingpin and start fresh with a permanent income bonus?")) { T.toast("Prestige coming in v2 — badge earned!", "good"); } };
    body.appendChild(prestige);
  }

  body.appendChild(el("h3", null, "Save"));
  var tools = el("div", "row");
  var exp = el("button", "btn btn--ghost", "Export save code");
  exp.onclick = function () { var c = T.exportCode(); prompt("Copy this save code:", c); };
  var imp = el("button", "btn btn--ghost", "Import save code");
  imp.onclick = function () { var c = prompt("Paste a save code:"); if (c && T.importCode(c)) { T.toast("Loaded.", "good"); location.reload(); } else if (c) T.toast("Invalid code", "bad"); };
  var prem = el("button", "btn btn--ghost", s.premium ? "Premium: on" : "Toggle premium (demo)");
  prem.onclick = function () { s.premium = !s.premium; var b = $("#hd-banner"); if (b) delete b.dataset.filled; T.toast("Premium " + (s.premium ? "on — paid billboards become parody" : "off"), "good"); T.save(); T.empire.render(); };
  var reset = el("button", "btn btn--danger", "Delete save");
  reset.onclick = function () { if (confirm("Delete your save and start over?")) { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} location.reload(); } };
  tools.appendChild(exp); tools.appendChild(imp); tools.appendChild(prem); tools.appendChild(reset);
  body.appendChild(tools);
};

/* Make a small, well-tuned module boundary visible to the rest of the file. */
window.TURF = T;
})();
