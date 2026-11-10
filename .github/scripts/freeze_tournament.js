#!/usr/bin/env node
/* DOVOD · .github/scripts/freeze_tournament.js · v1.3 · 2026-11-10 (награды mafgame: awards + MVP на карточку) · v1.2 · 2026-11-09 (точный Ci в протоколах: Ci_sum/k вместо 0.33) · v1.1 · 2026-11-09 (Ci: допуск на округление протоколов mafgame) · v1.0 · 2026-11-09
   Назначение: закрытие турнира по регламенту README («Как ЗАКРЫВАТЬ турнир») одной командой в GitHub Actions
   (у раннера прямой доступ к mafgame.org; из облачной сессии Claude mafgame закрыт).

   Оглавление
     1  чтение mafgame (Inertia data-page)
     2  протоколы → наш формат (тот же convertInertia из data/live.js, что и на сайте)
     3  сверка с официальной таблицей mafgame (до сотых, иначе стоп — ничего не пишем)
     4  запись: data/games_{id}_current.json (заморозка) + data/tournament_{id}.json (standings/winners/champion/closed)

   Запуск:  node .github/scripts/freeze_tournament.js 645
   Что НЕ делает: статус/подпись карточки в data/tournaments.js и тексты страниц — руками. v1.3: MVP на карточку и награды (awards) в tournament_{id}.json пишет сам.
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


// ── 5 · награды mafgame (v1.3): props.tournament.stats из /results → awards + mvp ─────────────
// Формат как у закрытых вручную 673/687/692: «Ник (балл)», дон/шериф — «Ник (победы/ср. доп)».
function awardsFrom(R) {
  const S = (R.tournament || {}).stats; if (!S) return null;
  const nick = {}; for (const st in (R.players || {})) for (const pid in R.players[st]) { const x = R.players[st][pid]; nick[x.user_id] = x.nickname; }
  const top = (pre, fmt) => [1, 2, 3].map(i => { const u = S[`${pre}_${i}_user_id`]; return u && nick[u] ? fmt(nick[u], i) : null; }).filter(Boolean);
  const v = (pre) => (n, i) => `${n} (${S[`${pre}_${i}_value`]})`;
  const ws = (pre) => (n, i) => `${n} (${parseInt(S[`${pre}_${i}_value`], 10)}/${S[`${pre}_${i}_value_avg`]})`;
  const a = { most_valuable_players: top('mvp', v('mvp')), most_valuable_mafia: top('mv_black', v('mv_black')),
    most_valuable_citizen: top('mv_red', v('mv_red')), best_don: top('mv_don', ws('mv_don')), best_sheriff: top('mv_sheriff', ws('mv_sheriff')),
    most_killed: S.most_killed_user_id && nick[S.most_killed_user_id] ? [`${nick[S.most_killed_user_id]} (${S.most_killed_value})`] : [] };
  for (const k in a) if (!a[k].length) delete a[k];
  const mvp = S.mvp_1_user_id && nick[S.mvp_1_user_id] ? nick[S.mvp_1_user_id] : null;
  return Object.keys(a).length ? { awards: a, mvp } : null;
}
// MVP на карточке архива (data/tournaments.js) — единственная правка карточки, которую делает скрипт
function patchCardMvp(tid, mvp) {
  const p = path.join(ROOT, 'data', 'tournaments.js'); let s = fs.readFileSync(p, 'utf8');
  const a = s.indexOf(`"id": "${tid}"`); if (a < 0 || !mvp) return false;
  const b = s.indexOf('\n  }', a); if (b < 0) return false;
  let blk = s.slice(a, b); const val = JSON.stringify(mvp);
  if (/"mvp":\s*"[^"]*"/.test(blk)) blk = blk.replace(/"mvp":\s*"[^"]*"/, `"mvp": ${val}`);
  else blk = blk.replace(/\s*$/, '') + `,\n    "mvp": ${val}`;
  const n = s.slice(0, a) + blk + s.slice(b); if (n === s) return false; fs.writeFileSync(p, n); return true;
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
    const p = P[s.name] || (P[s.name] = { s: 0, c: 0, k: 0, w: 0, n: 0 }); p.s += s.wpts + s.aps + s.ci; p.c += s.ci; if (s.ci) p.k++; p.n++; if (s.result === 'W') p.w++; })); }); return P; };
  // стадия в conv — по порядку: игры стадий идут подряд; соотносим по числу сессий part_data
  let off = 0; const gamesOf = {};
  for (const st of stages) { const n = +(PD[st] || {}).sessions || 0; gamesOf[st] = conv.games.slice(off, off + n); off += n; }
  const bad = [], ciRound = []; const rowsOf = {};
  for (const st of stages) {
    const inc = +(PD[st] || {}).sum_score_with === 1;
    const set = new Set(stages.filter(x => x === st || (inc && x < st)).flatMap(x => gamesOf[x]));
    const P = sumBy(g => set.has(g));
    rowsOf[st] = R.rating.results[st].rows.map((r, i) => {
      const n = nick[r.player_id] || String(r.player_id), p = P[n] || { s: 0, c: 0, k: 0 }, tot = +r.scores.total_score, ci = +r.scores.Ci_sum || 0;
      /* v1.1: Ci в протоколах игр mafgame хранит с двумя знаками (0.33), а в таблице считает точно (1/3) — расхождение до 0.005 на каждую
         игру с Ci. Поэтому: всё, кроме Ci, обязано биться до сотых; Ci — в пределах округления. Иначе стоп. */
      if (Math.abs(p.s - tot) > 0.006) {
        const restOk = Math.abs(p.s - p.c + ci - tot) <= 0.006, ciOk = Math.abs(p.c - ci) <= 0.005 * p.k + 0.001;
        if (restOk && ciOk) ciRound.push(`${n}: Ci по играм ${p.c.toFixed(2)}, в таблице ${ci.toFixed(4)}`);
        else bad.push(`стадия ${st} ${n}: mafgame ${tot}, у нас ${p.s.toFixed(4)} (Ci у нас ${p.c.toFixed(4)}, у mafgame ${ci.toFixed(4)})`);
      }
      return { place: i + 1, name: n, sigma: +(+r.scores.total_score).toFixed(4), wins: r.scores.wins, games: r.games_played, st };
    });
  }
  if (bad.length) { console.error('СВЕРКА НЕ СОШЛАСЬ — ничего не пишу:\n' + bad.join('\n')); process.exit(1); }
  if (ciRound.length) console.log('Ci в пределах округления mafgame:\n  ' + ciRound.join('\n  '));
  /* v1.2: восстанавливаем точный Ci. По регламенту 7.5 величина Ci у игрока одна на все его отстрелы на дистанции, поэтому
     при округлении в протоколах (0.33) ставим каждому его месту с Ci точное значение Ci_sum / k — тогда таблица страницы,
     которая суммирует протоколы, бьётся с mafgame до сотых, а не «9.79 против 9.80». */
  for (const st of stages) for (const r of R.rating.results[st].rows) {
    const n = nick[r.player_id], ci = +r.scores.Ci_sum || 0; if (!n || !ci) continue;
    const seatsCi = conv.games.filter(g => gamesOf[st].includes(g)).flatMap(g => g.tables.flatMap(t => t.seats.filter(s => s.name === n && s.ci)));
    const sum = seatsCi.reduce((a, s) => a + s.ci, 0);
    if (!seatsCi.length || Math.abs(sum - ci) < 1e-6 || Math.abs(sum - ci) > 0.005 * seatsCi.length + 0.001) continue;
    if (seatsCi.some(s => Math.abs(s.ci - seatsCi[0].ci) > 0.011)) continue;           // разные величины — не трогаем
    seatsCi.forEach(s => { s.ci = +(ci / seatsCi.length).toFixed(6); s.sigma = +(s.wpts + s.aps + s.ci).toFixed(6); });
  }

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
    reconciliation: `Сверено с официальной таблицей mafgame ${today}: ` + stages.map(st => `${(PD[st] || {}).name || st} ${rowsOf[st].length}/${rowsOf[st].length}`).join(', ') + ' — совпадают до сотых' + (ciRound.length ? ` (кроме округления Ci в протоколах mafgame: ${ciRound.join('; ')}; в таблице — официальные суммы)` : '') + '.' });
  const AW = awardsFrom(R); if (AW) { TJ.awards = AW.awards; if (AW.mvp) TJ.mvp = AW.mvp; }
  fs.writeFileSync(tjPath, JSON.stringify(TJ, null, 1) + '\n');
  if (AW && AW.mvp && patchCardMvp(TID, AW.mvp)) console.log('карточка: MVP ' + AW.mvp);
  console.log(`заморожено: ${nGames} игр; чемпион ${standings[0].name}; топ-3 ${TJ.winners.join(', ')}; строк в таблице ${standings.length}`);
})().catch(e => { console.error('ошибка: ' + e.message); process.exit(1); });
