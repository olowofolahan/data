/* ==========================================================================
 * Turf — online layer (async multiplayer)
 * --------------------------------------------------------------------------
 * Two backends behind one API:
 *   - "supabase"  OPEN multiplayer — any player on the shared link posts &
 *                 raids, using your Supabase project (config.js / Settings).
 *                 Everyone writes with the public anon key (guarded by RLS).
 *   - "db"        the artifact's built-in shared database — owner + invited
 *                 contributors can write; public-link outsiders are read-only.
 *   - null        offline (local file, or neither backend available).
 * publishProfile / loadLeaderboard / raid / processIncoming work the same way
 * for the game regardless of which backend is live.
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
var now = function () { return Date.now(); };
var randi = function (a, b) { return Math.floor(a + Math.random() * (b - a + 1)); };

var SB_ESM = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm";

T.online = { ready: false, mode: null, error: "", db: null, user: null, sb: null, uid: null, canWrite: null, _init: null };

/* Supabase creds: a per-device override (owner testing) wins, else config.js. */
T.online.supabaseConfig = function () {
  try { var o = JSON.parse(localStorage.getItem("turf.supabase") || "null"); if (o && o.url && o.key) return o; } catch (e) {}
  var c = window.TURF_CONFIG || {};
  if (c.supabaseUrl && c.supabaseAnonKey) return { url: c.supabaseUrl, key: c.supabaseAnonKey };
  return null;
};
T.online.setSupabaseConfig = function (url, key) {
  try { localStorage.setItem("turf.supabase", JSON.stringify({ url: url, key: key })); } catch (e) {}
};
T.online.clearSupabaseConfig = function () { try { localStorage.removeItem("turf.supabase"); } catch (e) {} };

/* Stable anonymous player id (uuid) for open play. */
T.online.anonId = function () {
  var id = null;
  try { id = localStorage.getItem("turf.uuid"); } catch (e) {}
  if (!id) {
    id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) { var r = Math.random() * 16 | 0; return (c === "x" ? r : (r & 0x3 | 0x8)).toString(16); });
    try { localStorage.setItem("turf.uuid", id); } catch (e) {}
  }
  return id;
};

T.online.init = function () {
  if (T.online._init) return T.online._init;
  T.online._init = (async function () {
    // 1) Supabase (open multiplayer) if configured.
    var cfg = T.online.supabaseConfig();
    if (cfg) {
      try {
        var mod = await import(SB_ESM);
        T.online.sb = mod.createClient(cfg.url, cfg.key);
        T.online.uid = T.online.anonId();
        T.online.canWrite = true;
        T.online.mode = "supabase";
        T.online.ready = true;
        return;
      } catch (e) {
        T.online.error = "Supabase couldn't load here (the sandbox may block it — host the game on a static site). " + (e && e.message ? e.message : "");
        // fall through to the artifact db
      }
    }
    // 2) Artifact shared database.
    try {
      if (window.claude && window.claude.use) {
        var db = await window.claude.use("db");
        var user = await window.claude.use("user");
        T.online.db = db || null;
        T.online.user = user || null;
        if (user) {
          try { T.online.uid = await user.id(); } catch (e) {}
          try { T.online.canWrite = await user.can("data.write"); } catch (e) { T.online.canWrite = null; }
        }
        if (db && T.online.uid) { T.online.mode = "db"; }
      }
    } catch (e) {}
    T.online.ready = true;
  })();
  return T.online._init;
};

T.online.available = function () { return !!(T.online.mode && T.online.uid); };
T.online.writable = function () { return T.online.available() && T.online.canWrite !== false; };
T.online.backendLabel = function () {
  return T.online.mode === "supabase" ? "Supabase (open multiplayer)"
    : T.online.mode === "db" ? "artifact shared database"
    : "offline";
};

function profileBody() {
  var s = T.state;
  return {
    name: String(s.player.name || "Boss").slice(0, 24),
    level: s.player.level,
    rank: T.rankForLevel(s.player.level).name,
    respect: Math.round(s.player.respect),
    power: T.empire.playerPower(),
    defense: T.empire.playerDefense(),
    districts: Object.keys(s.districts).filter(function (id) { return s.districts[id].owner === "player"; }).length,
    city: T.pack().city,
    country: T.pack().country
  };
}

/* ---- publish profile ---------------------------------------------------- */
T.online.publishProfile = async function () {
  if (!T.online.writable()) return false;
  var b = profileBody();
  try {
    if (T.online.mode === "supabase") {
      b.id = T.online.uid; b.updated_at = new Date().toISOString();
      var r = await T.online.sb.from("players").upsert(b);
      return !r.error;
    }
    b.updatedAt = now();
    await T.online.db.doc("players/" + T.online.uid).set(b);
    return true;
  } catch (e) { return false; }
};

/* ---- leaderboard -------------------------------------------------------- */
T.online.loadLeaderboard = async function () {
  if (!T.online.available()) return [];
  try {
    if (T.online.mode === "supabase") {
      var r = await T.online.sb.from("players").select("*").order("respect", { ascending: false }).limit(50);
      return (r.data || []).map(function (v) { v._id = v.id; return v; });
    }
    var snap = await T.online.db.collection("players").orderBy("respect", "desc").limit(50).get();
    return snap.docs.map(function (d) { var v = d.data() || {}; v._id = d.id; return v; });
  } catch (e) { return []; }
};

/* ---- raid another player ------------------------------------------------ */
T.online.raid = async function (target) {
  if (!T.online.writable()) return { ok: false, reason: "no-write" };
  if (!target || !target._id || target._id === T.online.uid) return { ok: false, reason: "bad-target" };
  var s = T.state, myPower = T.empire.playerPower(), theirPower = target.power || 0;
  var win = (myPower > theirPower) || (Math.random() < 0.3);
  var loot = 0;
  if (win) { loot = Math.max(1, Math.round((target.level || 1) * 60 + theirPower)) * T.pack().priceScale; s.player.cash += loot; s.player.respect += 15; }
  else { s.player.respect = Math.max(0, s.player.respect - 8); s.resources.health = clamp(s.resources.health - T.empire.mitigate(randi(10, 25)), 0, s.resources.healthMax); }
  try {
    if (T.online.mode === "supabase") {
      await T.online.sb.from("raids").insert({ attacker: T.online.uid, attacker_name: String(s.player.name || "A rival").slice(0, 24), defender_id: target._id, win: win, loot: loot, ts: new Date().toISOString() });
    } else {
      await T.online.db.collection("raids").add({ attacker: T.online.uid, attackerName: String(s.player.name || "A rival").slice(0, 24), defenderId: target._id, win: win, loot: loot, ts: now() });
    }
  } catch (e) {}
  T.save(); T.online.publishProfile();
  return { ok: true, win: win, loot: loot, name: target.name };
};

/* ---- apply raids made on me, then clear them ---------------------------- */
T.online.processIncoming = async function () {
  if (!T.online.available()) return null;
  var s = T.state;
  function applyOne(r) {
    if (r.win) {
      var rl = Math.min(s.player.cash, 80 * T.pack().priceScale);
      s.player.cash -= rl; s.player.respect = Math.max(0, s.player.respect - 10);
      var owned = Object.keys(s.districts).filter(function (id) { return s.districts[id].owner === "player"; });
      if (owned.length) { var dd = s.districts[owned[Math.floor(Math.random() * owned.length)]]; dd.control = clamp(dd.control - 10, 0, 100); }
      return { lostCash: rl, lost: 1, name: String(r.attacker_name || r.attackerName || "A rival").slice(0, 24) };
    }
    s.player.respect += 3; return { repelled: 1 };
  }
  try {
    var rows = [], ids = [];
    if (T.online.mode === "supabase") {
      var r = await T.online.sb.from("raids").select("*").eq("defender_id", T.online.uid).limit(50);
      rows = r.data || []; ids = rows.map(function (x) { return x.id; });
    } else {
      var snap = await T.online.db.collection("raids").where("defenderId", "==", T.online.uid).limit(50).get();
      rows = snap.docs.map(function (d) { var v = d.data() || {}; v.id = d.id; return v; }); ids = rows.map(function (x) { return x.id; });
    }
    if (!rows.length) return null;
    var sum = { lost: 0, lostCash: 0, repelled: 0, names: [] };
    rows.forEach(function (r) { var o = applyOne(r); if (o.lost) { sum.lost += o.lost; sum.lostCash += o.lostCash; sum.names.push(o.name); } if (o.repelled) sum.repelled += o.repelled; });
    // clear processed raids
    if (T.online.mode === "supabase") { try { await T.online.sb.from("raids").delete().in("id", ids); } catch (e) {} }
    else { for (var i = 0; i < ids.length; i++) { try { await T.online.db.doc("raids/" + ids[i]).delete(); } catch (e) {} } }
    T.save();
    return sum;
  } catch (e) { return null; }
};

/* ---- on load: connect, publish, apply incoming raids -------------------- */
T.online.onLoad = function () {
  T.online.init().then(function () {
    if (!T.online.available()) return;
    T.online.publishProfile();
    T.online.processIncoming().then(function (sum) {
      if (!sum || (!sum.lost && !sum.repelled)) return;
      var msg = "";
      if (sum.lost) msg += "You were raided " + sum.lost + " time" + (sum.lost > 1 ? "s" : "") + " (" + sum.names.slice(0, 3).join(", ") + ") — lost " + T.money(sum.lostCash) + " plus Respect & turf. ";
      if (sum.repelled) msg += "You repelled " + sum.repelled + " raid" + (sum.repelled > 1 ? "s" : "") + " (+Respect).";
      T.ui.screen("Raids while you were away", msg, "Settle up", function () { if (T.game.mode === "empire") T.empire.render(); });
    });
  });
};

window.TURF = T;
})();
