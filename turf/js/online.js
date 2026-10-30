/* ==========================================================================
 * Turf — online layer (async multiplayer via the artifact shared database)
 * --------------------------------------------------------------------------
 * Uses the published artifact's `db` + `user` runtime capabilities to connect
 * players asynchronously:
 *   - each player publishes a profile snapshot to the shared `players`
 *     collection (a global leaderboard),
 *   - players can "raid" another player's saved empire (resolved with the same
 *     Attack+Defence+Respect rating system), which drops a record into the
 *     shared `raids` collection; the defender applies the consequence the next
 *     time they load.
 * Everything degrades gracefully: on a local file or when the capability is
 * absent, online features simply stay off and the rest of the game is intact.
 * Writing (posting a score, raiding) needs the viewer to be the owner or a
 * Contributor/Editor on the shared artifact — public-link outsiders are
 * read-only, which the UI explains.
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
var now = function () { return Date.now(); };

T.online = { ready: false, db: null, user: null, uid: null, canWrite: null, _init: null };

T.online.init = function () {
  if (T.online._init) return T.online._init;
  T.online._init = (async function () {
    try {
      if (!window.claude || !window.claude.use) return;         // local file / chat artifact
      var db = await window.claude.use("db");
      var user = await window.claude.use("user");
      T.online.db = db || null;
      T.online.user = user || null;
      if (user) {
        try { T.online.uid = await user.id(); } catch (e) { T.online.uid = null; }
        try { T.online.canWrite = await user.can("data.write"); } catch (e) { T.online.canWrite = null; }
      }
      T.online.ready = true;
    } catch (e) { /* stay offline */ }
  })();
  return T.online._init;
};

T.online.available = function () { return !!(T.online.db && T.online.uid); };
T.online.writable = function () { return T.online.available() && T.online.canWrite !== false; };

/* Publish my current standing to the shared leaderboard. */
T.online.publishProfile = async function () {
  if (!T.online.writable()) return false;
  var s = T.state;
  var body = {
    name: String(s.player.name || "Boss").slice(0, 24),
    level: s.player.level,
    rank: T.rankForLevel(s.player.level).name,
    respect: Math.round(s.player.respect),
    power: T.empire.playerPower(),
    defense: T.empire.playerDefense(),
    districts: Object.keys(s.districts).filter(function (id) { return s.districts[id].owner === "player"; }).length,
    city: T.pack().city,
    country: T.pack().country,
    updatedAt: now()
  };
  try { await T.online.db.doc("players/" + T.online.uid).set(body); return true; }
  catch (e) { return false; }
};

/* Top players by respect. */
T.online.loadLeaderboard = async function () {
  if (!T.online.available()) return [];
  try {
    var snap = await T.online.db.collection("players").orderBy("respect", "desc").limit(50).get();
    return snap.docs.map(function (d) { var v = d.data() || {}; v._id = d.id; return v; });
  } catch (e) { return []; }
};

/* Raid another player's saved empire. Resolved with our rating vs theirs. */
T.online.raid = async function (target) {
  if (!T.online.writable()) return { ok: false, reason: "no-write" };
  if (!target || !target._id || target._id === T.online.uid) return { ok: false, reason: "bad-target" };
  var s = T.state, myPower = T.empire.playerPower(), theirPower = target.power || 0;
  var win = (myPower > theirPower) || (Math.random() < 0.3); // outrank = sure win; else underdog chance
  var loot = 0;
  if (win) {
    loot = Math.max(1, Math.round((target.level || 1) * 60 + (theirPower || 0))) * T.pack().priceScale;
    s.player.cash += loot; s.player.respect += 15;
  } else {
    s.player.respect = Math.max(0, s.player.respect - 8);
    s.resources.health = clamp(s.resources.health - T.empire.mitigate(randi(10, 25)), 0, s.resources.healthMax);
  }
  try {
    await T.online.db.collection("raids").add({
      attacker: T.online.uid,
      attackerName: String(s.player.name || "A rival").slice(0, 24),
      defenderId: target._id, win: win, loot: loot, ts: now()
    });
  } catch (e) { /* notify best-effort */ }
  T.save();
  T.online.publishProfile();
  return { ok: true, win: win, loot: loot, name: target.name };
};

/* Apply raids other players made on me since last time, then clear them. */
T.online.processIncoming = async function () {
  if (!T.online.available()) return null;
  var s = T.state;
  try {
    var snap = await T.online.db.collection("raids").where("defenderId", "==", T.online.uid).limit(50).get();
    if (snap.empty) return null;
    var lost = 0, lostCash = 0, repelled = 0, names = [], ids = [];
    snap.docs.forEach(function (d) {
      var r = d.data() || {};
      if (r.win) {
        var rl = Math.min(s.player.cash, 80 * T.pack().priceScale);
        s.player.cash -= rl; lostCash += rl;
        s.player.respect = Math.max(0, s.player.respect - 10); lost++;
        var owned = Object.keys(s.districts).filter(function (id) { return s.districts[id].owner === "player"; });
        if (owned.length) { var dd = s.districts[owned[Math.floor(Math.random() * owned.length)]]; dd.control = clamp(dd.control - 10, 0, 100); }
        names.push(String(r.attackerName || "A rival").slice(0, 24));
      } else { repelled++; s.player.respect += 3; }
      ids.push(d.id);
    });
    for (var i = 0; i < ids.length; i++) { try { await T.online.db.doc("raids/" + ids[i]).delete(); } catch (e) {} }
    T.save();
    return { lost: lost, lostCash: lostCash, repelled: repelled, names: names };
  } catch (e) { return null; }
};

function randi(a, b) { return Math.floor(a + Math.random() * (b - a + 1)); }

/* Run on load: connect, publish, and apply any raids that landed while away. */
T.online.onLoad = function () {
  T.online.init().then(function () {
    if (!T.online.available()) return;
    T.online.publishProfile();
    T.online.processIncoming().then(function (sum) {
      if (!sum || (!sum.lost && !sum.repelled)) return;
      var msg = "";
      if (sum.lost) msg += "You were raided " + sum.lost + " time" + (sum.lost > 1 ? "s" : "") +
        " (" + (sum.names.slice(0, 3).join(", ")) + ") — lost " + T.money(sum.lostCash) + " and some Respect & turf. ";
      if (sum.repelled) msg += "You repelled " + sum.repelled + " raid" + (sum.repelled > 1 ? "s" : "") + " (+Respect).";
      T.ui.screen("Raids while you were away", msg, "Settle up", function () { if (T.game.mode === "empire") T.empire.render(); });
    });
  });
};

window.TURF = T;
})();
