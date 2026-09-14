#!/usr/bin/env python3
"""
fetch_ledgers · v1.0 · 2026-09-14
Назначение: разовая (и повторяемая) выкачка данных рейтинга mafgame для исследования
«Гонка за золотую дюжину»: рейтинги по годам, листинги турниров, леджеры баллов игроков,
таблицы баллов рейтинговых турниров. Работает в GitHub Actions (прямой доступ к mafgame.org).

Оглавление
  1  настройки
  2  чтение mafgame (Inertia data-page)
  3  рейтинги по годам (топ-N)
  4  листинги турниров по годам
  5  леджеры игроков (/user/{id}/view → rating_points, все годы сразу)
  6  таблицы баллов рейтинговых турниров (/tournaments/{id}/points)
  7  запись файлов в data/research/ledger/

Выход (JSON, компактно):
  ratings.json      {год: [{pos, uid, nick, rating, ...}]}
  tournaments.json  {год: [листинг с полями id,name,start_date,no_of_stars,serial,parent_tournament_id,teams,...]}
  ledgers.json      {uid: {nick, rp: [[год, tid, дата, место, баллы, serial]]}}
  points.json       {tid: [[uid, nick, место, баллы, дата]]}
  meta.json         {snapshot, counts, errors}
"""
import datetime, html, json, os, re, sys, time
import urllib.request

# ── 1 · настройки ─────────────────────────────────────────────────────────────
YEARS      = [2024, 2025, 2026]
TOP_N      = int(os.environ.get('TOP_N', '120'))     # сколько игроков рейтинга брать в леджеры, на год
HOSTS      = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame']
PAUSE      = 0.4
OUT        = 'data/research/ledger'
TODAY      = datetime.date.today().isoformat()
UA         = 'dovod-mafia.com research fetch (github actions)'
errors     = []

def log(m): print(m, flush=True)

# ── 2 · чтение mafgame ────────────────────────────────────────────────────────
def fetch_page(path):
    last = None
    for host in HOSTS:
        for attempt in (1, 2, 3):
            try:
                req = urllib.request.Request(host + path, headers={'User-Agent': UA, 'Accept': 'text/html'})
                with urllib.request.urlopen(req, timeout=45) as r:
                    body = r.read().decode('utf-8', 'replace')
                m = re.search(r'data-page="([^"]+)"', body)
                if not m:
                    last = 'no data-page ' + host + path; break
                return json.loads(html.unescape(m.group(1)))['props']
            except Exception as e:
                last = '%s%s: %s' % (host, path, e); time.sleep(1.5 * attempt)
    raise RuntimeError(last or path)

def safe(path):
    try:
        p = fetch_page(path); time.sleep(PAUSE); return p
    except Exception as e:
        errors.append(str(e)); log('  ! ' + str(e)); return None

def scalars(d, keep_nested=()):
    out = {}
    for k, v in d.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            out[k] = v
        elif k in keep_nested:
            out[k] = v
    return out

# ── 3 · рейтинги по годам ─────────────────────────────────────────────────────
ratings = {}
for y in YEARS:
    rows, page = [], 1
    while len(rows) < TOP_N:
        p = safe('/rating?year=%d&page=%d' % (y, page))
        if not p: break
        sr = p.get('search_results') or {}
        data = sr.get('data') or []
        if not data: break
        for r in data:
            u = r.get('user') or {}
            row = scalars(r)
            row['uid'] = u.get('id'); row['nick'] = u.get('nickname')
            rows.append(row)
        if page == 1:
            log('рейтинг %d: всего игроков %s, страниц %s' % (y, sr.get('total'), sr.get('last_page')))
            ratings.setdefault('_totals', {})[str(y)] = {'total': sr.get('total'), 'last_page': sr.get('last_page')}
        if page >= (sr.get('last_page') or 1): break
        page += 1
    ratings[str(y)] = rows
    log('рейтинг %d: снято %d строк' % (y, len(rows)))

# ── 4 · листинги турниров ─────────────────────────────────────────────────────
tournaments = {}
for y in YEARS:
    rows, page = {}, 1
    while True:
        p = safe('/tournaments?s=all&y=%d&page=%d' % (y, page))
        if not p: break
        sr = p.get('search_results') or {}
        data = sr.get('data') or []
        for t in data:
            rows[int(t['id'])] = scalars(t, keep_nested=('cups',))
        if page >= (sr.get('last_page') or 1) or not data: break
        page += 1
    tournaments[str(y)] = list(rows.values())
    log('турниры %d: %d' % (y, len(rows)))

# ── 5 · леджеры игроков ───────────────────────────────────────────────────────
uids = []
for y in YEARS:
    for r in ratings[str(y)]:
        if r['uid'] and r['uid'] not in uids: uids.append(r['uid'])
log('леджеры: уникальных игроков %d' % len(uids))
ledgers = {}
for i, uid in enumerate(uids, 1):
    p = safe('/user/%d/view' % uid)
    if not p: continue
    ud = p.get('user_data') or {}
    rp = []
    for r in (p.get('rating_points') or []):
        t = r.get('tournament') or {}
        rp.append([r.get('year'), r.get('tournament_id'), r.get('date_acquired'),
                   r.get('position'), float(r.get('points') or 0), int(bool(t.get('serial'))),
                   int(bool(r.get('series_participation')))])
    city = ud.get('user_city') or {}
    ledgers[str(uid)] = {'nick': ud.get('nickname'), 'country': city.get('country'), 'city': city.get('city'), 'rp': rp}
    if i % 25 == 0: log('  леджеры %d/%d' % (i, len(uids)))

# ── 6 · таблицы баллов рейтинговых турниров ───────────────────────────────────
def gives_points(t):
    return (t.get('parent_tournament_id') in (None, 0)) and 1 <= int(t.get('no_of_stars') or 0) <= 5

tids = []
for y in YEARS:
    for t in tournaments[str(y)]:
        if gives_points(t) and (t.get('start_date') or '9999') <= TODAY:
            tids.append(int(t['id']))
log('таблицы баллов: турниров %d' % len(tids))
points = {}
for i, tid in enumerate(tids, 1):
    p = safe('/tournaments/%d/points' % tid)
    if not p: continue
    rows = []
    for r in (p.get('points') or []):
        u = r.get('user') or {}
        rows.append([r.get('user_id'), u.get('nickname'), r.get('position'), float(r.get('points') or 0), r.get('date_acquired')])
    points[str(tid)] = rows
    if i % 25 == 0: log('  таблицы %d/%d' % (i, len(tids)))

# ── 7 · запись ────────────────────────────────────────────────────────────────
os.makedirs(OUT, exist_ok=True)
def dump(name, obj):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    log('записан %s (%d КБ)' % (name, os.path.getsize(os.path.join(OUT, name)) // 1024))
dump('ratings.json', ratings)
dump('tournaments.json', tournaments)
dump('ledgers.json', ledgers)
dump('points.json', points)
dump('meta.json', {'snapshot': TODAY, 'top_n': TOP_N, 'players': len(ledgers), 'tournaments_points': len(points),
                   'listing': {y: len(tournaments[str(y)]) for y in YEARS}, 'errors': errors})
if len(ledgers) < 50 or len(points) < 30:
    log('СТОП: данных подозрительно мало'); sys.exit(1)
log('готово; ошибок %d' % len(errors))
