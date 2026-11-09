#!/usr/bin/env node
/* DOVOD · .github/scripts/freeze_tournament.js · v1.0 · 2026-11-09
   Назначение: закрытие турнира по регламенту README («Как ЗАКРЫВАТЬ турнир») одной командой в GitHub Actions
   (у раннера прямой доступ к mafgame.org; из облачной сессии Claude mafgame закрыт).

   Оглавление
     1  чтение mafgame (Inertia data-page)
     2  протоколы → наш формат (тот же convertInertia из data/live.js, что и на сайте)
     3  сверка с официальной таблицей mafgame (до сотых, иначе стоп — ничего не пишем)
     4  запись: data/games_{id}_current.json (заморозка) + data/tournament_{id}.json (standings/winners/champion/closed)

   Запуск:  node .github/scripts/freeze_tournament.js 645
   Что НЕ делает: не трогает data/tournaments.js (статус/подпись карточки) и тексты страниц — это правится руками.
   Стадии-серии (part_data.serial_child_tournament > 0, у финалов серийников) в протоколы финала не попадают.
   Итоговая таблица: стадии от последней к первой; стадия с sum_score_with=1 — нарастающим итогом (как на mafgame). */
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const TID = String(process.argv[2] || process.env.TID || '').trim();
if (!/^\d+$/.test(TID)) { console.error('укажи id турнира: node freeze_tournament.js 645'); process.exit(2); }
const HOSTS = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame'];

// ── 1 · чтение mafgame ──────────────────────────────────────────────────────
async function page(p) {
  let last = '';
  for (const h of HOSTS) for (let a = 1; a <= 3; a++) {
    try {
      const r = await fetch(h + p, { headers: { 'user-agent': 'DOVOD-site (+https://dovod-mafia.com)' } });
      if (!r.ok) { last = h + p + ' ' + r.status; break; }
      const m = (await r.text()).match(/data-page="([^"]+)"/);
      if (!m) { last = 'нет data-page ' + h + p; break; }
      return JSON.parse(m[1].replace(/&quot;/g, '"').replace(/&#039;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')).props;
    } catch (e) { last = h + p + ': ' + e.message; await new Promise(r => setTimeout(r, 1500 * a)); }
  }
  throw new Error(last);
}

(async () => {
  const G = (await page(`/tournaments/${TID}/game_results`)).games;
  const R = await page(`/tournaments/${TID}/results`);
  const PD = G.part_data || {};
  const own = st => !(+((PD[st] || {}).serial_child_tournament) > 0);   // своя стадия, не отборочная серия
  const keep = o => Object.fromEntries(Object.entries(o || {}).filter(([k]) => own(k.split('-')[0])));
  const g2 = { ...G, seats: keep(G.seats), results: keep(G.results), game_outcomes: keep(G.game_outcomes),
               game_comments: keep(G.game_comments), part_data: Object.fromEntries(Object.entries(PD).filter(([k]) => own(k))) };

  // ── 2 · протоколы через convertInertia сайта ──────────────────────────────
  global.window = global; global.document = { body: null, addEventListener() {}, querySelector() { return null; }, getElementById() { return null; } };
  global.localStorage = { getItem() { return null; }, setItem() {} };
  eval(fs.readFileSync(path.join(ROOT, 'data', 'live.js'), 'utf8'));
  const tjPath = path.join(ROOT, 'data', `tournament_${TID}.json`);
  const TJ = JSON.parse(fs.readFileSync(tjPath, 'utf8'));
  const fc = +TJ.final_coef || 1;
  const conv = window.convertInertia(JSON.parse(JSON.stringify(g2)), TID, fc);
  if (!conv || !conv.games.length) throw new Error('протоколов нет');
  const unknown = conv.games.reduce((n, g) => n + g.tables.filter(t => t.winner === 'unknown').length, 0);
  if (unknown) throw new Error(`столов без исхода: ${unknown} — турнир не доигран, замораживать рано`);

  // ── 3 · сверка с официальной таблицей ─────────────────────────────────────
  const nick = {}; for (const k in G.seats) nick[G.seats[k].player_id] = G.seats[k].original_nickname;
  const stages = Object.keys(R.rating.results).filter(own).map(Number).sort((a, b) => a - b);
  const sumBy = (pred) => { const P = {}; conv.games.forEach(g => { if (!pred(g)) return; g.tables.forEach(t => t.seats.forEach(s => {
    const p = P[s.name] || (P[s.name] = { s: 0, w: 0, n: 0 }); p.s += s.wpts + s.aps + s.ci; p.n++; if (s.result === 'W') p.w++; })); }); return P; };
  // стадия в conv — по порядку: игры стадий идут подряд; соотносим по числу сессий part_data
  let off = 0; const gamesOf = {};
  for (const st of stages) { const n = +(PD[st] || {}).sessions || 0; gamesOf[st] = conv.games.slice(off, off + n); off += n; }
  const bad = []; const rowsOf = {};
  for (const st of stages) {
    const inc = +(PD[st] || {}).sum_score_with === 1;
    const set = new Set(stages.filter(x => x === st || (inc && x < st)).flatMap(x => gamesOf[x]));
    const P = sumBy(g => set.has(g));
    rowsOf[st] = R.rating.results[st].rows.map((r, i) => {
      const n = nick[r.player_id] || String(r.player_id), our = P[n] ? P[n].s : 0;
      if (Math.abs(our - r.scores.total_score) > 0.006) bad.push(`стадия ${st} ${n}: mafgame ${r.scores.total_score}, у нас ${our.toFixed(4)}`);
      return { place: i + 1, name: n, sigma: +(+r.scores.total_score).toFixed(4), wins: r.scores.wins, games: r.games_played, st };
    });
  }
  if (bad.length) { console.error('СВЕРКА НЕ СОШЛАСЬ — ничего не пишу:\n' + bad.join('\n')); process.exit(1); }

  // ── 4 · запись ─────────────────────────────────────────────────────────────
  const today = new Date().toISOString().slice(0, 10).split('-').reverse().join('.');
  const nGames = conv.games.length;
  const out = { tournament_id: +TID, games_played: nGames, games_total: nGames, live: false, win_self: false, closed: true,
    note: `Протоколы ${nGames} игр заморожены ${today} после окончания турнира (freeze_tournament.js). Суммы совпадают с официальной таблицей mafgame.`,
    games: conv.games };
  fs.writeFileSync(path.join(ROOT, 'data', `games_${TID}_current.json`), JSON.stringify(out, null, 1) + '\n');

  const seen = new Set(), standings = [];
  for (const st of stages.slice().reverse()) for (const r of rowsOf[st]) {
    if (seen.has(r.name)) continue; seen.add(r.name);
    const lab = (+(PD[st] || {}).is_final === 1) ? 'финал' : ((PD[st] || {}).name || 'квалификация').toLowerCase();
    standings.push({ place: standings.length + 1, name: r.name, sigma: r.sigma, stage: lab, wins: r.wins, games: r.games });
  }
  Object.assign(TJ, { closed: true, in_progress: false, upcoming: false, games_played: nGames, games_total: nGames,
    champion: standings[0].name, winners: standings.slice(0, 3).map(r => r.name), standings,
    reconciliation: `Сверено с официальной таблицей mafgame ${today}: ` + stages.map(st => `${(PD[st] || {}).name || st} ${rowsOf[st].length}/${rowsOf[st].length}`).join(', ') + ' — совпадают до сотых.' });
  fs.writeFileSync(tjPath, JSON.stringify(TJ, null, 1) + '\n');
  console.log(`заморожено: ${nGames} игр; чемпион ${standings[0].name}; топ-3 ${TJ.winners.join(', ')}; строк в таблице ${standings.length}`);
})().catch(e => { console.error('ошибка: ' + e.message); process.exit(1); });
