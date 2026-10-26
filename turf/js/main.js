/* ==========================================================================
 * Turf — bootstrap & main loop
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var $ = function (s) { return document.querySelector(s); };

function wireChrome() {
  $("#to-empire").onclick = function () { T.game.setMode("empire"); };
  $("#to-street").onclick = function () {
    if (T.game.mode === "street" && T.street._S.mission) { T.toast("Finish or fail the mission first", "warn"); return; }
    T.game.setMode("street");
  };
  // "Free roam" entry from street: if no mission, just explore.
}

function startLoops() {
  // 1-second sim heartbeat (runs in any mode)
  setInterval(function () { if (T.state) T.game.heartbeat(); }, 1000);
  // render loop (street mode only draws)
  function frame(ts) { if (T.state) T.street.frame(ts); requestAnimationFrame(frame); }
  requestAnimationFrame(frame);
}

function enterGame(fresh) {
  if (fresh) {
    // brand new save
    var info = { ms: 0 };
  } else {
    var info = T.sim.catchUp();
  }
  T.game._lastTick = Date.now();
  wireChrome();
  T.game.setMode("empire");
  if (fresh) { T.ui.tutorial(); }
  else { T.ui.welcomeBack(info); }
  startLoops();
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
