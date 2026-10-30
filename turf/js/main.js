/* ==========================================================================
 * Turf — bootstrap & main loop
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var $ = function (s) { return document.querySelector(s); };

function startLoops() {
  // 1-second sim heartbeat
  setInterval(function () { if (T.state) T.game.heartbeat(); }, 1000);
}

function enterGame(fresh) {
  if (fresh) {
    // brand new save
    var info = { ms: 0 };
  } else {
    var info = T.sim.catchUp();
  }
  T.game._lastTick = Date.now();
  T.game.setMode("empire");
  if (fresh) { T.ui.tutorial(); }
  else { T.ui.welcomeBack(info); }
  startLoops();
  if (T.online && T.online.onLoad) { try { T.online.onLoad(); } catch (e) {} }
}

function boot() {
  var splash = $("#splash");
  if (T.hasSave() && T.load()) {
    if (splash) splash.style.display = "none";
    enterGame(false);
    return;
  }
  // new player flow
  if (splash) splash.style.display = "none";
  T.ui.countrySelect(function (country) {
    T.ui.newGame(country, function (name, look) {
      T.newGame(country, name, look);
      enterGame(true);
    });
  });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
})();
