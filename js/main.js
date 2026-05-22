/*
  Soul Languages — main.js
  Zero-dependency: theme toggle, lazy CC loading, episode loading, video lightbox
*/

(function () {
  "use strict";

  // ── 1. Theme toggle ───────────────────────────────────────────
  var tg = document.getElementById("theme-toggle");
  if (tg) {
    var saved = localStorage.getItem("sl-theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
    tg.textContent = saved === "dark" ? "☀️" : "🌙";
    tg.addEventListener("click", function () {
      var nxt = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nxt);
      localStorage.setItem("sl-theme", nxt);
      tg.textContent = nxt === "dark" ? "☀️" : "🌙";
    });
  }

  // ── 2. Language toggle (SL_CC loaded via <script defer>) ─────
  var lt = document.querySelector(".lang-toggle");

  if (lt) {
    lt.addEventListener("click", function () {
      var cur = localStorage.getItem("sl-lang") || "hant";
      var target = cur === "hant" ? "hans" : "hant";
      applyLang(target);
    });

    // Apply saved language on load (SL_CC loaded via <script defer>)
    var savedLang = localStorage.getItem("sl-lang") || "hant";
    if (savedLang === "hans") {
      applyLang("hans");
    }
  }

  function walkTextNodes(root, conv) {
    var iter = document.createNodeIterator(root, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = iter.nextNode())) {
      var p = n.parentNode;
      if (p && p.tagName && /^(SCRIPT|STYLE|IFRAME|NOSCRIPT)$/i.test(p.tagName)) continue;
      n.textContent = conv(n.textContent);
    }
  }

  function applyLang(lang) {
    if (typeof SL_CC === "undefined") {
      console.warn("CC converter not loaded yet");
      return;
    }
    if (lang === "hans") {
      walkTextNodes(document.body, SL_CC.toSimplified);
      document.documentElement.setAttribute("lang", "zh-Hans");
      lt.textContent = "繁";
      lt.setAttribute("aria-label", "切換繁體中文");
    } else {
      walkTextNodes(document.body, SL_CC.toTraditional);
      document.documentElement.setAttribute("lang", "zh-Hant");
      lt.textContent = "簡";
      lt.setAttribute("aria-label", "切換簡體中文");
    }
    localStorage.setItem("sl-lang", lang);
  }

  // ── 3. Mobile nav toggle ─────────────────────────────────────
  var mnt = document.querySelector(".mobile-nav-toggle");
  var navItems = document.querySelector(".nav-items");
  if (mnt && navItems) {
    mnt.addEventListener("click", function () {
      var open = navItems.classList.toggle("open");
      mnt.setAttribute("aria-expanded", open);
      mnt.textContent = open ? "✕" : "☰";
    });
    // Close nav when a link is clicked
    navItems.addEventListener("click", function () {
      navItems.classList.remove("open");
      mnt.setAttribute("aria-expanded", "false");
      mnt.textContent = "☰";
    });
  }

  // ── 4. Episode grid from JSON data ────────────────────────────
  var grid = document.getElementById("episodes-grid");
  if (grid) {
    fetch("/data/content.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        (d.episodes || []).forEach(function (ep) {
          var t = ep.title;
          var card = document.createElement("article");
          card.className = "ep-card";
          card.innerHTML =
            '<img class="ep-thumb" src="' + ep.thumb + '" alt="' + t.en + '"'
          + ' loading="lazy" data-video="' + ep.yt + '">'
          + '<div class="ep-body"><span class="ep-num">EP' + ep.num + '</span>'
          + '<p class="ep-title">' + t.en + '</p>'
          + '<p class="ep-sub">' + t.zh + '</p></div>';
          card.querySelector(".ep-thumb").addEventListener("click", openVideo);
          grid.appendChild(card);
        });
      })
      .catch(console.error);
  }

  // ── 5. Active nav highlight ──────────────────────────────────
  document.querySelectorAll(".nav-items a").forEach(function (a) {
    if (a.href === location.href) a.classList.add("active-nav");
  });

  // ── 6. Global keyboard dismiss ───────────────────────────────
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeVideo();
  });

  // ── 7. Event delegation for static episode cards ─────────────
  document.addEventListener("click", function (e) {
    var card = e.target.closest ? e.target.closest(".card") : null;
    if (card) {
      var thumb = card.querySelector(".card-img");
      if (thumb && thumb.getAttribute("data-video")) {
        openVideo({ currentTarget: thumb });
      }
    }
  });
})();

// ── Video lightbox ─────────────────────────────────────────────
function openVideo(e) {
  var lb = document.getElementById("lightbox");
  var li = document.getElementById("lightbox-inner");
  var id = e.currentTarget.getAttribute("data-video");
  li.innerHTML =
    '<iframe src="https://www.youtube.com/embed/' + id
    + '?autoplay=1&rel=0" title="YouTube video"'
    + ' allow="accelerometer;autoplay;clipboard-write;encrypted-media;'
    + 'gyroscope;picture-in-picture" allowfullscreen></iframe>';
  lb.hidden = false;
  requestAnimationFrame(function () { lb.classList.add("open"); });
  document.body.style.overflow = "hidden";
}

function closeVideo() {
  var lb = document.getElementById("lightbox"), li = document.getElementById("lightbox-inner");
  lb.classList.remove("open");
  li.innerHTML = "";
  document.body.style.overflow = "";
  setTimeout(function () { lb.hidden = true; }, 250);
}

(function registerClose() {
  var closeBtn = document.getElementById("lightbox-close");
  if (closeBtn) closeBtn.addEventListener("click", closeVideo);
  var lb = document.getElementById("lightbox");
  if (lb) lb.addEventListener("click", function (e) {
    if (e.target === lb || e.target.id === "lightbox-inner") closeVideo();
  });
})();
