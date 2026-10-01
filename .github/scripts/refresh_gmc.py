# -*- coding: utf-8 -*-
"""
refresh_gmc.py · v1.1 · 2026-10-01
Назначение: обновить датафайл страницы GMC Europa 2026 (data/gmc2026.js) по протоколам
mafgame.org — без участия человека. До этого страница жила вшитым снимком и протухала.
Запускается GitHub Actions — см. .github/workflows/refresh-gmc.yml.

Оглавление:
  1) настройки и пути
  2) сеть: страницы mafgame (Inertia data-page)
  3) реестр серий турнира 664
  4) протокол серии: баллы, допы, метрики судейства; судья из карточки
  5) сборка: серии, финалисты (топ-2 каждой серии), резерв замен, KPI
  6) предохранители и запись файла

Что робот НЕ трогает (правится руками прямо в data/gmc2026.js):
  meta   — регламент, финал, призовой, плановое число серий;
  judges — таблица судейства из отдельного разбора допов.
"""

import os, re, io, json, html, time, datetime, urllib.request, urllib.error

# ── 1) настройки ─────────────────────────────────────────────────────────────
SERIAL_ID  = 664                        # «German Mafia Cup Europa Edition 2026»
YEAR       = 2026
MAFGAME    = os.environ.get('MAFGAME_BASE_URL', 'https://mafgame.org').rstrip('/')
UA         = os.environ.get('REQUEST_USER_AGENT', 'dovod-mafia.com refresh (github actions)')
PAUSE      = 0.4
MIN_STAGES = 10                         # предохранитель: серий меньше — не пишем файл

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, 'data', 'gmc2026.js')
PAGE = os.path.join(BASE, 'gmc2026.html')
PAGES = [PAGE, os.path.join(BASE, 'series.html')]
SW   = os.path.join(BASE, 'sw.js')

CITY_FIX = {'Nuremberg': 'Nürnberg', 'City of Brussels': 'Brussel'}

log_lines = []
def log(s):
    print(s, flush=True)
    log_lines.append(s)

# ── 2) сеть ──────────────────────────────────────────────────────────────────
def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-US,en'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError('не удалось загрузить %s (%s)' % (url, last))

def inertia(url):
    body = fetch(url)
    m = re.search(r'data-page="([^"]+)"', body)
    if not m:
        raise RuntimeError('нет data-page в ' + url)
    return json.loads(html.unescape(m.group(1)))['props']

def city_of(t):
    c = t.get('city')
    if isinstance(c, dict):
        c = c.get('city')
    c = c or ''
    return CITY_FIX.get(c, c)

def country_of(t):
    c = t.get('city')
    return (c.get('country') or '') if isinstance(c, dict) else ''

def short_name(name):
    """«… Europa Edition 2026 - Köln 1» → «Köln 1»"""
    return (name or '').split(' - ')[-1].strip()

# ── 3) реестр серий ──────────────────────────────────────────────────────────
def registry():
    stages, page, pages = [], 1, 0
    while True:
        p = inertia('%s/tournaments?s=all&y=%d&page=%d' % (MAFGAME, YEAR, page))
        sr = p.get('search_results') or {}
        rows = sr.get('data') or []
        if not rows:
            break
        for t in rows:
            if t.get('parent_tournament_id') == SERIAL_ID:
                stages.append(t)
        pages += 1
        if page >= (sr.get('last_page') or 1):
            break
        page += 1
        time.sleep(PAUSE)
    log('листинг: страниц %d, серий контура %d' % (pages, len(stages)))
    return stages

# ── 4) карточка и протокол серии ─────────────────────────────────────────────
def card(tid):
    """город, страна, судья серии (первым в referees всегда главный судья турнира)"""
    try:
        p = inertia('%s/tournaments/%d/view' % (MAFGAME, tid))
    except Exception:
        return '', '', '', ''
    t = p.get('tournament') or {}
    refs = p.get('referees') or []
    main = t.get('main_referee_id')
    judge = ''
    for r in refs:
        if r.get('id') != main:
            judge = r.get('nickname') or ''
            break
    if not judge and refs:
        judge = refs[0].get('nickname') or ''
    return city_of(t), country_of(t), judge, (t.get('status') or '')

def protocol(tid):
    """→ (rows, metrics) или (None, None), если протокола ещё нет.
    rows: [{u, n, sc, ab, g}] — id, ник, балл, сумма допов, игр."""
    p = inertia('%s/tournaments/%d/results' % (MAFGAME, tid))
    rating = p.get('rating')
    if not isinstance(rating, dict):
        return None, None
    res = rating.get('results')
    if not isinstance(res, dict) or not res:
        return None, None
    rows, seats, ab, pen, wins = [], 0, 0.0, 0.0, 0
    for day, v in res.items():
        pmap = (p.get('players') or {}).get(day) or {}
        for r in v.get('rows') or []:
            pl = pmap.get(str(r.get('player_id'))) or {}
            sc = r.get('scores') or {}
            if sc.get('total_score') is None:
                continue
            g = int(sc.get('games_total') or r.get('games_played') or 0)
            a = float(sc.get('additional_bonus_points') or 0)
            rows.append(dict(u=pl.get('user_id'), n=pl.get('nickname'),
                             sc=round(float(sc['total_score']), 2), ab=round(a, 2), g=g))
            seats += g
            ab    += a
            pen   += float(sc.get('penalty_points') or 0)
            wins  += int(sc.get('wins') or 0)
    if not rows:
        return None, None
    rows.sort(key=lambda x: -x['sc'])
    games = seats // 10 if seats >= 10 else 0
    # схема 10 игроков: 7 красных / 3 чёрных → Σпобед = 30 + 4 × побед города
    town = (wins - 3 * games) / 4.0 if games else None
    met = dict(players=len(rows), games=games,
               town=(int(round(town)) if town is not None else None),
               gb=(round(ab / seats, 4) if seats else None), pen=round(pen, 2))
    return rows, met

# ── 5) сборка ────────────────────────────────────────────────────────────────
DEFAULT_META = dict(
    name='German Mafia Cup Europa Edition 2026', short='GMC Europa 2026', stars=4,
    rule='в финал проходят 1-е и 2-е места каждой серии; замены — третьи места по сумме допов',
    rule_src='FACT: пост канала germanmafiacup2019 от 05.02 (описание турнира с «топ-1» устарело)',
    planned='25–30 серий', final='14–15.11, Кёльн', final_date='2026-11-14',
    final_size='50–60 человек, 18 игр', prize='от 2500–3000 €', entry='взнос финала 100 €',
    mafgame='https://mafgame.org/tournaments/%d/view' % SERIAL_ID,
    obs_snapshot='25.08.2026')

def load_data():
    if not os.path.exists(DATA):
        return dict(snap='', meta=dict(DEFAULT_META), series=[], upcoming=[], nores=[],
                    qualified=[], reserve=[], kpi=[], judges=[])
    s = io.open(DATA, encoding='utf-8').read()
    m = re.search(r'window\.GMC=(\{.*\});', s, re.S)
    if not m:
        raise RuntimeError('не разобрал ' + DATA)
    return json.loads(m.group(1))

def main():
    D = load_data()
    before = json.loads(json.dumps(D))
    old = {s['id']: s for s in D.get('series', [])}
    for u in D.get('upcoming', []) + D.get('nores', []):
        old.setdefault(u['id'], u)

    stages = registry()
    if len(stages) < MIN_STAGES:
        raise SystemExit('предохранитель: серий %d < %d — файл не тронут' % (len(stages), MIN_STAGES))

    today = datetime.date.today().isoformat()
    series, upcoming, nores, added = [], [], [], []

    for t in sorted(stages, key=lambda x: x['start_date']):
        tid  = int(t['id'])
        date = (t.get('start_date') or '')[:10]
        prev = old.get(tid) or {}
        rec  = dict(id=tid, name=short_name(t.get('name')), date=date,
                    city=prev.get('city') or '', country=prev.get('country') or '',
                    judge=prev.get('judge') or '')
        # у будущих и у новых серий карточку спрашиваем: организатор переносит и переименовывает
        if date > today or not rec['city'] or not rec['judge']:
            c, co, j, st = card(tid); time.sleep(PAUSE)
            rec['city'] = c or rec['city'] or city_of(t)
            rec['country'] = co or rec['country']
            rec['judge'] = j or rec['judge']
            rec['closed'] = (st == 'closed')
        else:
            rec['closed'] = bool(prev.get('closed'))

        if date > today:
            upcoming.append(dict(id=tid, city=rec['city'], date=date, name=rec['name']))
            continue

        if prev.get('r'):                       # протокол не меняется — второй раз не тянем
            for k in ('r', 'top2', 'third', 'town', 'games', 'gb', 'pen', 'players'):
                if k in prev:
                    rec[k] = prev[k]
            series.append(rec)
            continue

        rows, met = protocol(tid); time.sleep(PAUSE)
        if not rows:
            nores.append(dict(id=tid, city=rec['city'], date=date, name=rec['name']))
            continue
        rec.update(players=met['players'], games=met['games'], town=met['town'],
                   gb=met['gb'], pen=met['pen'],
                   r=[[r['u'], r['n'], r['sc'], r['ab']] for r in rows])
        added.append('%s %s (%s %.2f)' % (rec['city'], date, rows[0]['n'], rows[0]['sc']))
        series.append(rec)

    series.sort(key=lambda s: s['date'])
    for i, s in enumerate(series, 1):
        s['num'] = i
        r = s.get('r') or []
        s['top2']  = ' · '.join('%s %.2f' % (x[1], x[2]) for x in r[:2])
        s['third'] = ('%s %.2f' % (r[2][1], r[2][2])) if len(r) > 2 else '—'

    # 5a) финалисты: топ-2 каждой сыгранной серии, в хронологии; повтор слота не создаёт
    qualified, seen = [], set()
    for s in series:
        for place, x in enumerate((s.get('r') or [])[:2], 1):
            if x[0] in seen:
                continue
            seen.add(x[0])
            qualified.append(dict(uid=x[0], nick=x[1], series=s['name'], date=s['date'],
                                  place=place, score=x[2], ok=bool(s.get('closed'))))
    # 5b) резерв: третьи места, порядок — сумма допов; уже прошедшие из очереди выпадают
    reserve = []
    for s in series:
        r = s.get('r') or []
        if len(r) > 2 and r[2][0] not in seen:
            reserve.append(dict(uid=r[2][0], nick=r[2][1], series=s['name'],
                                gb=r[2][3], score=r[2][2]))
    reserve.sort(key=lambda x: (-(x['gb'] or 0), -(x['score'] or 0)))

    # 5c) KPI
    played  = len(series)
    total   = played + len(upcoming) + len(nores)
    games   = sum(s.get('games') or 0 for s in series)
    seats   = games * 10
    players = len({x[0] for s in series for x in (s.get('r') or [])})
    town    = sum(s.get('town') or 0 for s in series)
    D['kpi'] = [
        ['%d / %d' % (played, total), 'серий сыграно (по регламенту %s)' % D['meta'].get('planned', '25–30 серий')],
        ['%d' % games, 'игр · %d посадок · %d игроков' % (seats, players)],
        ['%d' % len(qualified), 'слотов в финал занято'],
        ['%.1f%%' % (town * 100.0 / games if games else 0), 'игр выиграл город (%d из %d)' % (town, games)],
    ]

    D['snap'] = datetime.date.today().strftime('%d.%m.%Y')
    D['series'], D['upcoming'], D['nores'] = series, upcoming, nores
    D['qualified'], D['reserve'] = qualified, reserve
    D['meta'] = {**DEFAULT_META, **(D.get('meta') or {})}

    # ── 6) предохранители и запись ───────────────────────────────────────────
    was_played = len(before.get('series', []))
    was_qual   = len(before.get('qualified', []))
    if was_played and played < was_played:
        raise SystemExit('предохранитель: серий с протоколом стало меньше (%d < %d) — файл не тронут'
                         % (played, was_played))
    if was_qual and len(qualified) < was_qual:
        raise SystemExit('предохранитель: финалистов стало меньше (%d < %d) — файл не тронут'
                         % (len(qualified), was_qual))

    body = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    head = ('/* MafgameStat · data/gmc2026.js · снимок %s · собран роботом refresh_gmc.py.\n'
            '   Руками не править: следующий прогон перезапишет. Ручные поля — meta (регламент,\n'
            '   финал, призовой) и judges (таблица судейства из разбора допов). */\n' % D['snap'])
    new = head + 'window.GMC=' + body + ';\n'
    prev_txt = io.open(DATA, encoding='utf-8').read() if os.path.exists(DATA) else ''
    strip = lambda s: re.sub(r'^/\*.*?\*/\n', '', s, flags=re.S)
    changed = strip(prev_txt) != strip(new)
    if changed:
        os.makedirs(os.path.dirname(DATA), exist_ok=True)
        io.open(DATA, 'w', encoding='utf-8').write(new)
        stamp = datetime.date.today().strftime('%Y%m%d')
        # штамп нужен каждой странице, которая грузит датафайл, а не только gmc2026.html:
        # на series.html плитка GMC читает тот же window.GMC и без версии показывает вчерашние цифры
        for page in PAGES:
            if not os.path.exists(page):
                continue
            src = io.open(page, encoding='utf-8').read()
            upd = re.sub(r'<script src="data/gmc2026\.js(\?v=[^"]*)?"></script>',
                         '<script src="data/gmc2026.js?v=%s"></script>' % stamp, src)
            if upd != src:
                io.open(page, 'w', encoding='utf-8').write(upd)
        if os.path.exists(SW):
            sw = io.open(SW, encoding='utf-8').read()
            mm = re.search(r"const CACHE_VERSION = 'dovod-v(\d+)';", sw)
            if mm:
                io.open(SW, 'w', encoding='utf-8').write(
                    sw.replace(mm.group(0), "const CACHE_VERSION = 'dovod-v%d';" % (int(mm.group(1)) + 1)))
                log('CACHE_VERSION → dovod-v%d' % (int(mm.group(1)) + 1))

    log('серий с протоколом: %d из %d · игроков %d · слотов в финал %d · снимок %s'
        % (played, total, players, len(qualified), D['snap']))
    if added: log('новые протоколы: ' + '; '.join(added))
    if nores: log('без протокола: ' + '; '.join('%s %s' % (x['city'], x['date']) for x in nores))
    if upcoming: log('впереди: ' + '; '.join('%s %s' % (x['city'], x['date']) for x in upcoming))
    log('файл ' + ('обновлён' if changed else 'без изменений'))

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        io.open(summary, 'a', encoding='utf-8').write(
            '### GMC · обновление данных\n\n' + '\n'.join('- ' + x for x in log_lines) + '\n')

if __name__ == '__main__':
    main()
