#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh_mafiastats · v1.3 · 2026-11-06 (тестовая шкала тиров для отдельных турниров: apply/variants в mmr_tiers.json) · v1.2 · 2026-11-06 (тир по MMR — калибровка «шанс финала», data/research/mmr_tiers.json) · v1.1 · 2026-11-03 (тир по MMR: линейка markery по долям) · v1.0 · 2026-11-03
Назначение: подтянуть единый рейтинг MMR с mafiastats.com (открытый API, без ключей)
для игроков сайта DOVOD — без участия человека. Запускается GitHub Actions
(.github/workflows/refresh-mafiastats.yml).

Оглавление
  1  настройки и предохранители
  2  сеть: mafiastats API и рейтинг mafgame (Inertia data-page)
  3  какие игроки нужны (составы турниров сайта + рейтинг mafgame текущего года)
  4  MMR по mafgame-id: /rating/mafgame/{id}
  5  топы федераций: сейчас и на конец 2024/2025
  6  запись data/mmr.json, патч data/participants_*.json, версия кэша sw.js
  7  тир по MMR: пороги подбираются так, чтобы доли тиров L…F среди игроков
     с обоими рейтингами совпадали с долями тиров markery (квантильная линейка)

Правила mafiastats (fair use): кэшировать, ходить спокойно, ставить ссылку на профиль
игрока на mafiastats.com. Рейтинг пересчитывается несколько раз в неделю — чаще 2 раз
в неделю ходить незачем.

Предохранители (выход с ошибкой, файлы не пишутся):
  - API не ответил на контрольный запрос;
  - найдено меньше MIN_SHARE от запрошенных игроков (значит, API отдаёт мусор).
"""
import datetime, html, io, json, os, re, sys, time, glob
import urllib.request, urllib.error, urllib.parse

# ── 1) настройки ─────────────────────────────────────────────────────────────
API      = os.environ.get('MAFIASTATS_API', 'https://mafiastats.com/api/v1').rstrip('/')
MAFGAME  = os.environ.get('MAFGAME_BASE_URL', 'https://mafgame.org').rstrip('/')
UA       = 'dovod-mafia.com mmr refresh (github actions)'
PAUSE    = 0.3
YEAR     = datetime.date.today().year
MIN_SHARE = 0.5
FEDS     = ['mafgame', 'imafia', 'emotion', 'mwt']
TOP_N    = 100

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(BASE, 'data', 'mmr.json')
SW   = os.path.join(BASE, 'sw.js')

def log(m): print(m, flush=True)
def fail(m): print('::error::' + m, flush=True); sys.exit(1)

# ── 2) сеть ──────────────────────────────────────────────────────────────────
def get(url, accept='application/json', tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code == 404: return 404, ''
            if e.code == 429 or e.code >= 500: time.sleep(5 * (i + 1)); continue
            return e.code, ''
        except Exception:
            time.sleep(3 * (i + 1))
    return 0, ''

def api(path, **params):
    q = urllib.parse.urlencode(params, doseq=True)
    st, body = get(API + path + ('?' + q if q else ''))
    return json.loads(body) if st == 200 and body else None

def mafgame_page(path):
    st, body = get(MAFGAME + path, accept='text/html')
    if st != 200: return None
    m = re.search(r'data-page="([^"]+)"', body)
    return json.loads(html.unescape(m.group(1)))['props'] if m else None

# ── 3) какие игроки нужны ────────────────────────────────────────────────────
def wanted_ids():
    ids = {}
    for f in sorted(glob.glob(os.path.join(BASE, 'data', 'participants_*.json'))):
        try:
            d = json.load(io.open(f, encoding='utf-8'))
        except Exception:
            continue
        for p in d.get('players') or []:
            if p.get('uid'): ids[str(p['uid'])] = p.get('nick')
    n_part = len(ids)
    page, last = 1, 1
    while page <= last:
        props = mafgame_page('/rating?year=%d&page=%d' % (YEAR, page))
        if not props: log('  рейтинг mafgame: страница %d не открылась — пропускаю' % page); break
        sr = props['search_results']; last = sr.get('last_page') or 1
        for r in sr['data']:
            ids.setdefault(str(r['user_id']), (r.get('user') or {}).get('nickname'))
        page += 1; time.sleep(PAUSE)
    log('игроков к запросу: %d (из составов турниров %d)' % (len(ids), n_part))
    return ids

# ── 4) MMR по mafgame-id ─────────────────────────────────────────────────────
def r1(v): return None if v is None else round(float(v), 1)

def lookup(uid):
    j = api('/rating/mafgame/%s' % uid)
    if not j or not j.get('data'): return None
    d = j['data']; r = d.get('rating') or {}; o = d.get('online_rating') or {}
    return {'id': d.get('player_id'), 'mmr': r1(r.get('rating')), 'peak': r1(r.get('peak_rating')),
            'rank': r.get('rank'), 'chg': r1(r.get('rating_change')), 'games': r.get('games_count'),
            'wr': r.get('win_rate'), 'last': (r.get('last_game_at') or '')[:10] or None,
            'online': r1(o.get('rating')), 'online_games': o.get('games_count')}

# ── 5) топы федераций ────────────────────────────────────────────────────────
def tops():
    out = {}
    for period in ['now', YEAR - 1, YEAR - 2]:
        key = str(period); out[key] = {}
        for fed in FEDS:
            params = {'limit': TOP_N, 'federations[]': fed}
            if period != 'now': params['year'] = period
            j = api('/rating', **params); time.sleep(PAUSE)
            if not j: out[key][fed] = None; continue
            out[key][fed] = {'as_of': (j.get('meta') or {}).get('as_of'),
                             'rows': [{'place': x.get('place'), 'id': x.get('id'), 'nick': x.get('nickname'),
                                       'mmr': r1(x.get('rating')), 'games': x.get('games_count'),
                                       'feds': [f.get('code') for f in x.get('federations') or []]}
                                      for x in j.get('data') or []]}
    return out

# ── 6) запись ────────────────────────────────────────────────────────────────
def patch_participants(players, snap):
    changed = 0
    for f in sorted(glob.glob(os.path.join(BASE, 'data', 'participants_*.json'))):
        raw = io.open(f, encoding='utf-8').read()
        try: d = json.loads(raw)
        except Exception: continue
        for p in d.get('players') or []:
            m = players.get(str(p.get('uid')))
            if not m: continue
            ms = p.get('ms') or {}
            ms.update({'id': m['id'], 'rating': m['mmr'], 'rank': m['rank'], 'games': m['games'], 'wr': m['wr'], 'conf': 'mafgame-id'})
            p['ms'] = ms; p['r_ms_mmr'] = m['mmr']; p['r_ms_rank'] = m['rank']
        d.setdefault('meta', {})['ms_snap'] = snap
        new = json.dumps(d, ensure_ascii=False, indent=1)
        if new.strip() != raw.strip():
            io.open(f, 'w', encoding='utf-8').write(new + '\n'); changed += 1
    return changed

def bump_sw():
    s = io.open(SW, encoding='utf-8').read()
    m = re.search(r"CACHE_VERSION = 'dovod-v(\d+)'", s)
    if not m: return None
    v = int(m.group(1)) + 1
    io.open(SW, 'w', encoding='utf-8').write(s.replace(m.group(0), "CACHE_VERSION = 'dovod-v%d'" % v))
    return v

# ── 7) тир по MMR (линейка markery) ──────────────────────────────────────────
TIERS = 'LSABCDEF'

def mmr_ladder():
    """Пороги MMR по долям тиров markery среди игроков, у которых есть оба рейтинга."""
    # v1.2 (06.11.2026): если есть калибровка data/research/mmr_tiers.json (тир = шанс финала на типичном турнире,
    # data/research/model/mmr_calibrate.py) — берём её пороги; линейка по долям markery — запасной вариант.
    try:
        cal = json.load(io.open(os.path.join(BASE, 'data', 'research', 'mmr_tiers.json'), encoding='utf-8'))
        th = {t: int(v) for t, v in cal['thresholds'].items()}
        per = {tid: {t: int(v) for t, v in cal['variants'][var]['thresholds'].items()} for tid, var in (cal.get('apply') or {}).items() if var in (cal.get('variants') or {})}
        return {'thresholds': th, 'per': per, 'sample': cal.get('sample', {}).get('entries'), 'shares': {}, 'exact': 0, 'within1': 0, 'method': 'final-chance v' + str(cal.get('version'))}
    except Exception:
        pass
    pairs = {}
    for f in glob.glob(os.path.join(BASE, 'data', 'participants_*.json')):
        try: d = json.load(io.open(f, encoding='utf-8'))
        except Exception: continue
        for p in d.get('players') or []:
            if p.get('uid') and (p.get('r_tier') or '') in list(TIERS) and p.get('r_ms_mmr'):
                pairs[str(p['uid'])] = (p['r_tier'], float(p['r_ms_mmr']))
    if len(pairs) < 50: return None
    cnt = {t: sum(1 for x in pairs.values() if x[0] == t) for t in TIERS}
    mm = sorted((m for _, m in pairs.values()), reverse=True)
    th, k = {}, 0
    for t in TIERS[:-1]:
        k += cnt[t]
        th[t] = round((mm[k - 1] + mm[min(k, len(mm) - 1)]) / 2) if 0 < k < len(mm) else (round(mm[0]) + 1 if k == 0 else 0)
    def tier(m):
        for t in TIERS[:-1]:
            if m >= th[t]: return t
        return 'F'
    exact = sum(1 for t, m in pairs.values() if tier(m) == t)
    near = sum(1 for t, m in pairs.values() if abs(TIERS.index(tier(m)) - TIERS.index(t)) <= 1)
    return {'thresholds': th, 'sample': len(pairs), 'shares': cnt, 'exact': exact, 'within1': near}

def mmr_tier(m, th):
    if m is None: return None
    for t in TIERS[:-1]:
        if m >= th[t]: return t
    return 'F'

def apply_mmr_tiers():
    lad = mmr_ladder()
    if not lad: log('тир MMR: мало пар markery+MMR — пропускаю'); return None
    th = lad['thresholds']
    for f in sorted(glob.glob(os.path.join(BASE, 'data', 'participants_*.json'))):
        raw = io.open(f, encoding='utf-8').read()
        try: d = json.loads(raw)
        except Exception: continue
        tid = re.sub(r'\D', '', os.path.basename(f)); thf = (lad.get('per') or {}).get(tid, th)   # v1.3: тестовая шкала для отдельных турниров
        for p in d.get('players') or []:
            p['r_ms_tier'] = mmr_tier(p.get('r_ms_mmr'), thf)
        d.setdefault('meta', {})['ms_ladder'] = thf
        new = json.dumps(d, ensure_ascii=False, indent=1)
        if new.strip() != raw.strip(): io.open(f, 'w', encoding='utf-8').write(new + '\n')
    log('тир MMR: пороги %s · выборка %d · совпало с markery %d, ±1 тир %d' % (th, lad['sample'], lad['exact'], lad['within1']))
    return lad

def main():
    ping = api('/rating', limit=1)
    if not ping: fail('mafiastats API не отвечает — ничего не пишу')
    ids = wanted_ids()
    players, miss = {}, 0
    for i, uid in enumerate(sorted(ids, key=int)):
        m = lookup(uid)
        if m and m['mmr'] is not None: players[uid] = m
        else: miss += 1
        if i % 100 == 0: log('  … %d/%d' % (i, len(ids)))
        time.sleep(PAUSE)
    share = len(players) / max(1, len(ids))
    log('найдено MMR: %d из %d (%.0f%%)' % (len(players), len(ids), share * 100))
    if share < MIN_SHARE: fail('найдено меньше %d%% игроков — похоже, API отдаёт мусор' % (MIN_SHARE * 100))
    snap = datetime.date.today().isoformat()
    model = api('/rating-model')
    out = {'snap': snap, 'source': 'https://mafiastats.com', 'note': 'MMR mafiastats по mafgame-id; ключ players — mafgame user_id',
           'rating_type': 'regular', 'model': (model or {}).get('data'), 'players': players, 'tops': tops()}
    try:
        old = json.load(io.open(OUT, encoding='utf-8'))
    except Exception:
        old = None
    same = old and old.get('players') == json.loads(json.dumps(players)) and old.get('tops') == json.loads(json.dumps(out['tops']))
    if same:
        log('MMR не изменился с прошлого снимка (%s) — ничего не пишу' % old.get('snap')); return
    io.open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    ch = patch_participants(players, snap)
    lad = apply_mmr_tiers()
    if lad:
        out['tier_ladder'] = lad
        io.open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    v = bump_sw()
    log('готово: data/mmr.json (%d игроков), составов обновлено: %d, sw v%s' % (len(players), ch, v))

if __name__ == '__main__':
    if '--tiers-only' in sys.argv:
        lad = apply_mmr_tiers()
        if lad:
            d = json.load(io.open(OUT, encoding='utf-8')); d['tier_ladder'] = lad
            io.open(OUT, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n')
    else:
        main()
