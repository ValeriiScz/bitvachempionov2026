/* DOVOD · assets/share.js · v1.0 · 2026-10-29
   Кнопка «Поделиться» на всех страницах — особенно для тех, кто открыл сайт как приложение (PWA):
   там нет адресной строки, и скопировать ссылку иначе нельзя.
   Телефон/планшет: системное меню «Поделиться» (navigator.share). Иначе — меню: скопировать ссылку, Telegram, WhatsApp.
   Плавающая кнопка справа внизу (если на странице есть «Наверх» — встаёт над ней).
   Любой элемент с атрибутом data-share тоже открывает меню (например, кнопка в шапке статьи). */
(function () {
  if (window.__dvShare) return; window.__dvShare = 1;
  var css = document.createElement('style');
  css.textContent =
    '.dvsh-fab{position:fixed;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:9998;display:inline-flex;align-items:center;gap:6px;height:40px;padding:0 14px;border-radius:999px;border:1px solid rgba(34,211,238,.6);background:#0f1320;color:#22d3ee;font:700 13px/1 Inter,system-ui,sans-serif;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.45);text-transform:none;letter-spacing:normal;font-style:normal;transform:none;clip-path:none;min-width:0;width:auto;margin:0}' +
    '.dvsh-fab.up{bottom:calc(62px + env(safe-area-inset-bottom,0px))}' +
    '.dvsh-fab svg{width:16px;height:16px}' +
    '.dvsh-m{position:fixed;right:12px;z-index:9999;min-width:220px;background:#0f1320;border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:6px;box-shadow:0 10px 30px rgba(0,0,0,.55);font:500 14px/1.2 Inter,system-ui,sans-serif}' +
    '.dvsh-m a,.dvsh-m button{text-transform:none;letter-spacing:normal;font-style:normal;transform:none;clip-path:none;margin:0;display:flex;width:100%;align-items:center;gap:10px;padding:11px 12px;border:0;border-radius:10px;background:none;color:#e9ecf3;text-decoration:none;font:inherit;cursor:pointer;text-align:left}' +
    '.dvsh-m a:hover,.dvsh-m button:hover{background:rgba(255,255,255,.06)}' +
    '.dvsh-t{position:fixed;left:50%;bottom:calc(70px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:10000;background:#22d3ee;color:#05060a;padding:10px 16px;border-radius:999px;font:700 13.5px/1 Inter,system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.4)}' +
    '@media print{.dvsh-fab{display:none}}';
  document.head.appendChild(css);

  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M12 3v13"/><path d="M7 8l5-5 5 5"/></svg>';
  function info() {
    var t = (document.querySelector('meta[property="og:title"]') || {}).content || document.title.replace(/\s+—\s+DOVOD$/, '');
    return { title: t, url: location.href };
  }
  function toast(s) {
    var d = document.createElement('div'); d.className = 'dvsh-t'; d.textContent = s; document.body.appendChild(d);
    setTimeout(function () { d.remove(); }, 1800);
  }
  function copy(u) {
    var done = function () { toast('Ссылка скопирована'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(done, function () { legacy(u); done(); });
    else { legacy(u); done(); }
  }
  function legacy(u) { var i = document.createElement('textarea'); i.value = u; i.style.position = 'fixed'; i.style.opacity = '0'; document.body.appendChild(i); i.select(); try { document.execCommand('copy'); } catch (e) {} i.remove(); }
  var menu = null;
  function close() { if (menu) { menu.remove(); menu = null; } }
  function open(anchor) {
    var I = info();
    if (navigator.share && /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent)) {
      navigator.share({ title: I.title, url: I.url }).catch(function () {}); return;
    }
    close();
    var e = encodeURIComponent;
    menu = document.createElement('div'); menu.className = 'dvsh-m';
    menu.innerHTML =
      '<button type="button" data-a="copy">🔗 Скопировать ссылку</button>' +
      '<a target="_blank" rel="noopener" href="https://t.me/share/url?url=' + e(I.url) + '&text=' + e(I.title) + '">✈️ Отправить в Telegram</a>' +
      '<a target="_blank" rel="noopener" href="https://wa.me/?text=' + e(I.title + ' ' + I.url) + '">💬 Отправить в WhatsApp</a>' +
      (navigator.share ? '<button type="button" data-a="native">↗ Другие приложения</button>' : '');
    document.body.appendChild(menu);
    var r = anchor.getBoundingClientRect();
    if (r.top > window.innerHeight / 2) menu.style.bottom = (window.innerHeight - r.top + 8) + 'px';
    else menu.style.top = (r.bottom + 8) + 'px';
    if (anchor.className.indexOf('dvsh-fab') < 0) { menu.style.right = 'auto'; menu.style.left = Math.max(12, Math.min(r.left, window.innerWidth - 240)) + 'px'; }
    menu.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-a]');
      if (b && b.getAttribute('data-a') === 'copy') copy(I.url);
      if (b && b.getAttribute('data-a') === 'native') navigator.share({ title: I.title, url: I.url }).catch(function () {});
      close();
    });
    setTimeout(function () { document.addEventListener('click', function h(ev) { if (menu && !menu.contains(ev.target)) { close(); document.removeEventListener('click', h); } }); }, 0);
  }
  window.dvShare = open;
  function init() {
    if (document.body.hasAttribute('data-noshare')) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'dvsh-fab'; b.innerHTML = ICON + '<span>Поделиться</span>';
    b.setAttribute('aria-label', 'Поделиться ссылкой на страницу');
    if (document.querySelector('.upfab')) b.classList.add('up');
    b.onclick = function (ev) { ev.stopPropagation(); open(b); };
    document.body.appendChild(b);
    document.addEventListener('click', function (ev) { var t = ev.target.closest('[data-share]'); if (t) { ev.preventDefault(); ev.stopPropagation(); open(t); } });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
