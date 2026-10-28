/* DOVOD · assets/share.js · v1.1 · 2026-10-29 · без плавающей кнопки: ссылка «Поделиться» в крошках сверху (или кнопка в конце страницы) · v1.0 · 2026-10-29
   Кнопка «Поделиться» на всех страницах — особенно для тех, кто открыл сайт как приложение (PWA):
   там нет адресной строки, и скопировать ссылку иначе нельзя.
   Телефон/планшет: системное меню «Поделиться» (navigator.share). Иначе — меню: скопировать ссылку, Telegram, WhatsApp.
   Плавающая кнопка справа внизу (если на странице есть «Наверх» — встаёт над ней).
   Любой элемент с атрибутом data-share тоже открывает меню (например, кнопка в шапке статьи). */
(function () {
  if (window.__dvShare) return; window.__dvShare = 1;
  var css = document.createElement('style');
  css.textContent =
    '.dvsh-cr{margin-left:auto;display:inline-flex;align-items:center;gap:5px;padding:0;border:0;background:none;color:#22d3ee;font:inherit;letter-spacing:inherit;text-transform:inherit;cursor:pointer;white-space:nowrap}.dvsh-cr svg{width:12px;height:12px}' +
    '.dvsh-foot{display:flex;justify-content:center;padding:26px 16px calc(90px + env(safe-area-inset-bottom,0px))}' +
    '.dvsh-fb{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:999px;border:1px solid rgba(34,211,238,.5);background:none;color:#22d3ee;font:700 13px/1 Inter,system-ui,sans-serif;cursor:pointer;text-transform:none;letter-spacing:normal}.dvsh-fb svg{width:15px;height:15px}' +
    '.dvsh-m{position:fixed;right:12px;z-index:9999;min-width:220px;background:#0f1320;border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:6px;box-shadow:0 10px 30px rgba(0,0,0,.55);font:500 14px/1.2 Inter,system-ui,sans-serif}' +
    '.dvsh-m a,.dvsh-m button{text-transform:none;letter-spacing:normal;font-style:normal;transform:none;clip-path:none;margin:0;display:flex;width:100%;align-items:center;gap:10px;padding:11px 12px;border:0;border-radius:10px;background:none;color:#e9ecf3;text-decoration:none;font:inherit;cursor:pointer;text-align:left}' +
    '.dvsh-m a:hover,.dvsh-m button:hover{background:rgba(255,255,255,.06)}' +
    '.dvsh-t{position:fixed;left:50%;bottom:calc(70px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:10000;background:#22d3ee;color:#05060a;padding:10px 16px;border-radius:999px;font:700 13.5px/1 Inter,system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.4)}' +
    '@media print{.dvsh-cr,.dvsh-foot{display:none}}';
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
    { menu.style.right = 'auto'; menu.style.left = Math.max(12, Math.min(r.left, window.innerWidth - 240)) + 'px'; }
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
    // у страниц турниров своя кнопка (крошки на компьютере, верхняя плашка на телефоне) — не дублируем
    var own = document.querySelector('.dv-share,.mshare');
    document.addEventListener('click', function (ev) { var t = ev.target.closest('[data-share]'); if (t) { ev.preventDefault(); ev.stopPropagation(); open(t); } });
    if (own) return;
    // v1.1: без плавающей кнопки (мешала нижнему меню на телефоне). Аккуратная ссылка справа в «хлебных крошках»;
    // на страницах без крошек — скромная кнопка в самом конце страницы.
    var b = document.createElement('button'); b.type = 'button'; b.innerHTML = ICON + '<span>Поделиться</span>';
    b.setAttribute('aria-label', 'Поделиться ссылкой на страницу');
    var crumb = document.querySelector('.dv-crumb');
    if (crumb) { b.className = 'dvsh-cr'; crumb.appendChild(b); }
    else { var w = document.createElement('div'); w.className = 'dvsh-foot'; b.className = 'dvsh-fb'; w.appendChild(b); document.body.appendChild(w); }
    b.onclick = function (ev) { ev.stopPropagation(); open(b); };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
