#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh_markery · v1.0.1 · 2026-11-12 (диагностика ответа markery в аннотациях Actions) · v1.0 · 2026-11-12
Назначение: свежий ELO markery.online (справочно, опора сайта — MMR) для составов
незавершённых турниров DOVOD — без участия человека. Запускается GitHub Actions
(.github/workflows/refresh-markery.yml), 2 раза в неделю и при новом составе.

Оглавление
  1  настройки и предохранители
  2  сеть: таблица ELO markery (POST /api/elo_select_by_filter, открыто, без входа)
  3  сопоставление игрока: markery_id → mafgame-uid из ссылки профиля → ник (только однозначный)
  4  патч data/participants_{id}.json (только незавершённые турниры из tournaments.js)
  5  ср. ELO на карточках data/tournaments.js, версия кэша sw.js

Тир ELO (справочно) — полосы по историческим тирам markery у наших игроков:
  L ≥1650 (ГИПОТЕЗА: между S-макс 1573 и L-мин 1717) · S ≥1300 · A ≥1197 · B ≥1075 · C ≥994 · D ≥937 · E ≥886 · F ниже.
Предохранители: в таблице меньше MIN_ROWS строк или контрольный игрок не найден → выход с ошибкой, файлы не пишутся.
Ручной режим (когда markery не пускает робота): --rows rows.json — список [pid, name, elo, rank, date, url].
"""
import datetime, io, json, os, re, sys, time, glob
import urllib.request, urllib.error

URL = 'https://markery.online/api/elo_select_by_filter'
UA = 'Mozilla/5.0 (dovod-mafia.com elo refresh; github actions)'
MIN_ROWS = 3000
BANDS = [('L', 1650), ('S', 1300), ('A', 1197), ('B', 1075), ('C', 994), ('D', 937), ('E', 886)]
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODAY = datetime.date.today().isoformat()

def log(m): print(m, flush=True)
def fail(m): print('::error::' + m, flush=True); sys.exit(1)
def tier(e):
    if e is None: return None
    for t, v in BANDS:
        if e >= v: return t
    return 'F'

# ── 2) сеть ──
def page(skip, count=1000, tries=3):
    body = json.dumps({'eloType': 101, 'region': None, 'preferOrganizationInfo': None, 'skip': skip, 'count': count}).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(URL, data=body, method='POST', headers={'User-Agent': UA, 'Content-Type': 'application/json', 'Accept': 'application/json', 'Origin': 'https://markery.online', 'Referer': 'https://markery.online/eloRating'})
            with urllib.request.urlopen(req, timeout=60) as r: raw = r.read().decode('utf-8', 'replace'); st = r.status
            try: a = json.loads(raw)
            except Exception: a = None
            if isinstance(a, list): return a
            print('::warning::markery skip=%d: HTTP %s, не список: %s' % (skip, st, raw[:300].replace('\n', ' ')), flush=True)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:300].replace('\n', ' ')
            print('::warning::markery skip=%d: HTTP %s %s' % (skip, e.code, body), flush=True)
        except Exception as e:
            print('::warning::markery skip=%d: %s' % (skip, e), flush=True)
        time.sleep(5 * (i + 1))
    return None

def fetch_rows():
    rows = []
    for skip in range(0, 40000, 1000):
        a = page(skip)
        if a is None: fail('markery не ответил (skip=%d) — ничего не пишу' % skip)
        for k, e in enumerate(a):
            p = e.get('playerInfo') or {}; t = e.get('tournament') or {}
            rows.append([p.get('playerId'), p.get('name'), e.get('eloAfter'), e.get('rank') or (skip + k + 1), (t.get('date') or '')[:10], p.get('url') or ''])
        if len(a) < 1000: break
        time.sleep(0.5)
    return rows

# ── 3) сопоставление ──
def index(rows):
    by_pid, by_uid, by_name = {}, {}, {}
    for r in rows:
        by_pid[r[0]] = r
        m = re.search(r'mafgame\.org/user/(\d+)', r[5] or '')
        if m: by_uid[int(m.group(1))] = r
        by_name.setdefault((r[1] or '').strip().lower(), []).append(r)
    def find(uid, nick, pid):
        if pid and pid in by_pid: return by_pid[pid], 'id'
        if uid and int(uid) in by_uid: return by_uid[int(uid)], 'uid'
        if not pid:
            c = by_name.get((nick or '').strip().lower()) or []
            if len(c) == 1: return c[0], 'name'
        return None, None
    return find

# ── 4) составы незавершённых турниров ──
def open_ids():
    s = io.open(os.path.join(BASE, 'data', 'tournaments.js'), encoding='utf-8').read()
    ids = []
    for m in re.finditer(r'\{\s*"id":\s*"(\d+)"', s):
        b = s.find('\n  }', m.start()); blk = s[m.start():b]
        if '"status": "finished"' not in blk: ids.append(m.group(1))
    return ids

def patch(find, snap):
    stat = {'files': 0, 'id': 0, 'uid': 0, 'name': 0, 'miss': 0}
    for tid in open_ids():
        f = os.path.join(BASE, 'data', 'participants_%s.json' % tid)
        if not os.path.exists(f): continue
        raw = io.open(f, encoding='utf-8').read(); d = json.loads(raw)
        for p in d.get('players') or []:
            r, how = find(p.get('uid'), p.get('nick'), p.get('markery_id'))
            if not r: stat['miss'] += 1; continue
            stat[how] += 1
            e = round(float(r[2])) if r[2] is not None else None
            p.update({'markery_id': r[0], 'r_elo_cur': e, 'r_rank': r[3], 'r_tier': tier(e), 'elo_snap': snap, 'mk_match': how, 'mk_last': r[4] or None})
        d.setdefault('meta', {})['elo_snap'] = snap
        new = json.dumps(d, ensure_ascii=False, indent=1)
        if new.strip() != raw.strip(): io.open(f, 'w', encoding='utf-8').write(new + '\n'); stat['files'] += 1
    return stat

# ── 5) карточки и кэш ──
def update_cards():
    path = os.path.join(BASE, 'data', 'tournaments.js'); s = io.open(path, encoding='utf-8').read(); n = 0
    for tid in open_ids():
        m = re.search(r'\{\s*"id":\s*"%s"' % tid, s); a = m.start(); b = s.find('\n  }', a); blk = s[a:b]
        if '"eloAvg"' not in blk: continue
        try: d = json.load(io.open(os.path.join(BASE, 'data', 'participants_%s.json' % tid), encoding='utf-8'))
        except Exception: continue
        P = d.get('players') or []; v = [p['r_elo_cur'] for p in P if p.get('r_elo_cur') is not None]
        if not v: continue
        nb = re.sub(r'"eloAvg":\s*[\d.]+', '"eloAvg": %d' % round(sum(v) / len(v)), blk)
        nb = re.sub(r'"eloN":\s*\d+', '"eloN": %d' % len(v), nb)
        nb = re.sub(r'"eloTotal":\s*\d+', '"eloTotal": %d' % len(P), nb)
        if nb != blk: s = s[:a] + nb + s[b:]; n += 1
    if n: io.open(path, 'w', encoding='utf-8').write(s)
    return n

def bump_sw():
    p = os.path.join(BASE, 'sw.js'); s = io.open(p, encoding='utf-8').read()
    m = re.search(r"CACHE_VERSION = 'dovod-v(\d+)'", s)
    if m: io.open(p, 'w', encoding='utf-8').write(s.replace(m.group(0), "CACHE_VERSION = 'dovod-v%d'" % (int(m.group(1)) + 1)))

def main():
    if '--rows' in sys.argv:
        rows = json.load(io.open(sys.argv[sys.argv.index('--rows') + 1], encoding='utf-8'))
        snap = sys.argv[sys.argv.index('--snap') + 1] if '--snap' in sys.argv else TODAY
    else:
        rows = fetch_rows(); snap = TODAY
        if len(rows) < MIN_ROWS: fail('в таблице markery всего %d строк — подозрительно, ничего не пишу' % len(rows))
        if not any(r[0] == 10035 for r in rows): fail('контрольный игрок (Tripok, 10035) не найден — ничего не пишу')
    log('markery: строк %d · снимок %s' % (len(rows), snap))
    st = patch(index(rows), snap); c = update_cards()
    log('составы: файлов изменено %d · по id %d · по mafgame-uid %d · по нику %d · не найдено %d · карточек %d' % (st['files'], st['id'], st['uid'], st['name'], st['miss'], c))
    if st['files'] or c: bump_sw()

if __name__ == '__main__': main()
