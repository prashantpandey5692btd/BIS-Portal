/* ============================================================
   BIS PORTAL — SHARED JAVASCRIPT  v4
   Bulletproof theme system
   ============================================================ */
(function () {
  'use strict';

  var THEME_KEY = 'bis_theme';

  function applyTheme(theme) {
    var isLight = (theme === 'light');
    document.documentElement.setAttribute('data-theme', isLight ? 'light' : 'dark');
    if (document.body) {
      if (isLight) {
        document.body.classList.add('theme-light');
      } else {
        document.body.classList.remove('theme-light');
      }
    }
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      btn.textContent = isLight ? '🌙' : '☀️';
      btn.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
    });
  }

  function getSaved() {
    try { return localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'; }
    catch(e) { return 'dark'; }
  }

  function toggleTheme() {
    var next = document.body.classList.contains('theme-light') ? 'dark' : 'light';
    try { localStorage.setItem(THEME_KEY, next); } catch(e) {}
    applyTheme(next);
  }

  function wireButtons() {
    document.querySelectorAll('.theme-toggle').forEach(function (btn) {
      var clone = btn.cloneNode(true);
      btn.parentNode.replaceChild(clone, btn);
      clone.addEventListener('click', toggleTheme);
    });
  }

  /* Apply to <html> immediately */
  var saved = getSaved();
  document.documentElement.setAttribute('data-theme', saved);

  /* Apply fully once DOM ready */
  function ready() {
    applyTheme(saved);
    wireButtons();

    /* Mobile nav */
    var ham = document.getElementById('navHamburger');
    var nav = document.getElementById('mobileNav');
    if (ham && nav) {
      ham.addEventListener('click', function () {
        var open = nav.classList.toggle('open');
        ham.classList.toggle('open', open);
        ham.setAttribute('aria-expanded', String(open));
      });
      nav.querySelectorAll('.mobile-nav-link').forEach(function (l) {
        l.addEventListener('click', function () {
          nav.classList.remove('open');
          ham.classList.remove('open');
          ham.setAttribute('aria-expanded', 'false');
        });
      });
      document.addEventListener('click', function (e) {
        if (!ham.contains(e.target) && !nav.contains(e.target)) {
          nav.classList.remove('open');
          ham.classList.remove('open');
          ham.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }

}());
