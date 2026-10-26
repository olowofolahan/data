/* ==========================================================================
 * Turf — Street mode (the GTA side)
 * --------------------------------------------------------------------------
 * A real-time, top-down view drawn on an HTML5 canvas over a generated tile
 * city. On foot or in a stolen car, with pedestrians, traffic, police, a
 * 0..5 Heat-star system, billboards & flyer walls, and the design's five
 * street-mission types. All graphics are procedural — no external assets.
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var now = function () { return Date.now(); };
var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
var rand = function (a, b) { return a + Math.random() * (b - a); };
var randint = function (a, b) { return Math.floor(rand(a, b + 1)); };
var pick = function (a) { return a[randint(0, a.length - 1)]; };

var TILE = 32;
var MAP_W = 56, MAP_H = 48;
var ROAD = 0, SIDEWALK = 1, BUILDING = 2;

var S = {
  built: false, canvas: null, ctx: null, mini: null, mctx: null,
  grid: null, districtOf: null, pois: [], billboards: [], flyerWalls: [],
  cars: [], peds: [], police: [], flyerPickups: [],
  player: null, cam: { x: 0, y: 0 },
  keys: {}, touch: { x: 0, y: 0, active: false }, actionHeld: false,
  stars: 0, lastCrime: 0, mission: null, msg: "", msgUntil: 0,
  tracers: [], lastConvert: 0, nearGunShop: false, pastorDeadUntil: 0,
  running: false, lastFrame: 0
};
T.street = { _S: S };

/* ---------------------- world generation -------------------------------- */
function buildWorld() {
  var g = [];
  for (var y = 0; y < MAP_H; y++) { g[y] = []; for (var x = 0; x < MAP_W; x++) g[y][x] = BUILDING; }
  var BLOCK = 8;
  // Roads on a grid (2 tiles wide).
  for (y = 0; y < MAP_H; y++) for (x = 0; x < MAP_W; x++) {
    if ((x % BLOCK === 0 || x % BLOCK === 1) || (y % BLOCK === 0 || y % BLOCK === 1)) g[y][x] = ROAD;
  }
  // Sidewalk ring around each block's building interior.
  for (y = 1; y < MAP_H - 1; y++) for (x = 1; x < MAP_W - 1; x++) {
    if (g[y][x] === BUILDING) {
      if (g[y - 1][x] === ROAD || g[y + 1][x] === ROAD || g[y][x - 1] === ROAD || g[y][x + 1] === ROAD)
        g[y][x] = SIDEWALK;
    }
  }
  S.grid = g;

  // District regions: 3 columns x 2 rows mapped onto the 6 pack districts.
  var pk = T.pack();
  S.districtOf = [];
  for (y = 0; y < MAP_H; y++) {
    S.districtOf[y] = [];
    for (x = 0; x < MAP_W; x++) {
      var col = Math.min(2, Math.floor(x / (MAP_W / 3)));
      var row = Math.min(1, Math.floor(y / (MAP_H / 2)));
      var idx = row * 3 + col;
      S.districtOf[y][x] = pk.districts[idx] ? pk.districts[idx].id : pk.districts[0].id;
    }
  }

  // POIs placed on sidewalk tiles that touch a road.
  var sidewalks = [];
  for (y = 2; y < MAP_H - 2; y++) for (x = 2; x < MAP_W - 2; x++)
    if (g[y][x] === SIDEWALK) sidewalks.push({ x: x, y: y });
  function grabPoi(kind, color, label) {
    var t = sidewalks.splice(randint(0, sidewalks.length - 1), 1)[0];
    S.pois.push({ kind: kind, color: color, label: label, x: t.x * TILE + TILE / 2, y: t.y * TILE + TILE / 2 });
    return t;
  }
  grabPoi("safehouse", "#2ecc71", "Safehouse");
  grabPoi("chop", "#e67e22", "Chop shop");
  grabPoi("respray", "#3498db", "Respray");
  grabPoi("clinic", "#e74c3c", "Clinic");
  grabPoi("gun", "#95a5a6", "Gun shop");
  grabPoi("garage", "#7f8c8d", "Garage");

  // Billboards: pick building tiles adjacent to road; give price tiers.
  S.billboards = [];
  var tiers = ["A", "B", "C"];
  for (var i = 0; i < 10; i++) {
    for (var tries = 0; tries < 50; tries++) {
      var bx = randint(3, MAP_W - 4), by = randint(3, MAP_H - 4);
      if (g[by][bx] === BUILDING &&
          (g[by + 1][bx] === ROAD || g[by + 1][bx] === SIDEWALK)) {
        S.billboards.push({ id: "bb_" + i, x: bx * TILE, y: by * TILE + TILE - 8,
          w: 64, h: 32, tier: tiers[i % 3], ad: null });
        break;
      }
    }
  }
  // Flyer walls on some sidewalks.
  S.flyerWalls = [];
  for (i = 0; i < 6; i++) {
    var t = sidewalks[randint(0, sidewalks.length - 1)];
    S.flyerWalls.push({ x: t.x * TILE + TILE / 2, y: t.y * TILE + TILE / 2, used: false });
  }

  // Player starts at the safehouse.
  var sh = S.pois.filter(function (p) { return p.kind === "safehouse"; })[0];
  S.player = { x: sh.x, y: sh.y, angle: 0, hp: T.state.resources.health, car: null, atkCd: 0 };

  // Parked cars along roadsides.
  S.cars = [];
  for (i = 0; i < 26; i++) spawnParkedCar();
  // Traffic.
  for (i = 0; i < 10; i++) spawnTraffic();
  // Pedestrians.
  S.peds = [];
  for (i = 0; i < 24; i++) spawnPed(false);
  spawnPastor();

  S.tracers = []; S.lastConvert = now(); S.pastorDeadUntil = 0;
  S.built = true;
}

function tileAt(px, py) {
  var tx = Math.floor(px / TILE), ty = Math.floor(py / TILE);
  if (tx < 0 || ty < 0 || tx >= MAP_W || ty >= MAP_H) return BUILDING;
  return S.grid[ty][tx];
}
function walkable(px, py) { return tileAt(px, py) !== BUILDING; }
function drivable(px, py) { return tileAt(px, py) === ROAD; }

function randRoadTile() {
  for (var i = 0; i < 200; i++) {
    var x = randint(1, MAP_W - 2), y = randint(1, MAP_H - 2);
    if (S.grid[y][x] === ROAD) return { x: x * TILE + TILE / 2, y: y * TILE + TILE / 2 };
  }
  return { x: TILE * 2, y: TILE * 2 };
}
function spawnParkedCar() {
  var pk = T.pack(), v = pick(pk.vehicles);
  // place on a road tile that borders a sidewalk (kerbside)
  for (var i = 0; i < 60; i++) {
    var x = randint(2, MAP_W - 3), y = randint(2, MAP_H - 3);
    if (S.grid[y][x] === ROAD &&
        (S.grid[y][x + 1] === SIDEWALK || S.grid[y][x - 1] === SIDEWALK ||
         S.grid[y + 1][x] === SIDEWALK || S.grid[y - 1][x] === SIDEWALK)) {
      S.cars.push({ x: x * TILE + TILE / 2, y: y * TILE + TILE / 2, angle: rand(0, 6.28),
        vx: 0, vy: 0, type: v, color: v.color, hp: 100, parked: true, driver: null });
      return;
    }
  }
}
function spawnTraffic() {
  var pk = T.pack(), v = pick(pk.vehicles), t = randRoadTile();
  var dir = pick([[1, 0], [-1, 0], [0, 1], [0, -1]]);
  S.cars.push({ x: t.x, y: t.y, angle: Math.atan2(dir[1], dir[0]),
    vx: dir[0], vy: dir[1], type: v, color: v.color, hp: 100, parked: false,
    driver: {}, dir: dir });
}
function spawnPed(hostile) {
  var pk = T.pack();
  // spawn on a sidewalk
  for (var i = 0; i < 60; i++) {
    var x = randint(2, MAP_W - 3), y = randint(2, MAP_H - 3);
    if (S.grid[y][x] === SIDEWALK) {
      S.peds.push({ x: x * TILE + TILE / 2, y: y * TILE + TILE / 2,
        dir: pick([[1, 0], [-1, 0], [0, 1], [0, -1]]), hp: hostile ? 40 : 20,
        hostile: hostile, flee: 0, color: hostile ? pick(pk.rivals).color : "#dcd3c2",
        name: pick(pk.npcNames) });
      return S.peds[S.peds.length - 1];
    }
  }
  return null;
}
function spawnPolice() {
  var t = randRoadTile();
  S.police.push({ x: t.x, y: t.y, angle: 0, hp: 60, color: "#1f3a93", contact: 0 });
}
function spawnPastor() {
  var ped = spawnPed(false);
  if (!ped) return;
  ped.preacher = true; ped.hostile = false; ped.hp = 60;
  ped.color = "#f3ecd8"; ped.name = "Pastor";
  ped.bubble = pick(T.PASTOR_LINES); ped.bubbleUntil = now() + 4000;
}
function spawnConvert() {
  // Prefer converting an existing nearby civilian; else spawn a fresh one.
  var p = S.player, chosen = null, bd = 420;
  S.peds.forEach(function (ped) {
    if (ped.hostile || ped.preacher || ped.convert) return;
    var d = Math.hypot(ped.x - p.x, ped.y - p.y);
    if (d < bd && d > 60) { bd = d; chosen = ped; }
  });
  if (!chosen) { chosen = spawnPed(false); if (!chosen) return; chosen.x = p.x + rand(-260, 260); chosen.y = p.y + rand(-260, 260); if (!walkable(chosen.x, chosen.y)) { chosen.x = p.x; chosen.y = p.y + 120; } }
  chosen.convert = true; chosen.state = "approach"; chosen.color = "#9ad0ff"; chosen.flee = 0;
  chosen.name = pick(T.pack().npcNames);
  chosen.bubble = "Boss... I need to talk to you."; chosen.bubbleUntil = now() + 5000;
  S.lastConvert = now();
}

/* ---------------------- input ------------------------------------------- */
function bindInput() {
  window.addEventListener("keydown", function (e) {
    if (T.game.mode !== "street") return;
    S.keys[e.key.toLowerCase()] = true;
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].indexOf(e.key.toLowerCase()) >= 0) e.preventDefault();
    if (e.key.toLowerCase() === "e") tryEnterExit();
    if (e.key.toLowerCase() === "q") switchWeapon();
    if (e.key.toLowerCase() === "b" && S.nearGunShop) T.ui.gunShop();
    if (e.key.toLowerCase() === "m") T.toast("Minimap is bottom-left", "warn");
  });
  window.addEventListener("keyup", function (e) { S.keys[e.key.toLowerCase()] = false; });

  // Touch joystick
  var joy = document.getElementById("joy");
  if (joy) {
    var base = joy.getBoundingClientRect, center = null;
    var start = function (ev) { S.touch.active = true; var r = joy.getBoundingClientRect(); center = { x: r.left + r.width / 2, y: r.top + r.height / 2 }; move(ev); };
    var move = function (ev) {
      if (!S.touch.active) return;
      var p = ev.touches ? ev.touches[0] : ev;
      var dx = p.clientX - center.x, dy = p.clientY - center.y;
      var len = Math.hypot(dx, dy) || 1, max = 40;
      S.touch.x = dx / Math.max(len, max); S.touch.y = dy / Math.max(len, max);
      var kn = document.getElementById("joy-knob");
      if (kn) { kn.style.transform = "translate(" + clamp(dx, -max, max) + "px," + clamp(dy, -max, max) + "px)"; }
    };
    var end = function () { S.touch.active = false; S.touch.x = S.touch.y = 0; var kn = document.getElementById("joy-knob"); if (kn) kn.style.transform = "translate(0,0)"; };
    joy.addEventListener("touchstart", start); joy.addEventListener("touchmove", move); joy.addEventListener("touchend", end);
    joy.addEventListener("mousedown", start); window.addEventListener("mousemove", move); window.addEventListener("mouseup", end);
  }
  var bind = function (id, down, up) {
    var b = document.getElementById(id); if (!b) return;
    var d = function (e) { e.preventDefault(); down(); }; var u = function (e) { e.preventDefault(); if (up) up(); };
    b.addEventListener("touchstart", d); b.addEventListener("touchend", u);
    b.addEventListener("mousedown", d); b.addEventListener("mouseup", u);
  };
  bind("btn-action", function () { S.actionHeld = true; doAttack(); }, function () { S.actionHeld = false; });
  bind("btn-enter", function () { tryEnterExit(); });
  bind("btn-weapon", function () { switchWeapon(); });
  bind("btn-shop", function () { if (S.nearGunShop) T.ui.gunShop(); else T.toast("Stand by the gun shop", "warn"); });
}

/* ---------------------- player actions ---------------------------------- */
function tryEnterExit() {
  var p = S.player;
  if (p.car) {
    // exit
    p.car.parked = true; p.car.vx = p.car.vy = 0; p.car = null;
    T.toast("Out of the car", "warn");
    return;
  }
  // find nearest car within 44px
  var best = null, bd = 44;
  S.cars.forEach(function (c) { var d = Math.hypot(c.x - p.x, c.y - p.y); if (d < bd) { bd = d; best = c; } });
  if (best) {
    if (!best.parked) { addStars(1); T.toast("Pulled the driver out!", "bad"); best.driver = null; }
    best.parked = false; p.car = best;
    if (S.mission && S.mission.kind === "cartheft" && !S.mission.hasCar) { S.mission.hasCar = true; setMsg("Car secured — get to the chop shop"); }
    T.toast("Driving a " + best.type.name, "good");
  } else T.toast("No car nearby", "warn");
}
function doAttack() {
  var p = S.player; if (p.atkCd > 0) return;
  var w = T.weaponById(T.state.equipped);
  p.atkCd = w.cooldown;
  if (w.type === "gun") {
    var ammo = T.state.ammo[w.id] || 0;
    if (ammo <= 0) {
      if (!S._noAmmo || now() - S._noAmmo > 1500) { T.toast("Out of ammo for the " + w.name, "warn"); S._noAmmo = now(); }
      return;
    }
    T.state.ammo[w.id] = ammo - 1;
    fireGun(w);
    addStars(w.id === "pistol" ? 1 : 2); // guns are loud
  } else {
    meleeHit(w);
  }
}
function angleDiff(a, b) { var d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }
function onPedDamaged(ped) {
  ped.flee = ped.flee || 120;
  if (ped.preacher || ped.convert) { T.state.player.respect = Math.max(0, T.state.player.respect - 5); if (!S._badBiz || now() - S._badBiz > 2000) { T.toast("Rough on a man of God — bad for business.", "warn"); S._badBiz = now(); } addStars(1); }
  else if (!ped.hostile) { addStars(1); } // hitting a civilian is a crime
}
function cleanupDead() {
  for (var i = S.peds.length - 1; i >= 0; i--) {
    if (S.peds[i].hp <= 0) {
      var d = S.peds[i];
      if (d.hostile && S.mission && S.mission.kind === "turf") S.mission.killed = (S.mission.killed || 0) + 1;
      if (d.preacher) S.pastorDeadUntil = now() + 30000;
      S.peds.splice(i, 1);
    }
  }
  for (var j = S.police.length - 1; j >= 0; j--) if (S.police[j].hp <= 0) S.police.splice(j, 1);
}
function meleeHit(w) {
  var p = S.player;
  S.peds.forEach(function (ped) { if (Math.hypot(ped.x - p.x, ped.y - p.y) < w.range) { ped.hp -= w.damage; onPedDamaged(ped); } });
  S.police.forEach(function (po) { if (Math.hypot(po.x - p.x, po.y - p.y) < w.range) { po.hp -= w.damage; addStars(1); } });
  cleanupDead();
}
function fireGun(w) {
  var p = S.player, aim = p.angle, tol = 0.55 + w.spread;
  var cand = [];
  S.peds.forEach(function (e) { cand.push({ e: e, kind: "ped" }); });
  S.police.forEach(function (e) { cand.push({ e: e, kind: "pol" }); });
  var hits = cand.map(function (c) {
    var dx = c.e.x - p.x, dy = c.e.y - p.y, d = Math.hypot(dx, dy);
    return { c: c, d: d, diff: Math.abs(angleDiff(Math.atan2(dy, dx), aim)) };
  }).filter(function (h) { return h.d <= w.range && h.diff <= tol; }).sort(function (a, b) { return a.d - b.d; });

  var endX = p.x + Math.cos(aim) * w.range, endY = p.y + Math.sin(aim) * w.range;
  if (hits.length) { aim = Math.atan2(hits[0].c.e.y - p.y, hits[0].c.e.x - p.x); p.angle = aim; endX = hits[0].c.e.x; endY = hits[0].c.e.y; }
  var n = Math.max(1, Math.min(w.pellets, hits.length));
  for (var i = 0; i < n; i++) {
    if (!hits[i]) break;
    hits[i].c.e.hp -= w.damage;
    if (hits[i].c.kind === "ped") onPedDamaged(hits[i].c.e); else addStars(1);
  }
  // muzzle tracers (spread for the shotgun feel)
  var pel = w.pellets > 1 ? w.pellets : 1;
  for (var k = 0; k < pel; k++) {
    var j = (Math.random() - 0.5) * (w.spread + 0.05);
    S.tracers.push({ x1: p.x, y1: p.y, x2: p.x + Math.cos(aim + j) * (w.range * 0.92), y2: p.y + Math.sin(aim + j) * (w.range * 0.92), until: now() + 70 });
  }
  cleanupDead();
}
function switchWeapon() {
  var owned = T.WEAPONS.filter(function (w) { return T.state.weapons[w.id]; });
  if (owned.length <= 1) { T.toast("Only fists for now — buy a weapon", "warn"); return; }
  var idx = owned.map(function (w) { return w.id; }).indexOf(T.state.equipped);
  var next = owned[(idx + 1) % owned.length];
  T.state.equipped = next.id; T.save();
  T.toast("Equipped " + next.name + (next.type === "gun" ? " (" + (T.state.ammo[next.id] || 0) + ")" : ""), "good");
}
function addStars(n) {
  S.stars = clamp(S.stars + n, 0, 5);
  S.lastCrime = now();
  T.state.player.heat = clamp(T.state.player.heat + n * 4, 0, 100);
}

/* ---------------------- missions ---------------------------------------- */
T.street.startMission = function (missionId, job) {
  var def = T.MISSIONS[missionId];
  if (!def) { T.toast("No such mission", "bad"); return; }
  var energy = job && job.energy ? job.energy : 4;
  if (missionId === "m_turf" && job && job.districtId) {
    if (T.state.resources.stamina < 3) { T.toast("Need 3 stamina", "warn"); return; }
    T.state.resources.stamina -= 3;
  } else if (T.state.resources.energy < energy) { T.toast("Not enough energy", "warn"); return; }
  else T.state.resources.energy -= energy;

  T.game.setMode("street");
  if (!S.built) buildWorld();

  var m = { kind: def.kind, job: job || null, startedAt: now(), timer: 0 };
  var P = S.player;
  if (def.kind === "delivery") {
    m.pickup = randRoadTile(); m.dropoff = randRoadTile(); m.stage = "pickup"; m.timeLimit = 70;
    setMsg("Pick up the package (yellow marker)");
  } else if (def.kind === "collection") {
    m.stops = []; for (var i = 0; i < 3; i++) m.stops.push(Object.assign(randRoadTile(), { done: false }));
    setMsg("Collect from 3 shops (yellow markers)");
  } else if (def.kind === "turf") {
    m.target = 4; m.killed = 0; m.district = job && job.districtId;
    for (i = 0; i < 4; i++) { var h = spawnPed(true); if (h) { h.x = P.x + rand(-160, 160); h.y = P.y + rand(-160, 160); if (!walkable(h.x, h.y)) { h.x = P.x; h.y = P.y + 80; } } }
    setMsg("Clear 4 rival gangsters (red) from the block");
  } else if (def.kind === "cartheft") {
    m.hasCar = false; m.chop = S.pois.filter(function (p) { return p.kind === "chop"; })[0];
    setMsg("Steal any car, then reach the chop shop");
  }
  S.mission = m;
  T.toast("Mission: " + def.label, "good");
};
function finishMission(win) {
  var m = S.mission; if (!m) return;
  S.mission = null;
  if (win) {
    var job = m.job;
    var pay = job && job.cashMax ? randint(job.cashMin, job.cashMax) * T.pack().priceScale * 1.6 : randint(200, 500) * T.pack().priceScale;
    pay = Math.round(pay);
    T.state.player.cash += pay;
    T.sim.addXp(job && job.xp ? Math.round(job.xp * 1.5) : 30);
    T.state.player.respect += 20;
    if (m.kind === "turf" && m.district) {
      var st = T.state.districts[m.district];
      st.control = clamp(st.control + 40, 0, 100);
      if (st.control >= 100) { st.owner = "player"; st.control = 100; T.state.player.respect += 40; }
    }
    if (m.kind === "cartheft" && S.player.car) {
      T.state.inventory.items.push(S.player.car.type.name + " (hot)");
      S.player.car = null;
    }
    T.toast("Mission done! +" + T.money(pay), "good");
    setMsg("Mission complete — nice work");
  } else {
    T.toast("Mission failed", "bad");
    setMsg("Mission failed");
  }
  T.state.resources.health = S.player.hp;
  T.save();
}
function setMsg(t) { S.msg = t; S.msgUntil = now() + 6000; }

/* ---------------------- update ------------------------------------------ */
function update(dt) {
  var p = S.player;
  if (p.atkCd > 0) p.atkCd--;

  // movement vector
  var mx = 0, my = 0;
  if (S.keys["w"] || S.keys["arrowup"]) my -= 1;
  if (S.keys["s"] || S.keys["arrowdown"]) my += 1;
  if (S.keys["a"] || S.keys["arrowleft"]) mx -= 1;
  if (S.keys["d"] || S.keys["arrowright"]) mx += 1;
  if (S.touch.active) { mx += S.touch.x; my += S.touch.y; }
  if (S.keys[" "]) doAttack();
  var len = Math.hypot(mx, my);
  if (len > 1) { mx /= len; my /= len; }

  if (p.car) {
    var c = p.car, spd = c.type.speed * 2.2;
    if (len > 0.1) { c.angle = Math.atan2(my, mx); }
    var nx = c.x + mx * spd, ny = c.y + my * spd;
    if (len > 0.1) {
      if (drivable(nx, c.y) || walkable(nx, c.y)) c.x = nx;
      if (drivable(c.x, ny) || walkable(c.x, ny)) c.y = ny;
    }
    p.x = c.x; p.y = c.y; p.angle = c.angle;
    // car runs over hostiles/police? run over civ = crime
    S.peds.forEach(function (ped, i) { if (Math.hypot(ped.x - c.x, ped.y - c.y) < 20 && len > 0.2) { ped.hp -= 40; if (!ped.hostile) addStars(1); if (ped.hp <= 0) { if (ped.hostile && S.mission && S.mission.kind === "turf") S.mission.killed = (S.mission.killed || 0) + 1; S.peds.splice(i, 1); } } });
  } else {
    var pspd = 1.7;
    var nx2 = p.x + mx * pspd, ny2 = p.y + my * pspd;
    if (len > 0.1) { p.angle = Math.atan2(my, mx); }
    if (walkable(nx2, p.y)) p.x = nx2;
    if (walkable(p.x, ny2)) p.y = ny2;
  }

  // POI interactions
  S.pois.forEach(function (poi) {
    var d = Math.hypot(poi.x - p.x, poi.y - p.y);
    if (d < 26) {
      if (poi.kind === "safehouse") { if (p.hp < T.state.resources.healthMax) { p.hp = T.state.resources.healthMax; T.state.resources.health = p.hp; T.save(); setMsg("Healed & saved at the safehouse"); } }
      else if (poi.kind === "respray" && p.car && S.stars > 0) { S.stars = 0; T.state.player.heat = clamp(T.state.player.heat - 30, 0, 100); p.car.color = pick(["#555", "#888", "#2c3e50", "#16a085"]); setMsg("Resprayed — Heat shaken off"); }
      else if (poi.kind === "chop" && p.car) {
        if (S.mission && S.mission.kind === "cartheft" && S.mission.hasCar) { finishMission(true); }
        else { var val = p.car.type.value * T.pack().priceScale; T.state.player.cash += val; T.toast("Sold the " + p.car.type.name + " for " + T.money(val), "good"); p.car = null; T.save(); }
      }
      else if (poi.kind === "clinic" && p.hp < T.state.resources.healthMax) { var fee = 50 * T.pack().priceScale; if (T.state.player.cash >= fee) { T.state.player.cash -= fee; p.hp = T.state.resources.healthMax; T.state.resources.health = p.hp; setMsg("Patched up (" + T.money(fee) + ")"); } }
    }
  });

  // flyer walls
  S.flyerWalls.forEach(function (fw) {
    if (!fw.used && Math.hypot(fw.x - p.x, fw.y - p.y) < 26) {
      fw.used = true;
      var ad = T.ads.pick("flyer", null, "wall_" + Math.round(fw.x) + "_" + Math.round(fw.y));
      T.ui.flyer(ad, false);
      setTimeout(function () { fw.used = false; }, 30000); // refreshes later
    }
  });

  // pedestrians (incl. the Pastor and born-again converts)
  S.peds.forEach(function (ped) {
    var speed = ped.flee > 0 ? 1.6 : 0.6;
    var roam = ped.hostile || ped.convert; // these may cross roads, not just sidewalks
    if (ped.flee > 0) { ped.flee--; var ax = p.x - ped.x, ay = p.y - ped.y, al = Math.hypot(ax, ay) || 1; ped.dir = [-ax / al, -ay / al]; }
    else if (Math.random() < 0.02) ped.dir = pick([[1, 0], [-1, 0], [0, 1], [0, -1]]);

    if (ped.preacher) {
      if (now() > ped.bubbleUntil) { ped.bubble = pick(T.PASTOR_LINES); ped.bubbleUntil = now() + rand(3500, 6000); }
    }
    if (ped.hostile) { var hx = p.x - ped.x, hy = p.y - ped.y, hl = Math.hypot(hx, hy) || 1; if (hl < 220) { ped.dir = [hx / hl, hy / hl]; speed = 1.1; if (hl < 26 && p.atkCd === 0 && Math.random() < 0.05) { p.hp -= 6; } } }

    if (ped.convert && ped.state === "approach") {
      var cx = p.x - ped.x, cy = p.y - ped.y, cl = Math.hypot(cx, cy) || 1;
      ped.dir = [cx / cl, cy / cl]; speed = 1.3; ped.flee = 0;
      if (cl < 30 && !T.ui._convertOpen) {
        ped.state = "preached";
        var scr = T.SCRIPTURES[Math.floor(Math.random() * T.SCRIPTURES.length)];
        T.ui.bornAgain(ped.name, scr, function () { ped.state = "leave"; ped.flee = 300; });
      }
    }
    if (ped.state === "leave" && ped.flee <= 0) { ped.remove = true; }

    var nx = ped.x + ped.dir[0] * speed, ny = ped.y + ped.dir[1] * speed;
    if (roam ? walkable(nx, ped.y) : (tileAt(nx, ped.y) === SIDEWALK)) ped.x = nx; else ped.dir[0] *= -1;
    if (roam ? walkable(ped.x, ny) : (tileAt(ped.x, ny) === SIDEWALK)) ped.y = ny; else ped.dir[1] *= -1;
  });
  // retire converts that have wandered off
  for (var pi = S.peds.length - 1; pi >= 0; pi--) if (S.peds[pi].remove) S.peds.splice(pi, 1);

  // the Pastor's flock: spawn a convert now and then (not during a mission)
  if (!T.ui._convertOpen && !S.mission && now() - S.lastConvert > 55000 &&
      !S.peds.some(function (c) { return c.convert && (c.state === "approach" || c.state === "preached"); }) &&
      Math.random() < 0.012) spawnConvert();
  // keep one Pastor on the streets
  if (now() > S.pastorDeadUntil && !S.peds.some(function (c) { return c.preacher; }) && Math.random() < 0.03) spawnPastor();

  // gun shop proximity (open with B / the Guns button)
  var gun = S.pois.filter(function (x) { return x.kind === "gun"; })[0];
  S.nearGunShop = gun && Math.hypot(gun.x - p.x, gun.y - p.y) < 40;
  // keep a baseline pedestrian count (fewer at night)
  var want = T.sim.isNight() ? 12 : 22;
  if (S.peds.length < want && Math.random() < 0.05) spawnPed(false);

  // traffic
  S.cars.forEach(function (c) {
    if (c.parked || c === (S.player.car)) return;
    var nx = c.x + c.dir[0] * c.type.speed, ny = c.y + c.dir[1] * c.type.speed;
    if (drivable(nx, ny)) { c.x = nx; c.y = ny; }
    else { c.dir = pick([[1, 0], [-1, 0], [0, 1], [0, -1]]); c.angle = Math.atan2(c.dir[1], c.dir[0]); }
    if (Math.random() < 0.01) { c.dir = pick([[1, 0], [-1, 0], [0, 1], [0, -1]]); c.angle = Math.atan2(c.dir[1], c.dir[0]); }
  });

  // police spawn/despawn with stars
  var wantPolice = S.stars;
  if (S.police.length < wantPolice && Math.random() < 0.05) spawnPolice();
  if (S.stars === 0 && S.police.length && Math.random() < 0.02) S.police.pop();
  S.police.forEach(function (po, i) {
    var dx = p.x - po.x, dy = p.y - po.y, dl = Math.hypot(dx, dy) || 1;
    var spd = 1.9;
    var nx = po.x + (dx / dl) * spd, ny = po.y + (dy / dl) * spd;
    if (walkable(nx, po.y)) po.x = nx;
    if (walkable(po.x, ny)) po.y = ny;
    po.angle = Math.atan2(dy, dx);
    if (dl < 24) {
      if (p.car) { p.car.hp -= 1; }
      else {
        po.contact++;
        if (po.contact > 70) { arrest(); }
      }
    } else po.contact = Math.max(0, po.contact - 1);
    if (dl > 700) S.police.splice(i, 1);
  });

  // heat-star cooldown when no recent crime & not near police
  if (now() - S.lastCrime > 8000 && S.stars > 0) {
    var nearCop = S.police.some(function (po) { return Math.hypot(po.x - p.x, po.y - p.y) < 180; });
    if (!nearCop) { S.stars = Math.max(0, S.stars - 1); S.lastCrime = now(); }
  }

  // sync health & knockout
  T.state.resources.health = clamp(p.hp, 0, T.state.resources.healthMax);
  if (p.hp <= 0) { knockout(); }

  // mission progress
  if (S.mission) updateMission();

  // camera
  S.cam.x = clamp(p.x - S.canvas.width / 2, 0, MAP_W * TILE - S.canvas.width);
  S.cam.y = clamp(p.y - S.canvas.height / 2, 0, MAP_H * TILE - S.canvas.height);
}

function updateMission() {
  var m = S.mission, p = S.player;
  if (m.kind === "delivery") {
    m.timer += 1 / 60;
    if (m.timer > m.timeLimit) { finishMission(false); return; }
    if (m.stage === "pickup" && Math.hypot(m.pickup.x - p.x, m.pickup.y - p.y) < 26) { m.stage = "dropoff"; setMsg("Deliver it (yellow marker) — hurry!"); }
    else if (m.stage === "dropoff" && Math.hypot(m.dropoff.x - p.x, m.dropoff.y - p.y) < 26) { finishMission(true); }
  } else if (m.kind === "collection") {
    m.stops.forEach(function (s) { if (!s.done && Math.hypot(s.x - p.x, s.y - p.y) < 26) { s.done = true; T.toast("Collected", "good"); } });
    if (m.stops.every(function (s) { return s.done; })) finishMission(true);
  } else if (m.kind === "turf") {
    if ((m.killed || 0) >= m.target) finishMission(true);
  } else if (m.kind === "cartheft") {
    // handled at chop POI
  }
}

function arrest() {
  S.police = []; S.stars = 0;
  var lost = Math.min(T.state.player.cash, randint(100, 400) * T.pack().priceScale);
  T.state.player.cash -= lost;
  T.state.player.heat = clamp(T.state.player.heat - 20, 0, 100);
  if (S.mission) finishMission(false);
  var sh = S.pois.filter(function (x) { return x.kind === "safehouse"; })[0];
  S.player.x = sh.x; S.player.y = sh.y; S.player.car = null;
  S.player.hp = T.state.resources.health;
  T.save();
  T.ui.screen("Busted", "The Task Force caught you. You lost " + T.money(lost) + " and any carried goods. You wake up back at the safehouse.", "Continue", function () {});
}
function knockout() {
  S.police = []; S.stars = 0;
  var fee = 80 * T.pack().priceScale;
  T.state.player.cash = Math.max(0, T.state.player.cash - fee);
  S.player.hp = T.state.resources.healthMax; T.state.resources.health = S.player.hp;
  if (S.mission) finishMission(false);
  var cl = S.pois.filter(function (x) { return x.kind === "clinic"; })[0];
  S.player.x = cl.x; S.player.y = cl.y; S.player.car = null;
  T.save();
  T.ui.screen("Knocked out", "You woke up at the clinic and paid " + T.money(fee) + " in fees.", "Continue", function () {});
}

/* ---------------------- render ------------------------------------------ */
var TILE_COLORS = { 0: "#3a3a42", 1: "#6b6256", 2: "#c9b79c" };
function render() {
  var ctx = S.ctx, W = S.canvas.width, H = S.canvas.height;
  var night = T.sim.isNight();
  ctx.fillStyle = "#24242a"; ctx.fillRect(0, 0, W, H);
  var x0 = Math.floor(S.cam.x / TILE), y0 = Math.floor(S.cam.y / TILE);
  var x1 = Math.min(MAP_W, x0 + Math.ceil(W / TILE) + 1);
  var y1 = Math.min(MAP_H, y0 + Math.ceil(H / TILE) + 1);
  for (var y = y0; y < y1; y++) for (var x = x0; x < x1; x++) {
    var t = S.grid[y][x];
    ctx.fillStyle = t === BUILDING ? districtTint(x, y) : TILE_COLORS[t];
    ctx.fillRect(x * TILE - S.cam.x, y * TILE - S.cam.y, TILE, TILE);
    if (t === ROAD) { // lane marks on intersections-ish
      ctx.fillStyle = "rgba(255,255,255,.06)"; ctx.fillRect(x * TILE - S.cam.x + TILE / 2 - 1, y * TILE - S.cam.y, 2, TILE);
    }
  }

  // billboards
  S.billboards.forEach(function (bb) {
    if (bb.x + bb.w < S.cam.x || bb.x > S.cam.x + W) return;
    if (!bb.ad) bb.ad = T.ads.pick("billboard", bb.tier, bb.id);
    var sx = bb.x - S.cam.x, sy = bb.y - S.cam.y;
    ctx.fillStyle = bb.ad.bg || "#111"; ctx.fillRect(sx, sy, bb.w, bb.h);
    ctx.fillStyle = bb.ad.fg || "#fff"; ctx.font = "bold 9px system-ui"; ctx.textBaseline = "top";
    ctx.fillText((bb.ad.brand || "AD").slice(0, 12), sx + 3, sy + 3);
    ctx.font = "7px system-ui"; ctx.fillText((bb.ad.text || "").slice(0, 16), sx + 3, sy + 15);
    ctx.strokeStyle = "#000"; ctx.strokeRect(sx, sy, bb.w, bb.h);
    // count an impression if on-screen
    T.ads.track(bb.ad.id, bb.id, "impression");
  });

  // POIs
  S.pois.forEach(function (poi) {
    var sx = poi.x - S.cam.x, sy = poi.y - S.cam.y;
    ctx.fillStyle = poi.color; ctx.beginPath(); ctx.arc(sx, sy, 10, 0, 6.28); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.font = "8px system-ui"; ctx.textAlign = "center";
    ctx.fillText(poi.label, sx, sy - 14); ctx.textAlign = "left";
  });
  // flyer walls
  S.flyerWalls.forEach(function (fw) { if (fw.used) return; var sx = fw.x - S.cam.x, sy = fw.y - S.cam.y; ctx.fillStyle = "#f1c40f"; ctx.fillRect(sx - 5, sy - 7, 10, 14); ctx.fillStyle = "#000"; ctx.font = "8px system-ui"; ctx.fillText("✎", sx - 3, sy + 3); });

  // mission markers
  if (S.mission) drawMissionMarkers(ctx);

  // cars
  S.cars.forEach(function (c) { if (c === S.player.car) return; drawCar(ctx, c); });

  // peds (incl. Pastor & converts)
  S.peds.forEach(function (ped) {
    var sx = ped.x - S.cam.x, sy = ped.y - S.cam.y;
    if (sx < -40 || sy < -40 || sx > W + 40 || sy > H + 40) return;
    var r = ped.preacher ? 7 : 6;
    ctx.fillStyle = ped.color; ctx.beginPath(); ctx.arc(sx, sy, r, 0, 6.28); ctx.fill();
    if (ped.hostile) { ctx.strokeStyle = "#000"; ctx.stroke(); }
    if (ped.preacher) { // white cross above
      ctx.strokeStyle = "#6a4fb0"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(sx, sy - 16); ctx.lineTo(sx, sy - 9); ctx.moveTo(sx - 3, sy - 14); ctx.lineTo(sx + 3, sy - 14); ctx.stroke(); ctx.lineWidth = 1;
    }
    if (ped.convert) { ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(sx, sy - 11, 4, 0, 6.28); ctx.stroke(); ctx.lineWidth = 1; }
    if ((ped.preacher || ped.convert) && ped.bubble && now() < ped.bubbleUntil) drawBubble(ctx, sx, sy - 22, ped.bubble);
  });
  // gunfire tracers
  S.tracers = S.tracers.filter(function (t) { return t.until > now(); });
  S.tracers.forEach(function (t) {
    ctx.strokeStyle = "rgba(255,230,120,.9)"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(t.x1 - S.cam.x, t.y1 - S.cam.y); ctx.lineTo(t.x2 - S.cam.x, t.y2 - S.cam.y); ctx.stroke(); ctx.lineWidth = 1;
  });
  // police
  S.police.forEach(function (po) { var sx = po.x - S.cam.x, sy = po.y - S.cam.y; ctx.fillStyle = po.color; ctx.beginPath(); ctx.arc(sx, sy, 7, 0, 6.28); ctx.fill(); ctx.fillStyle = "#e74c3c"; ctx.fillRect(sx - 4, sy - 10, 3, 3); ctx.fillStyle = "#3498db"; ctx.fillRect(sx + 1, sy - 10, 3, 3); });

  // player
  var p = S.player, psx = p.x - S.cam.x, psy = p.y - S.cam.y;
  if (p.car) drawCar(ctx, p.car, true);
  else {
    ctx.save(); ctx.translate(psx, psy); ctx.rotate(p.angle);
    ctx.fillStyle = "#f5d76e"; ctx.beginPath(); ctx.arc(0, 0, 7, 0, 6.28); ctx.fill();
    ctx.fillStyle = "#111"; ctx.fillRect(4, -2, 5, 4); // facing nub
    ctx.restore();
  }

  // night overlay
  if (night) { ctx.fillStyle = "rgba(10,10,40,.38)"; ctx.fillRect(0, 0, W, H); }

  renderMini();
  renderHud();
}
function districtTint(x, y) {
  var id = S.districtOf[y][x];
  var d = T.pack().districts.filter(function (dd) { return dd.id === id; })[0];
  // dark building colour tinted toward district colour
  return shade(d ? d.color : "#444", -0.55);
}
function shade(hex, amt) {
  var c = hex.replace("#", ""); var r = parseInt(c.substr(0, 2), 16), g = parseInt(c.substr(2, 2), 16), b = parseInt(c.substr(4, 2), 16);
  r = clamp(Math.round(r + r * amt), 0, 255); g = clamp(Math.round(g + g * amt), 0, 255); b = clamp(Math.round(b + b * amt), 0, 255);
  return "rgb(" + r + "," + g + "," + b + ")";
}
function drawCar(ctx, c, isPlayer) {
  var sx = c.x - S.cam.x, sy = c.y - S.cam.y;
  ctx.save(); ctx.translate(sx, sy); ctx.rotate(c.angle);
  ctx.fillStyle = c.color; ctx.fillRect(-12, -7, 24, 14);
  ctx.fillStyle = "rgba(255,255,255,.35)"; ctx.fillRect(2, -5, 6, 10);
  if (isPlayer) { ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.5; ctx.strokeRect(-12, -7, 24, 14); }
  ctx.restore();
}
function drawBubble(ctx, cx, cy, text) {
  text = text.length > 30 ? text.slice(0, 29) + "…" : text;
  ctx.font = "9px system-ui"; ctx.textAlign = "center";
  var w = ctx.measureText(text).width + 12;
  ctx.fillStyle = "rgba(255,255,255,.92)";
  roundRect(ctx, cx - w / 2, cy - 14, w, 16, 5); ctx.fill();
  ctx.fillStyle = "#1a1a22"; ctx.fillText(text, cx, cy - 3);
  ctx.textAlign = "left";
}
function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function drawMissionMarkers(ctx) {
  var m = S.mission;
  var mark = function (pt, col) { var sx = pt.x - S.cam.x, sy = pt.y - S.cam.y; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(sx, sy, 11, 0, 6.28); ctx.fill(); ctx.strokeStyle = "#000"; ctx.stroke(); };
  if (m.kind === "delivery") mark(m.stage === "pickup" ? m.pickup : m.dropoff, "#f1c40f");
  else if (m.kind === "collection") m.stops.forEach(function (s) { if (!s.done) mark(s, "#f1c40f"); });
  else if (m.kind === "cartheft" && m.hasCar && m.chop) mark(m.chop, "#e67e22");
}

/* mini-map */
function renderMini() {
  if (!S.mctx) return;
  var mc = S.mini, mctx = S.mctx, sx = mc.width / MAP_W, sy = mc.height / MAP_H;
  mctx.fillStyle = "#111"; mctx.fillRect(0, 0, mc.width, mc.height);
  for (var y = 0; y < MAP_H; y += 1) for (var x = 0; x < MAP_W; x += 1) {
    if (S.grid[y][x] === ROAD) { mctx.fillStyle = "#555"; mctx.fillRect(x * sx, y * sy, sx, sy); }
  }
  S.pois.forEach(function (p) { mctx.fillStyle = p.color; mctx.fillRect((p.x / TILE) * sx - 1, (p.y / TILE) * sy - 1, 2, 2); });
  S.police.forEach(function (p) { mctx.fillStyle = "#3498db"; mctx.fillRect((p.x / TILE) * sx - 1, (p.y / TILE) * sy - 1, 2, 2); });
  mctx.fillStyle = "#f5d76e"; mctx.fillRect((S.player.x / TILE) * sx - 1.5, (S.player.y / TILE) * sy - 1.5, 3, 3);
}

/* street HUD (DOM) */
function renderHud() {
  var set = function (id, v) { var e = document.getElementById(id); if (e && e.innerHTML !== v) e.innerHTML = v; };
  set("sh-cash", T.money(T.state.player.cash));
  var hpPct = clamp(S.player.hp / T.state.resources.healthMax * 100, 0, 100);
  var hpEl = document.getElementById("sh-hpbar"); if (hpEl) hpEl.style.width = hpPct + "%";
  var stars = ""; for (var i = 0; i < 5; i++) stars += i < S.stars ? "★" : "☆";
  set("sh-stars", stars);
  set("sh-clock", T.sim.clockStr() + (T.sim.isNight() ? " 🌙" : " ☀️"));
  var w = T.weaponById(T.state.equipped);
  set("sh-weapon", (w.type === "gun" ? "🔫 " : "🥊 ") + w.name + (w.type === "gun" ? " " + (T.state.ammo[w.id] || 0) : ""));
  var shopBtn = document.getElementById("btn-shop");
  if (shopBtn) shopBtn.style.display = S.nearGunShop ? "" : "none";
  var shopHint = document.getElementById("sh-shophint");
  if (shopHint) shopHint.style.display = S.nearGunShop ? "" : "none";
  var banner = document.getElementById("sh-mission");
  if (banner) {
    if (S.mission && now() < S.msgUntil) { banner.style.display = ""; banner.textContent = S.msg + missionExtra(); }
    else if (S.mission) { banner.style.display = ""; banner.textContent = missionLabel() + missionExtra(); }
    else if (now() < S.msgUntil) { banner.style.display = ""; banner.textContent = S.msg; }
    else banner.style.display = "none";
  }
}
function missionLabel() { return S.mission ? (T.MISSIONS["m_" + S.mission.kind] ? "" : "") + capitalize(S.mission.kind) + " mission" : ""; }
function missionExtra() {
  var m = S.mission; if (!m) return "";
  if (m.kind === "turf") return "  (" + (m.killed || 0) + "/" + m.target + ")";
  if (m.kind === "collection") return "  (" + m.stops.filter(function (s) { return s.done; }).length + "/3)";
  if (m.kind === "delivery") return "  (" + Math.max(0, Math.ceil(m.timeLimit - m.timer)) + "s)";
  return "";
}
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

/* ---------------------- lifecycle --------------------------------------- */
function resize() {
  if (!S.canvas) return;
  var wrap = S.canvas.parentElement;
  S.canvas.width = wrap.clientWidth;
  S.canvas.height = wrap.clientHeight;
}
T.street.onShow = function () {
  if (!S.canvas) {
    S.canvas = document.getElementById("game-canvas");
    S.ctx = S.canvas.getContext("2d");
    S.mini = document.getElementById("minimap");
    if (S.mini) S.mctx = S.mini.getContext("2d");
    window.addEventListener("resize", resize);
    bindInput();
  }
  resize();
  if (!S.built) buildWorld();
  else { S.player.hp = T.state.resources.health; }
};
T.street.frame = function (ts) {
  if (T.game.mode !== "street" || !S.built) return;
  update(1);
  render();
};
window.TURF = T;
})();
