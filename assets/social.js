/* DOVOD · assets/social.js · v1.0 · 2026-10-29
   Виджет под статьёй: 👁 просмотры, 5 реакций (можно любые сразу, повторный клик снимает), комментарии (ник + текст).
   Разметка на странице: <div id="dv-social" data-a="mgp-2026"></div> (+ необязательный <div id="dv-social-note"></div> вверху).
   Сервер — /api/social. Пока хранилище не подключено (503) — виджет ничего не показывает. */
(function () {
  var box = document.getElementById('dv-social'); if (!box) return;
  var A = box.getAttribute('data-a'); var API = '/api/social';
  var R = [['fire', '🔥', 'Огонь'], ['target', '🎯', 'В точку'], ['wow', '🤯', 'Вау'], ['hmm', '🤔', 'Спорно'], ['lol', '😂', 'Ору']];
  var vid = ''; try { vid = localStorage.getItem('dv_vid') || ''; } catch (e) {}
  if (!/^[A-Za-z0-9_-]{8,40}$/.test(vid)) { vid = Math.random().toString(36).slice(2) + Date.now().toString(36); try { localStorage.setItem('dv_vid', vid); } catch (e) {} }
  var nick = ''; try { nick = localStorage.getItem('dv_nick') || ''; } catch (e) {}
  var S = null, busy = false;
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var css = document.createElement('style');
  css.textContent =
    '#dv-social{margin:44px 0 10px;padding-top:26px;border-top:1px solid rgba(255,255,255,.12);font-size:15px}' +
    '#dv-social .sv{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:14px}' +
    '#dv-social .eye{color:#8b93a7;font-size:14px;white-space:nowrap}' +
    '#dv-social .rx{display:flex;gap:8px;flex-wrap:wrap}' +
    '#dv-social .rb{display:inline-flex;align-items:center;gap:6px;padding:7px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.04);color:#e9ecf3;font:inherit;font-size:14px;cursor:pointer;transition:.15s}' +
    '#dv-social .rb:hover{border-color:rgba(255,255,255,.35)}' +
    '#dv-social .rb.on{border-color:#22d3ee;background:rgba(34,211,238,.14)}' +
    '#dv-social .rb .e{font-size:17px;line-height:1}#dv-social .rb .l{color:#a9b0c2}#dv-social .rb b{font-weight:700}' +
    '#dv-social h3{font-size:18px;margin:26px 0 12px}' +
    '#dv-social form{display:grid;gap:8px;margin-bottom:18px}' +
    '#dv-social input,#dv-social textarea{width:100%;box-sizing:border-box;background:#11141c;border:1px solid rgba(255,255,255,.16);border-radius:10px;color:#e9ecf3;font:inherit;font-size:15px;padding:10px 12px}' +
    '#dv-social textarea{min-height:84px;resize:vertical}#dv-social .hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}' +
    '#dv-social .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}' +
    '#dv-social button.send{background:#22d3ee;color:#05060a;border:0;border-radius:10px;padding:10px 18px;font:inherit;font-weight:700;cursor:pointer}' +
    '#dv-social .msg{color:#f59e0b;font-size:13.5px}' +
    '#dv-social .cm{padding:12px 0;border-top:1px solid rgba(255,255,255,.08)}' +
    '#dv-social .cm .h{font-size:13px;color:#8b93a7;margin-bottom:4px}#dv-social .cm .h b{color:#e9ecf3;font-size:14px}' +
    '#dv-social .cm .ct{white-space:pre-wrap;word-break:break-word;line-height:1.5}' +
    '#dv-social .empty{color:#8b93a7;font-size:14px}' +
    '';
  document.head.appendChild(css);

  function req(method, body) {
    var url = method === 'GET' ? API + '?a=' + encodeURIComponent(A) + '&vid=' + encodeURIComponent(vid) : API;
    return fetch(url, method === 'GET' ? { cache: 'no-store' } : { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(Object.assign({ a: A, vid: vid }, body)) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, st: r.status, j: j }; }); });
  }
  function when(ts) {
    var d = new Date(ts), now = Date.now(), s = (now - ts) / 1000;
    if (s < 60) return 'только что'; if (s < 3600) return Math.floor(s / 60) + ' мин назад';
    if (s < 86400) return Math.floor(s / 3600) + ' ч назад';
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }) + ', ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  }
  function views(n) { var m = n % 10, h = n % 100; return n + ' ' + (m === 1 && h !== 11 ? 'просмотр' : (m >= 2 && m <= 4 && (h < 10 || h >= 20) ? 'просмотра' : 'просмотров')); }
  function render(msg) {
    var mine = S.mine || [];
    var rx = R.map(function (r) {
      var n = (S.reactions || {})[r[0]] || 0, on = mine.indexOf(r[0]) >= 0;
      return '<button type="button" class="rb' + (on ? ' on' : '') + '" data-k="' + r[0] + '" title="' + r[2] + '"><span class="e">' + r[1] + '</span><span class="l">' + r[2] + '</span>' + (n ? '<b>' + n + '</b>' : '') + '</button>';
    }).join('');
    var cms = (S.comments || []).map(function (c) {
      return '<div class="cm"><div class="h"><b>' + esc(c.n) + '</b> · ' + when(c.ts) + '</div><div class="ct">' + esc(c.t) + '</div></div>';
    }).join('') || '<div class="empty">Пока никто не написал — будьте первым.</div>';
    box.innerHTML =
      '<div class="sv"><div class="rx">' + rx + '</div><div class="eye">👁 ' + views(S.views || 0) + '</div></div>' +
      '<h3 id="comments">Комментарии' + ((S.comments || []).length ? ' · ' + S.comments.length : '') + '</h3>' +
      '<form autocomplete="off"><input name="n" maxlength="32" placeholder="Ваш ник" value="' + esc(nick) + '">' +
      '<textarea name="t" maxlength="1000" placeholder="Что думаете о гонке?"></textarea>' +
      '<input class="hp" name="hp" tabindex="-1" aria-hidden="true">' +
      '<div class="row"><button class="send" type="submit">Отправить</button><span class="msg">' + (msg ? esc(msg) : '') + '</span></div></form>' + cms;
    box.querySelectorAll('.rb').forEach(function (b) { b.onclick = function () { react(b.getAttribute('data-k')); }; });
    box.querySelector('form').onsubmit = send;
  }
  function react(k) {
    if (busy) return; busy = true;
    var on = (S.mine || []).indexOf(k) < 0;
    // мгновенный отклик, потом сверка с сервером
    S.mine = on ? (S.mine || []).concat(k) : S.mine.filter(function (x) { return x !== k; });
    S.reactions[k] = Math.max(0, (S.reactions[k] || 0) + (on ? 1 : -1)); render();
    req('POST', { op: 'react', k: k, on: on ? 1 : 0 }).then(function (r) { if (r.ok) { S = r.j; render(); } }).catch(function () {}).then(function () { busy = false; });
  }
  function send(e) {
    e.preventDefault(); if (busy) return;
    var f = e.target, n = f.n.value.trim(), t = f.t.value.trim();
    if (n.length < 2 || t.length < 2) { f.querySelector('.msg').textContent = 'Напишите ник и текст'; return; }
    busy = true; nick = n; try { localStorage.setItem('dv_nick', n); } catch (x) {}
    req('POST', { op: 'comment', n: n, t: t, hp: f.hp.value }).then(function (r) {
      if (r.ok) { S = r.j; render(); } else { f.querySelector('.msg').textContent = (r.j && r.j.err) || 'Не получилось, попробуйте ещё раз'; }
    }).catch(function () { f.querySelector('.msg').textContent = 'Нет связи, попробуйте ещё раз'; }).then(function () { busy = false; });
  }
  req('GET').then(function (r) {
    if (!r.ok) return;                                  // хранилище не подключено — виджета нет
    S = r.j; render();
    var note = document.getElementById('dv-social-note'); if (note) note.style.display = 'block';
    var seen = false; try { seen = sessionStorage.getItem('dv_seen_' + A); } catch (e) {}
    if (!seen) { try { sessionStorage.setItem('dv_seen_' + A, '1'); } catch (e) {} req('POST', { op: 'view' }).catch(function () {}); }
  }).catch(function () {});
})();
