/* ==========================================================================
 * Turf — overlays & screens
 * --------------------------------------------------------------------------
 * Modal/overlay UI shared by both modes: country select, new game, the
 * "while you were away" summary, the full-screen flyer ad (rewarded, closable
 * after 2s), the weekly upkeep summary, random-event cards and the
 * arrested / knocked-out screens.
 * ========================================================================== */
(function () {
"use strict";
var T = window.TURF;
var $ = function (s) { return document.querySelector(s); };
var el = function (tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
T.ui = {};
/* True while any modal overlay is on screen (used to avoid stacking visits). */
T.ui._anyOverlay = function () { return !!document.querySelector("#overlays .overlay-back"); };

function overlay(node, dismissable) {
  var host = $("#overlays");
  var back = el("div", "overlay-back");
  var box = el("div", "overlay-box");
  box.appendChild(node);
  back.appendChild(box);
  host.appendChild(back);
  requestAnimationFrame(function () { back.classList.add("overlay-back--in"); });
  back.close = function () { back.classList.remove("overlay-back--in"); setTimeout(function () { if (back.parentNode) back.parentNode.removeChild(back); }, 250); };
  if (dismissable) back.addEventListener("click", function (e) { if (e.target === back) back.close(); });
  return back;
}

/* ---- Country select ---------------------------------------------------- */
T.ui.countrySelect = function (onPick) {
  var guess = guessCountry();
  var node = el("div");
  node.appendChild(el("h2", null, "Choose your city"));
  node.appendChild(el("p", "muted", "The engine is the same everywhere — each country is just a data pack. Guessed from your browser: <strong>" + T.COUNTRY_PACKS[guess].country + "</strong>."));
  var grid = el("div", "cards");
  Object.keys(T.COUNTRY_PACKS).forEach(function (key) {
    var pk = T.COUNTRY_PACKS[key];
    var card = el("div", "card" + (key === guess ? " card--hi" : ""));
    card.innerHTML = "<h4>" + pk.city + "</h4><div class='muted small'>" + pk.country + " · " + pk.currency.name +
      " (" + pk.currency.symbol + ") · " + pk.weather + "</div>" +
      "<div class='muted small'>" + pk.districts.length + " districts · rivals: " + pk.rivals.map(function (r) { return r.name; }).join(", ") + "</div>";
    var b = el("button", "btn", "Play " + pk.country);
    b.onclick = function () { back.close(); onPick(key); };
    card.appendChild(b);
    grid.appendChild(card);
  });
  node.appendChild(grid);
  var back = overlay(node, false);
};
function guessCountry() {
  try {
    var lang = (navigator.language || "en").toLowerCase();
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    if (/lagos|africa\/lagos/i.test(tz) || lang.indexOf("ng") >= 0) return "lagos";
    if (/toronto|winnipeg|regina|edmonton|canada/i.test(tz) || lang.indexOf("ca") >= 0) return "prairie";
  } catch (e) {}
  return "lagos";
}

/* ---- New game ---------------------------------------------------------- */
T.ui.newGame = function (country, onStart) {
  var pk = T.COUNTRY_PACKS[country];
  var node = el("div");
  node.appendChild(el("h2", null, "New game — " + pk.city));
  var nameWrap = el("div", "field");
  nameWrap.appendChild(el("label", null, "Your name"));
  var input = el("input", "input"); input.value = "Ola"; input.maxLength = 16;
  nameWrap.appendChild(input);
  node.appendChild(nameWrap);
  node.appendChild(el("label", null, "Look"));
  var looks = el("div", "chips");
  var chosen = { look: pk.characterLooks[0] };
  pk.characterLooks.forEach(function (l, i) {
    var c = el("button", "chip" + (i === 0 ? " chip--on" : ""), l);
    c.onclick = function () { chosen.look = l; looks.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("chip--on"); }); c.classList.add("chip--on"); };
    looks.appendChild(c);
  });
  node.appendChild(looks);
  var start = el("button", "btn btn--big", "Start");
  start.onclick = function () { back.close(); onStart((input.value || "Newcomer").slice(0, 16), chosen.look); };
  node.appendChild(start);
  var back = overlay(node, false);
};

/* ---- Tutorial ---------------------------------------------------------- */
T.ui.tutorial = function () {
  var node = el("div");
  node.appendChild(el("h2", null, "Welcome to Turf"));
  node.appendChild(el("p", null, "You start broke. Climb from small-time hustler to Kingpin."));
  var steps = el("ul", "tut");
  ["Spend <strong>energy</strong> on jobs for cash + XP. Energy refills over real time (40 per hour).",
   "Hire <strong>crew</strong>, buy <strong>properties</strong> for passive income, and take <strong>districts</strong> to 100% control.",
   "Build an <strong>arsenal</strong> (it boosts your strength in fights) and attack rival gangs in the <strong>Fight</strong> tab.",
   "Watch your <strong>Heat</strong> and pay the <strong>weekly upkeep</strong>, or crew start to leave. Add <strong>friends</strong> and invite them by email."
  ].forEach(function (s) { steps.appendChild(el("li", null, s)); });
  node.appendChild(steps);
  var go = el("button", "btn btn--big", "Let's go");
  go.onclick = function () { back.close(); };
  node.appendChild(go);
  var back = overlay(node, false);
};

/* ---- While you were away ---------------------------------------------- */
T.ui.welcomeBack = function (info) {
  if (info.ms < 60 * 1000) return; // don't bother for quick returns
  var node = el("div");
  node.appendChild(el("h2", null, "While you were away"));
  var mins = Math.round(info.ms / 60000);
  node.appendChild(el("p", "muted", "You were gone about " + (mins >= 60 ? Math.round(mins / 60) + "h" : mins + "m") + "."));
  var ul = el("ul", "tut");
  if (info.propIncome > 0) ul.appendChild(el("li", null, "Property income collected: <strong>" + T.money(info.propIncome) + "</strong>"));
  if (info.districtIncome > 0) ul.appendChild(el("li", null, "District income: <strong>" + T.money(info.districtIncome) + "</strong>"));
  if (info.heatCooled > 0) ul.appendChild(el("li", null, "Heat cooled by <strong>" + Math.round(info.heatCooled) + "</strong>"));
  ul.appendChild(el("li", null, "Energy & stamina refilled."));
  node.appendChild(ul);
  var b = el("button", "btn btn--big", "Back to business");
  b.onclick = function () { back.close(); };
  node.appendChild(b);
  var back = overlay(node, false);
};

/* ---- Flyer (rewarded full-screen ad) ---------------------------------- */
T.ui.flyer = function (ad, replay) {
  T.ads.track(ad.id, "flyer", "view");
  var node = el("div", "flyer");
  node.style.background = ad.bg || "#111"; node.style.color = ad.fg || "#fff";
  node.innerHTML = "<div class='flyer-brand'>" + (ad.brand || "Flyer") + "</div>" +
    "<div class='flyer-tag'>" + (ad.text || "") + "</div>" +
    (ad.parody ? "<div class='ad-tag'>parody ad</div>" : "");
  var reward = "";
  if (!replay) {
    var day = T.sim.gameDay();
    if (T.state.lastFlyerDay !== day) { T.state.lastFlyerDay = day; T.state.flyersToday = 0; }
    if (T.state.flyersToday < 3) {
      T.state.flyersToday++;
      var kind = Math.random();
      if (kind < 0.5) { var c = 50 * T.pack().priceScale; T.state.player.cash += c; reward = "+" + T.money(c); }
      else { T.state.resources.energy = Math.min(T.state.resources.energyMax, T.state.resources.energy + 3); reward = "+3 energy"; }
      // keep the flyer in inventory
      T.state.inventory.flyers.push(JSON.stringify({ brand: ad.brand, text: ad.text, bg: ad.bg, fg: ad.fg, url: ad.url || null }));
      T.save();
    } else reward = "(daily reward cap reached)";
  }
  if (reward) node.appendChild(el("div", "flyer-reward", "Reward: " + reward));
  var btns = el("div", "flyer-btns");
  var close = el("button", "btn", "Close");
  close.disabled = !replay; // closable after 2 seconds
  if (ad.url) { var visit = el("button", "btn btn--ghost", "Visit"); visit.onclick = function () { T.ads.track(ad.id, "flyer", "click"); window.open(ad.url, "_blank"); }; btns.appendChild(visit); }
  btns.appendChild(close);
  node.appendChild(btns);
  close.onclick = function () { back.close(); };
  var back = overlay(node, false);
  if (!replay) { setTimeout(function () { close.disabled = false; close.textContent = "Close"; }, 2000); if (!replay) close.textContent = "Close (2s)"; }
};

/* ---- Random event card ------------------------------------------------- */
T.ui.event = function (ev) {
  var node = el("div");
  node.appendChild(el("h2", null, ev.title));
  node.appendChild(el("p", null, ev.text));
  var b = el("button", "btn btn--big", "OK");
  b.onclick = function () { back.close(); if (T.game.mode === "empire") T.empire.render(); };
  node.appendChild(b);
  var back = overlay(node, true);
};

/* ---- Weekly upkeep ----------------------------------------------------- */
T.ui.upkeep = function () {
  if (T.ui._upkeepOpen) return; T.ui._upkeepOpen = true;
  var res = T.sim.payUpkeep();
  var node = el("div");
  node.appendChild(el("h2", null, "Weekly upkeep"));
  var ul = el("ul", "tut");
  ul.appendChild(el("li", null, "Crew wages: <strong>" + T.money(res.bill.wages) + "</strong>"));
  ul.appendChild(el("li", null, "Property maintenance: <strong>" + T.money(res.bill.maint) + "</strong>"));
  ul.appendChild(el("li", null, "Bribes (Heat): <strong>" + T.money(res.bill.bribes) + "</strong>"));
  ul.appendChild(el("li", null, "Total: <strong>" + T.money(res.bill.total) + "</strong>"));
  node.appendChild(ul);
  if (res.paid) node.appendChild(el("p", "ok", "Paid in full."));
  else {
    node.appendChild(el("p", "bad", "You couldn't cover it. Crew loyalty dropped." + (res.lost.length ? " Left: " + res.lost.join(", ") + "." : "")));
  }
  var b = el("button", "btn btn--big", "Continue");
  b.onclick = function () { back.close(); T.ui._upkeepOpen = false; if (T.game.mode === "empire") T.empire.render(); };
  node.appendChild(b);
  var back = overlay(node, false);
};

/* ---- Gun shop (street) -------------------------------------------------- */
T.ui.gunShop = function () {
  if (T.ui._shopOpen) return; T.ui._shopOpen = true;
  var node = el("div");
  node.appendChild(el("h2", null, "Gun shop"));
  node.appendChild(el("p", "muted", "Buy weapons and ammo. Guns unlock by rank. Keep it quiet — firing in public brings Heat."));
  var host = el("div");
  var rerender = function () { host.innerHTML = ""; T.weaponCards(host, rerender); };
  rerender();
  node.appendChild(host);
  var b = el("button", "btn btn--big", "Leave");
  b.onclick = function () { back.close(); T.ui._shopOpen = false; };
  node.appendChild(b);
  var back = overlay(node, false);
};

/* ---- Born-again convert ------------------------------------------------- */
T.ui.bornAgain = function (name, scripture, onClose) {
  if (T.ui._convertOpen) { if (onClose) onClose(); return; }
  T.ui._convertOpen = true;
  var node = el("div", "convert");
  node.appendChild(el("h2", null, "🙏 A convert approaches"));
  node.appendChild(el("p", null, "<strong>" + name + "</strong> steps up, cap in hand:"));
  node.appendChild(el("p", "convert-opener", "“" + pick(T.CONVERT_OPENERS) + "”"));
  node.appendChild(el("blockquote", "scripture",
    "“" + scripture.text + "”<footer>— " + scripture.ref + " (KJV)</footer>"));
  var row = el("div", "row");
  var bless = el("button", "btn", "🙏 Bless them & let them go");
  bless.onclick = function () {
    T.state.player.heat = Math.max(0, T.state.player.heat - 10);
    T.state.player.respect += 2; T.state.converts = (T.state.converts || 0) + 1;
    T.toast(name + " leaves in peace. Heat eases.", "good");
    T.save(); close();
  };
  var wave = el("button", "btn btn--ghost", "Wave them off");
  wave.onclick = function () { T.toast(name + " walks on, praying for you.", "warn"); close(); };
  row.appendChild(bless); row.appendChild(wave);
  node.appendChild(row);
  function close() { back.close(); T.ui._convertOpen = false; if (onClose) onClose(); if (T.game.mode === "empire") T.empire.render(); }
  var back = overlay(node, false);
};
function pick(a) { return a[Math.floor(Math.random() * a.length)]; }

/* ---- Generic choice overlay (title + html + buttons) ------------------- */
T.ui.choice = function (title, html, options) {
  var node = el("div");
  node.appendChild(el("h2", null, title));
  if (html) { var d = el("div"); d.innerHTML = html; node.appendChild(d); }
  options.forEach(function (opt) {
    var cls = "btn btn--big" + (opt.kind === "ghost" ? " btn--ghost" : opt.kind === "danger" ? " btn--danger" : "");
    var b = el("button", cls, opt.label);
    b.disabled = !!opt.disabled;
    if (opt.disabled && opt.disabledTitle) b.title = opt.disabledTitle;
    b.onclick = function () { back.close(); if (opt.onClick) opt.onClick(); };
    node.appendChild(b);
  });
  var cancel = el("button", "btn btn--ghost btn--big", "Cancel");
  cancel.onclick = function () { back.close(); };
  node.appendChild(cancel);
  var back = overlay(node, true);
  return back;
};

/* ---- Clinic (knocked out in an Empire fight) --------------------------- */
T.ui.clinic = function () {
  var fee = 80 * T.pack().priceScale;
  T.state.player.cash = Math.max(0, T.state.player.cash - fee);
  T.state.resources.health = T.state.resources.healthMax;
  T.save();
  T.ui.screen("Knocked out", "You took a beating and woke up at the clinic. Patched up for " + T.money(fee) + ".", "Continue", function () { if (T.game.mode === "empire") T.empire.render(); });
};

/* ---- Generic screen (arrested / knocked out) -------------------------- */
T.ui.screen = function (title, text, btn, cb) {
  var node = el("div");
  node.appendChild(el("h2", null, title));
  node.appendChild(el("p", null, text));
  var b = el("button", "btn btn--big", btn || "OK");
  b.onclick = function () { back.close(); if (cb) cb(); };
  node.appendChild(b);
  var back = overlay(node, false);
};

window.TURF = T;
})();
