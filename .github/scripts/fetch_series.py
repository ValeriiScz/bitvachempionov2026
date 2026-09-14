#!/usr/bin/env python3
"""
fetch_series · v1.0 · 2026-09-14
Назначение: снимки серийников mafgame для исследования «Гонка за золотую дюжину» —
регламент из описания родителя + результаты всех серий (или составы будущих серий).
Работает в GitHub Actions (прямой доступ к mafgame.org).

Оглавление
  1  настройки
  2  чтение mafgame (Inertia data-page)
  3  выбор серийников: рейтинговые родители (serial=1, parent=null, 1–5★) за YEARS
  4  по родителю: описание/регламент + все серии (результаты или составы)
  5  запись data/research/series/<год>_<id>.json + index.json

Формат серии: rows = [[uid, nick, club, место, total, games, wins, plus, penalty, ci, first_killed]]
"""
import datetime, html, json, os, re, sys, time
import urllib.request

YEARS  = [2025, 2026]
HOSTS  = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame']
PAUSE  = 0.4
OUT    = 'data/research/series'
TODAY  = datetime.date.today().isoformat()
UA     = 'dovod-mafia.com research fetch (github actions)'
errors = []
def log(m): print(m, flush=True)

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

def strip(h):
    if not h: return ''
    h = re.sub(r'<br\s*/?>|</p>|</li>|</h\d>', '\n', h)
    return html.unescape(re.sub(r'<[^>]+>', ' ', h)).replace('\xa0', ' ').strip()

# ── 3 · листинги → серийники ─────────────────────────────────────────────────
listing = {}
for y in YEARS:
    page = 1
    while True:
        p = safe('/tournaments?s=all&y=%d&page=%d' % (y, page))
        if not p: break
        sr = p.get('search_results') or {}
        data = sr.get('data') or []
        for t in data: listing[int(t['id'])] = dict(t, _year=y)
        if page >= (sr.get('last_page') or 1) or not data: break
        page += 1
log('листинг: %d турниров' % len(listing))
parents = [t for t in listing.values() if t.get('serial') and t.get('parent_tournament_id') in (None, 0)
           and 1 <= int(t.get('no_of_stars') or 0) <= 5]
log('рейтинговых серийников: %d' % len(parents))

# ── 4 · по родителю ───────────────────────────────────────────────────────────
def rows_from_results(p):
    out = []
    rating = p.get('rating') or {}
    players = p.get('players') or {}
    for day, blk in (rating.get('results') or {}).items():
        pl = players.get(day) or {}
        for r in blk.get('rows') or []:
            s = r.get('scores') or {}
            info = pl.get(str(r.get('player_id'))) or {}
            out.append([info.get('user_id'), info.get('nickname'), info.get('club_name'), None,
                        round(float(s.get('total_score') or 0), 2), s.get('games_total'), s.get('wins'),
                        s.get('additional_bonus_points'), s.get('penalty_points'), s.get('Ci_sum'), s.get('killed_first_count'),
                        int(day)])
    out.sort(key=lambda r: -r[4])
    for i, r in enumerate(out, 1): r[3] = i
    return out, rating.get('calculated_at')

os.makedirs(OUT, exist_ok=True)
index = []
for par in sorted(parents, key=lambda t: (t['_year'], t['start_date'])):
    pid = int(par['id'])
    log('серийник %d %s (%s)' % (pid, par['name'], par['start_date']))
    pv = safe('/tournaments/%d/results' % pid) or {}
    tour = pv.get('tournament') or {}
    rec = {'id': pid, 'year': par['_year'], 'name': par['name'], 'start_date': par['start_date'], 'stars': par.get('no_of_stars'),
           'city': par.get('city'), 'country': par.get('country'), 'expected': par.get('expected_participants'),
           'description': strip(tour.get('description')), 'regulations': strip(tour.get('regulations')) if isinstance(tour.get('regulations'), str) else tour.get('regulations'),
           'status': tour.get('status'), 'final_rows': None, 'series': []}
    fr, _ = rows_from_results(pv)
    if fr: rec['final_rows'] = fr
    kids = sorted([t for t in listing.values() if t.get('parent_tournament_id') == pid], key=lambda t: t['start_date'])
    for k in kids:
        kid = int(k['id'])
        s = {'id': kid, 'name': k['name'], 'start_date': k['start_date'], 'city': k.get('city'), 'country': k.get('country'),
             'stars': k.get('no_of_stars'), 'expected': k.get('expected_participants'), 'played': None, 'rows': [], 'regs': []}
        if k['start_date'] <= TODAY:
            p = safe('/tournaments/%d/results' % kid) or {}
            rows, calc = rows_from_results(p)
            s['rows'] = rows; s['played'] = bool(rows); s['calculated_at'] = calc
            s['status'] = (p.get('tournament') or {}).get('status')
        if not s['rows']:
            p = safe('/tournaments/%d/participants' % kid) or {}
            regs, seen = [], set()
            for lst, flag in ((p.get('players'), 1), (p.get('applications'), 0)):
                for x in lst or []:
                    if not isinstance(x, dict): continue
                    uid = x.get('user_id'); nick = x.get('nickname') or ((x.get('user') or {}).get('nickname'))
                    if uid and uid not in seen:
                        seen.add(uid); regs.append([uid, nick, flag])
            s['regs'] = regs
        rec['series'].append(s)
    played = sum(1 for s in rec['series'] if s['rows'])
    log('  серий %d, сыграно %d, финал %s' % (len(kids), played, 'есть' if fr else 'нет'))
    fn = '%d_%d.json' % (par['_year'], pid)
    with open(os.path.join(OUT, fn), 'w', encoding='utf-8') as f:
        json.dump(rec, f, ensure_ascii=False, separators=(',', ':'))
    index.append({'file': fn, 'id': pid, 'year': par['_year'], 'name': par['name'], 'start_date': par['start_date'],
                  'stars': par.get('no_of_stars'), 'series': len(kids), 'played': played, 'final': bool(fr)})

with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
    json.dump({'snapshot': TODAY, 'parents': index, 'errors': errors}, f, ensure_ascii=False, indent=1)
if len(index) < 10:
    log('СТОП: серийников подозрительно мало'); sys.exit(1)
log('готово: %d серийников, ошибок %d' % (len(index), len(errors)))
