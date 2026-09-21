# -*- coding: utf-8 -*-
"""
refresh_mcl.py · v1.1 · 2026-09-21 · версия для сайта DOVOD
Назначение: обновить датафайл страниц MCL (data/mcl2026.js) по протоколам mafgame.org
и постам канала лиги, без участия человека. Тот же робот работает у партнёров
(ecosciug/mafiacl-kings) — там пути другие, здесь ещё поднимается CACHE_VERSION в sw.js.
Запускается GitHub Actions ежедневно — см. .github/workflows/refresh-mcl.yml.

Оглавление:
  1)  настройки и пути
  2)  сеть: загрузка страниц mafgame (Inertia data-page) и канала Telegram
  3)  реестр серии: все этапы турнира-серии 757
  4)  протоколы этапов: баллы, победители, метрики судейства
  5)  Telegram: фото победителей по хештегу + ссылка на пост + судья из анонса
  6)  сборка зачёта конференций, состава финала, KPI и тикера
  7)  предохранители и запись файла
  8)  сводка прогона

Что робот НЕ трогает (задаётся руками в файле): quota, total, mode, route, semiSlots,
semiDate, semiPrize, semiNote у конференций,
prize, finalISO, contacts, quotas, judges — таблица судейства из отдельного разбора.
"""

import os, re, io, json, html, time, urllib.request, urllib.error, datetime, hashlib

# ── 1) настройки ─────────────────────────────────────────────────────────────
SERIAL_ID   = 757                      # турнир-серия «Mafia Champions league» Europe 2026
YEAR        = 2026
MAFGAME     = os.environ.get('MAFGAME_BASE_URL', 'https://mafgame.org').rstrip('/')
TG_CHANNEL  = os.environ.get('MCL_TG_CHANNEL', 'mafiamcl')
TG_HASHTAG  = os.environ.get('MCL_TG_HASHTAG', '#mclрезультаты2026')
UA          = os.environ.get('REQUEST_USER_AGENT', 'Mozilla/5.0 (compatible; MafiaCLKingsBot/1.0; +https://mafiacl.com)')
PAUSE       = 0.4
MIN_STAGES  = 10                       # предохранитель: меньше — не пишем файл

# .github/scripts/ → корень репозитория на два уровня выше
BASE   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA   = os.path.join(BASE, 'data', 'mcl2026.js')
ASSETS = os.path.join(BASE, 'assets', 'mcl')
SW     = os.path.join(BASE, 'sw.js')

CONF_ORDER = ['CE', 'IL', 'CY']
FLAG = {'Prague':'CZ','Dortmund':'DE','Cologne':'DE','Chemnitz':'DE','Nürnberg':'DE','Nuremberg':'DE',
        'Brussel':'BE','City of Brussels':'BE','Wroclaw':'PL','Ramat Gan':'IL','Haifa':'IL','Limassol':'CY'}
COUNTRY = {'CZ':'Czechia','DE':'Germany','BE':'Belgium','PL':'Poland','IL':'Israel','CY':'Cyprus'}
CITY_FIX = {'Nuremberg':'Nürnberg', 'City of Brussels':'Brussel'}
CURSIGN  = {'EUR':'€', 'USD':'$', 'GBP':'£', 'PLN':'zł', 'CZK':'Kč', 'ILS':'ILS'}

log_lines = []
def log(s):
    print(s, flush=True)
    log_lines.append(s)

# ── 2) сеть ──────────────────────────────────────────────────────────────────
def fetch(url, tries=3):
    for i in range(tries):
        try:
            # ⚠ Accept-Language решает, на каком языке придут названия городов:
            # с 'ru' прилетает «Прага»/«Хемниц», а на страницах лиги города латиницей.
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en'})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))

def inertia(url):
    """props из атрибута data-page страницы mafgame"""
    raw = fetch(url)
    m = re.search(r'data-page="([^"]+)"', raw)
    if not m:
        raise RuntimeError('data-page не найден: ' + url)
    return json.loads(html.unescape(m.group(1)))['props']

# ── 3) реестр серии ──────────────────────────────────────────────────────────
def stage_conf(name):
    n = name.lower()
    if 'israel' in n:  return 'IL'
    if 'cyprus' in n:  return 'CY'
    return 'CE'

def stage_num(name):
    m = re.search(r'/(\d{1,2})\s*$', name.strip())
    return int(m.group(1)) if m else 0

def registry():
    """все этапы серии: идём по листингу года, отбираем parent_tournament_id == SERIAL_ID"""
    stages, page, seen_pages = [], 1, 0
    while True:
        p = inertia('%s/tournaments?s=all&y=%d&page=%d' % (MAFGAME, YEAR, page))
        sr = p.get('search_results') or {}
        rows = sr.get('data') or []
        if not rows:
            break
        for t in rows:
            if t.get('parent_tournament_id') == SERIAL_ID:
                stages.append(t)
        last = sr.get('last_page') or 1
        seen_pages += 1
        if page >= last:
            break
        page += 1
        time.sleep(PAUSE)
    log('листинг: страниц %d, этапов серии %d' % (seen_pages, len(stages)))
    return stages

# ── 4) протоколы ─────────────────────────────────────────────────────────────
def city_of(t):
    c = t.get('city')
    if isinstance(c, dict):
        c = c.get('city')
    c = c or ''
    return CITY_FIX.get(c, c)

def details(tid):
    """взнос, валюта и город со страницы турнира.
    В листинге взноса нет вовсе, а название города приходит локализованным
    («Хемниц» вместо «Chemnitz») — на страницах лиги города пишутся латиницей."""
    try:
        t = inertia('%s/tournaments/%d/view' % (MAFGAME, tid)).get('tournament') or {}
    except Exception:
        return '', ''
    fee = t.get('participation_fee')
    cur = ((t.get('participation_currency') or {}).get('code') or '')
    try:
        fee = float(fee)
    except (TypeError, ValueError):
        fee = 0
    feetx = ('%g %s' % (fee, CURSIGN.get(cur, cur))).strip() if fee > 0 else ''
    return feetx, city_of(t)

def protocol(tid):
    """→ (rows, metrics) или (None, None), если протокола ещё нет"""
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
            rows.append(dict(u=pl.get('user_id'), n=pl.get('nickname'),
                             sc=round(float(sc['total_score']), 3)))
            seats += int(sc.get('games_total') or r.get('games_played') or 0)
            ab    += float(sc.get('additional_bonus_points') or 0)
            pen   += float(sc.get('penalty_points') or 0)
            wins  += int(sc.get('wins') or 0)
    if not rows:
        return None, None
    rows.sort(key=lambda x: -x['sc'])
    games = seats // 10 if seats >= 10 else 0
    # в схеме 10 игроков: 7 красных / 3 чёрных → Σпобед = 30 + 4 × побед города
    town = (wins - 3 * games) / 4.0 if games else None
    metrics = dict(players=len(rows), games=games,
                   town=(int(round(town)) if town is not None else None),
                   gb=(round(ab / seats, 4) if seats else None),
                   pen=round(pen, 2))
    return rows, metrics

# ── 5) Telegram ──────────────────────────────────────────────────────────────
def tg_posts(pages=4):
    """посты канала: [{post, text, photos:[{u,w,h}]}] — свежие страницы через ?before="""
    out, before = [], None
    for _ in range(pages):
        url = 'https://t.me/s/%s' % TG_CHANNEL + (('?before=%d' % before) if before else '')
        try:
            raw = fetch(url, tries=2)
        except Exception as e:
            log('⚠ Telegram недоступен (%s) — фото и судьи не обновляются' % e.__class__.__name__)
            return out
        blocks = re.split(r'(?=<div class="tgme_widget_message[ "])', raw)
        ids = []
        for b in blocks:
            m = re.search(r'data-post="[^/]+/(\d+)"', b)
            if not m:
                continue
            pid = int(m.group(1)); ids.append(pid)
            txt = re.sub(r'<br\s*/?>', '\n', b)
            txt = html.unescape(re.sub(r'<[^>]+>', ' ', txt))
            txt = re.sub(r'[ \t]+', ' ', txt)
            photos = []
            for st in re.findall(r'style="([^"]*background-image[^"]*)"', b):
                # в обычных постах кавычки одинарные, в альбомах — двойные
                mu = re.search(r"url\((['\"]?)(.*?)\1\)", html.unescape(st))
                if mu and 'telesco' in mu.group(2):
                    photos.append(mu.group(2))
            # размеры из ссылки-обёртки альбома (padding-top даёт соотношение)
            ratios = [float(x) for x in re.findall(r'padding-top:\s*([\d.]+)%', b)]
            out.append(dict(post=pid, text=txt, photos=photos, ratios=ratios))
        if not ids:
            break
        before = min(ids)
        time.sleep(PAUSE)
    seen, uniq = set(), []
    for x in out:
        if x['post'] in seen: continue
        seen.add(x['post']); uniq.append(x)
    log('Telegram: постов прочитано %d' % len(uniq))
    return uniq

def download(url, path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
        if len(body) < 4096:
            return False
        io.open(path, 'wb').write(body)
        return True
    except Exception:
        return False

# ── 6) сборка датафайла ──────────────────────────────────────────────────────
def load_data():
    s = io.open(DATA, encoding='utf-8').read()
    m = re.search(r'window\.MCL=(\{.*\});', s, re.S)
    if not m:
        raise RuntimeError('не разобрал ' + DATA)
    return json.loads(m.group(1))

def main():
    D = load_data()
    D_before = json.loads(json.dumps(D))          # снимок «до» для предохранителей
    old_series   = {s['id']: s for s in D.get('series', [])}
    old_upcoming = {u['id']: u for u in D.get('upcoming', [])}
    avatars      = {r['u']: r.get('p', '') for c in D['conf'].values() for r in c['rows'] if r.get('p')}

    stages = registry()
    if len(stages) < MIN_STAGES:
        raise SystemExit('предохранитель: этапов %d < %d — файл не тронут' % (len(stages), MIN_STAGES))

    today = datetime.date.today().isoformat()
    series, upcoming, added, nores = [], [], [], []

    for t in sorted(stages, key=lambda x: x['start_date']):
        tid   = t['id']
        name  = t.get('name') or ''
        conf  = stage_conf(name)
        num   = stage_num(name)
        date  = (t.get('start_date') or '')[:10]
        semi  = 1 if 'semifinal' in name.lower() else 0
        prev  = old_series.get(tid) or old_upcoming.get(tid) or {}
        # У будущих этапов город и взнос всегда спрашиваем у страницы турнира: организатор
        # переносит и переименовывает их на ходу (940 был Nürnberg 19.09, стал Prague 27.09),
        # а в реестре город приходит локализованным («Хемниц»). У сыгранных — из файла.
        future = date > today
        city  = '' if future else (prev.get('city') or '')
        feetx = '' if future else prev.get('fee', '')
        if not city or not feetx:
            f2, c2 = details(tid); time.sleep(PAUSE)
            city  = c2 or city or city_of(t)
            feetx = feetx or f2
        fl    = FLAG.get(city, '') or (prev.get('fl') if not future else '') or ''

        rec = dict(id=tid, c=conf, num=num, city=city, fl=fl, country=COUNTRY.get(fl, ''),
                   date=date, fee=feetx or prev.get('fee', ''), j=prev.get('j', ''),
                   time=prev.get('time', ''), img=prev.get('img', ''), post=prev.get('post'))
        if semi:
            rec['semi'] = 1

        if date > today:
            upcoming.append(rec)
            continue

        # протокол уже разобран в прошлый прогон — он не меняется, второй раз не тянем
        if prev.get('r'):
            rec.update({k: prev[k] for k in ('kind', 'top', 'r', 'players', 'games', 'town', 'gb', 'gbl', 'pen')
                        if k in prev})
            series.append(rec)
            continue

        rows, met = protocol(tid)
        time.sleep(PAUSE)
        if not rows:
            rec.update(kind='ann', nores=1)
            series.append(rec); nores.append('%s %s' % (city, date))
            continue

        rec.update(kind=(prev.get('kind') or 'card'),
                   top=[[r['n'], r['sc']] for r in rows[:3]],
                   players=met['players'], games=met['games'], town=met['town'], gb=met['gb'],
                   gbl=prev.get('gbl'), pen=met['pen'],
                   r=[[r['u'], r['n'], r['sc']] for r in rows])
        added.append('%s %s (%s %.2f)' % (city, date, rows[0]['n'], rows[0]['sc']))
        series.append(rec)

    # 5b) фото и судьи из канала
    posts = tg_posts()
    win_post = {}
    for p in posts:
        if TG_HASHTAG in p['text']:
            m = re.search(r'Series Winner\s+([^\n]{1,40})', p['text'])
            if m:
                win_post.setdefault(m.group(1).strip().rstrip('.').strip(), p)
        m2 = re.search(r'Судья:\s*(?:г-н|г-жа)?\s*([^\n]{1,30})', p['text'])
        if m2:
            p['judge'] = m2.group(1).strip()
    for s in series:
        if not s.get('top'):
            continue
        winner = s['top'][0][0]
        p = win_post.get(winner)
        if not p:
            continue
        s['post'] = p['post']
        import glob
        have = sorted(glob.glob(os.path.join(ASSETS, 'w-%d*.jpg' % s['id'])))
        local = os.path.basename(have[0]) if have else 'w-%d.jpg' % s['id']
        target = os.path.join(ASSETS, local)
        if not have and p['photos']:
            card = None
            for u, ratio in zip(p['photos'], (p['ratios'] + [0] * len(p['photos']))):
                if 55 <= ratio <= 58:      # 16:9 — карточка победителя
                    card = u; break
            card = card or p['photos'][0]
            if download(card, target):
                log('фото серии %s скачано из поста %d' % (s['id'], p['post']))
        if os.path.exists(target):
            s['img'] = 'assets/mcl/' + local

    # 6b) зачёт конференций
    for c in CONF_ORDER:
        k = D['conf'][c]
        agg = {}
        for s in series:
            if s['c'] != c or not s.get('r'):
                continue
            label = '%s %s' % (s['city'], s['date'][8:10] + '.' + s['date'][5:7])
            for uid, nick, sc in s['r']:
                a = agg.setdefault(uid, dict(u=uid, n=nick, d=[]))
                a['n'] = nick
                a['d'].append([label, sc])
        rows = []
        for a in agg.values():
            t = round(sum(x[1] for x in a['d']), 3)
            rows.append(dict(u=a['u'], n=a['n'], a=round(t / len(a['d']), 3), s=len(a['d']), t=t,
                             d=a['d'], p=avatars.get(a['u'], '')))
        norm_sorted = sorted([r for r in rows if r['s'] >= 2], key=lambda r: (-r['a'], r['n'] or ''))
        rest_sorted = sorted([r for r in rows if r['s'] <  2], key=lambda r: (-r['a'], r['n'] or ''))
        if k.get('route') == 'semi':
            # отбор в полуфинал: сначала выполнившие норму, потом добор из сыгравших одну серию
            rows = norm_sorted + rest_sorted
            slots = k.get('semiSlots') or 10
            k['cut'] = rows[slots - 1]['a'] if len(rows) >= slots else None
        else:
            rows.sort(key=lambda r: (-r['a'], -r['s'], r['n'] or ''))
            k['cut'] = norm_sorted[k['quota'] - 1]['a'] if len(norm_sorted) >= k['quota'] else None
        k['rows']    = rows
        k['played']  = sum(1 for s in series if s['c'] == c and s.get('r'))
        k['played2'] = len(norm_sorted)

    # 6c) состав финала, KPI, тикер
    NAMES = {'CE': 'CENTRAL', 'IL': 'ISRAEL', 'CY': 'CYPRUS'}
    squad = []
    for c in CONF_ORDER:
        k = D['conf'][c]
        if k.get('route') == 'semi':
            # места этих конференций разыгрываются в полуфинале, зачёт их не определяет
            for i in range(k['quota']):
                squad.append(dict(c=c, slot='%s·%d' % (NAMES[c], i + 1), n='', a=0, s=0, p='', semi=1))
            continue
        norm = [r for r in k['rows'] if r['s'] >= 2]
        for i in range(k['quota']):
            r = norm[i] if i < len(norm) else None
            squad.append(dict(c=c, slot='%s·%d' % (NAMES[c], i + 1), n=(r['n'] if r else ''),
                              a=(r['a'] if r else 0), s=(r['s'] if r else 0), p=(r['p'] if r else '')))
    D['squad'] = squad

    played  = sum(1 for s in series if s.get('r'))
    total   = sum(D['conf'][c]['total'] for c in CONF_ORDER)
    games   = sum(s.get('games') or 10 for s in series if s.get('r'))
    players = len({r['u'] for c in D['conf'].values() for r in c['rows']})
    D['kpi'] = [['%d/%d' % (played, total), 'серий сыграно'],
                ['%d' % games, 'игр · %d посадок' % (games * 10)],
                ['%d' % players, 'игрока в контуре'],
                [D.get('prize', {}).get('total', ''), 'призовой фонд финала']]
    D['ticker'] = ['%s — %s %.2f' % (s['city'].upper(), s['top'][0][0], s['top'][0][1])
                   for s in series if s.get('top')]
    D['series']   = series
    D['upcoming'] = upcoming
    D['snap']     = datetime.date.today().strftime('%d.%m.%Y')

    # ── 7) предохранители и запись ───────────────────────────────────────────
    was_played  = sum(1 for s in D_before.get('series', []) if s.get('r') or s.get('top'))
    was_players = len({r['u'] for c in D_before.get('conf', {}).values() for r in c.get('rows', [])})
    if played < was_played:
        raise SystemExit('предохранитель: серий с протоколом стало меньше (%d < %d) — файл не тронут'
                         % (played, was_played))
    if was_players and players < was_players * 0.8:
        raise SystemExit('предохранитель: игроков стало %d вместо %d — файл не тронут' % (players, was_players))


    body = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    head = ('/* MafgameStat · data/mcl2026.js · снимок %s · собран роботом refresh_mcl.py.\n'
            '   Руками не править: следующий прогон перезапишет. Ручные поля (квоты, объём серий,\n'
            '   призовой фонд, контакты, таблица судейства) правятся в этом же файле и роботом не трогаются. */\n'
            % D['snap'])
    new = head + 'window.MCL=' + body + ';\n'
    old = io.open(DATA, encoding='utf-8').read()
    changed = re.sub(r'^/\*.*?\*/\n', '', old, flags=re.S) != re.sub(r'^/\*.*?\*/\n', '', new, flags=re.S)
    if changed:
        io.open(DATA, 'w', encoding='utf-8').write(new)
        # версия у ссылки на датафайл: без неё браузер отдаёт читателю вчерашние цифры
        stamp = datetime.date.today().strftime('%Y%m%d')
        for page in ('mcl2026.html', 'mcl-standings.html', 'mcl-series.html', 'mcl-lab.html'):
            fp = os.path.join(BASE, page)
            if not os.path.exists(fp):
                continue
            src = io.open(fp, encoding='utf-8').read()
            upd = re.sub(r'<script src="data/mcl2026\.js(\?v=\d+)?"></script>',
                         '<script src="data/mcl2026.js?v=%s"></script>' % stamp, src)
            if upd != src:
                io.open(fp, 'w', encoding='utf-8').write(upd)
        # сервис-воркер держит датафайл в кэше — без нового номера версии
        # читатели увидят старые цифры до второго открытия страницы
        sw = io.open(SW, encoding='utf-8').read()
        mm = re.search(r"const CACHE_VERSION = 'dovod-v(\d+)';", sw)
        if mm:
            io.open(SW, 'w', encoding='utf-8').write(
                sw.replace(mm.group(0), "const CACHE_VERSION = 'dovod-v%d';" % (int(mm.group(1)) + 1)))
            log('CACHE_VERSION → dovod-v%d' % (int(mm.group(1)) + 1))
        else:
            log('⚠ CACHE_VERSION в sw.js не найден — кэш не тронут')

    # ── 8) сводка ────────────────────────────────────────────────────────────
    log('серий с протоколом: %d из %d · игроков: %d · снимок %s' % (played, total, players, D['snap']))
    for c in CONF_ORDER:
        k = D['conf'][c]
        log('  %s: квота %s, сыграно %s/%s, порог %s' % (c, k['quota'], k['played'], k['total'], k['cut']))
    if added: log('новые протоколы: ' + '; '.join(added))
    if nores: log('без протокола: ' + '; '.join(nores))
    log('состав финала: ' + ' | '.join('%s %s' % (x['slot'], x['n'] or '—') for x in squad))
    log('файл ' + ('обновлён' if changed else 'без изменений'))

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with io.open(summary, 'a', encoding='utf-8') as f:
            f.write('### MCL · обновление данных\n\n' + '\n'.join('- ' + x for x in log_lines) + '\n')

if __name__ == '__main__':
    main()
