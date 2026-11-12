/* Twirler Pictures — site behaviour
   Age gate + small progressive enhancements. No dependencies. */

(function () {
  'use strict';

  var GATE_KEY = 'twirler.ageVerified.v1';

  /* ---------- age gate ---------- */
  function initGate() {
    var gate = document.getElementById('age-gate');
    if (!gate) return;

    var verified = false;
    try { verified = sessionStorage.getItem(GATE_KEY) === '1'; } catch (e) {}

    if (verified) {
      gate.hidden = true;
      document.documentElement.classList.remove('gated');
    } else {
      gate.hidden = false;
      document.documentElement.classList.add('gated');
      var enter = gate.querySelector('[data-gate-enter]');
      if (enter) enter.focus();
    }

    gate.addEventListener('click', function (ev) {
      var enter = ev.target.closest('[data-gate-enter]');
      var exit = ev.target.closest('[data-gate-exit]');
      if (enter) {
        try { sessionStorage.setItem(GATE_KEY, '1'); } catch (e) {}
        gate.hidden = true;
        document.documentElement.classList.remove('gated');
        var main = document.getElementById('main');
        if (main) main.focus();
      }
      if (exit) {
        window.location.replace('https://www.google.com/');
      }
    });
  }

  /* ---------- year ---------- */
  function initYear() {
    document.querySelectorAll('[data-year]').forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* ---------- nav current page ---------- */
  function initNav() {
    var path = location.pathname.replace(/\/+$/, '') || '/index.html';
    document.querySelectorAll('.nav-links a').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (href === path || (path === '/index.html' && href === 'index.html')) {
        a.setAttribute('aria-current', 'page');
      }
    });
  }

  /* ---------- enquiry form (mailto fallback until a backend exists) ---------- */
  function initForm() {
    var form = document.getElementById('enquiry-form');
    if (!form) return;
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var data = new FormData(form);
      var lines = [];
      data.forEach(function (v, k) { lines.push(k + ': ' + v); });
      var subject = encodeURIComponent('Twirler enquiry — ' + (data.get('type') || 'General'));
      var body = encodeURIComponent(lines.join('\n'));
      window.location.href = 'mailto:bookings@twirlerpictures.co.uk?subject=' + subject + '&body=' + body;
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initGate();
    initYear();
    initNav();
    initForm();
  });
})();
