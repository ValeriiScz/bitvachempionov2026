#!/usr/bin/env python3
"""
refresh_mafgame · v1.4 · 2026-11-13 (составы на страницах набора participants_{id}.json обновляются каждый прогон: новые, выписавшиеся, заявки → подтверждения; раньше это были снимки на день добавления турнира) · v1.3.1 · 2026-11-10 (ручной перезапуск: часовой cron GitHub фактически срабатывает раз в ~8 ч, заявка Gangster на Prague Cup не попала) · v1.3 · 2026-10-19 (отмена/перенос пересчитываются каждый прогон по названию: «[ОТМЕНЁН]», «Отмена», «ОТМЕНА», «[ПЕРЕНОС]», «Перенос на …»; префикс срезается) · v1.2.1 · 2026-10-19 (ручной перезапуск — ночной cron задержан GitHub) · v1.2 · 2026-10-13 (played пересчитывается каждый прогон: start < TODAY и не отменён) · v1.1 · 2026-09-06
Назначение: каждую ночь обновить данные сайта DOVOD из mafgame.org без участия человека.
Запускается GitHub Actions (.github/workflows/refresh-data.yml), работает на серверах GitHub —
ни мак Валерия, ни Claude для этого не нужны.

Оглавление
  1  настройки и предохранители
  2  чтение mafgame (листинг + составы)
  3  патч датасета в calendar.html
  4  пересборка data/season.js
  5  даты в data/meta.js и версия кэша в sw.js
  6  сводка изменений для отчёта Actions
  7  составы страниц набора data/participants_{id}.json (v1.4)

Что делает: тянет реестр турниров года, сверяет с датасетом, вшитым в calendar.html,
обновляет даты/города/звёзды/призовые, добавляет новые турниры, убирает снятые,
подтягивает свежие заявки по будущим рейтинговым турнирам, пересобирает сводку сезона,
поднимает CACHE_VERSION. Если изменений нет — ничего не пишет.

Предохранители (при срабатывании выходит с ошибкой и НЕ коммитит):
  - в листинге меньше MIN_TOURNAMENTS турниров (значит платформа отдала мусор);
  - разом исчезает больше MAX_DISAPPEARED турниров;
  - хоть одна страница листинга не распарсилась.
v1.1: исправлен UnboundLocalError в сводке (block делал `lines +=`, что делало `lines`
локальной переменной закрытия). Скрипт падал в любой прогон, где были новые/снятые
турниры или переносы дат — то есть всегда, кроме ночей без изменений в календаре.
"""
import datetime, html, io, json, os, re, sys, time
import urllib.request, urllib.error

# ── 1 · настройки и предохранители ────────────────────────────────────────────
YEAR              = datetime.date.today().year
TODAY             = datetime.date.today().isoformat()
MIN_TOURNAMENTS   = 300      # меньше — считаем выгрузку сломанной
MAX_DISAPPEARED   = 15       # больше — на прод не пускаем, нужен человек
MAX_PARTICIPANTS  = 90       # сколько составов тянуть за один прогон (будущих турниров ~72)
HOSTS             = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame']  # второй — наш прокси, запас
PAUSE             = 0.4      # сек между запросами, чтобы не долбить платформу
CAL, SEASON, META, SW = 'calendar.html', 'data/season.js', 'data/meta.js', 'sw.js'

def log(msg):
    print(msg, flush=True)

def fail(msg):
    log('СТОП: ' + msg)
    sys.exit(1)

# ── 2 · чтение mafgame ────────────────────────────────────────────────────────
def fetch_page(path):
    """Возвращает props страницы Inertia. Пробует основной хост, потом прокси."""
    last = None
    for host in HOSTS:
        url = host + path
        for attempt in (1, 2, 3):
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'dovod-mafia.com data refresh (github actions)',
                    'Accept': 'text/html'})
                with urllib.request.urlopen(req, timeout=45) as r:
                    body = r.read().decode('utf-8', 'replace')
                m = re.search(r'data-page="([^"]+)"', body)
                if not m:
                    last = 'нет data-page в ответе ' + url
                    break
                return json.loads(html.unescape(m.group(1)))['props']
            except Exception as e:
                last = '%s: %s' % (url, e)
                time.sleep(1.5 * attempt)
    raise RuntimeError(last or 'не удалось получить ' + path)

def fetch_listing():
    rows, page, last_page = {}, 1, None
    while True:
        p = fetch_page('/tournaments?s=all&y=%d&page=%d' % (YEAR, page))
        sr = p.get('search_results') or {}
        data = sr.get('data') or []
        if not data and page == 1:
            fail('листинг пуст')
        for t in data:
            rows[int(t['id'])] = t
        last_page = sr.get('last_page') or 1
        log('  страница %d/%s — турниров %d' % (page, last_page, len(data)))
        if page >= last_page:
            break
        page += 1
        time.sleep(PAUSE)
    return rows

RAW = {}   # tid → props страницы /participants (v1.4: нужны составам страниц набора)

def fetch_regs(tid):
    p = fetch_page('/tournaments/%d/participants' % tid)
    RAW[tid] = p
    out, seen = [], set()
    def add(lst, flag, nested):
        for x in (lst or []):
            if not isinstance(x, dict):
                continue
            uid = x.get('user_id')
            nick = x.get('nickname') or ((x.get('user') or {}).get('nickname') if nested else None)
            if not uid or uid in seen:
                continue
            seen.add(uid)
            out.append([uid, nick or '', flag])
    add(p.get('players'), 1, False)
    add(p.get('applications'), 0, True)
    add(p.get('no_team_applications'), 0, True)
    return out

# ── 3 · патч датасета ─────────────────────────────────────────────────────────
def num(v, cast):
    if v in (None, ''):
        return None
    try:
        return cast(v)
    except Exception:
        return None

def kind_of(n):
    if n.get('teams'):
        return 'teams'
    if n.get('serial'):
        return 'serial' if n.get('parent_tournament_id') else 'serial_final'
    return 'regular'

def load_dataset():
    s = io.open(CAL, encoding='utf-8').read()
    i = s.find('const D=')
    j = s.find('};', i)
    if i < 0 or j < 0:
        fail('в calendar.html не найден блок const D={...}')
    return s, i, j, json.loads(s[i + 8:j + 1])

# v1.3 (19.10.2026): статус «отменён / перенос» — из названия на mafgame, КАЖДЫЙ прогон и для уже известных турниров.
# Раньше флаги ставились только при добавлении нового турнира и только по «[ОТМЕНЁН]»: #767 переименовали в
# «Отмена 🏆Командный Чемпионат Польши 2026🏆» — у нас он висел живым будущим турниром и давал 26 баллов в гонку.
CANCEL_RE = re.compile(r'^\s*(\[\s*(ОТМЕН[ЁЕ]Н|ОТМЕНА)\s*\]|(ОТМЕН[ЁЕ]Н|ОТМЕНА)\b)\s*[:\-–—·]?\s*', re.I)
MOVED_RE  = re.compile(r'^\s*(\[\s*ПЕРЕНОС\s*\]|ПЕРЕНОС\b)\s*[:\-–—·]?\s*', re.I)
def name_status(raw):
    """→ (cancelled, moved, чистое имя). Префикс «[ОТМЕНЁН]», «Отмена», «ОТМЕНА» (в любом регистре) — отмена;
    «[ПЕРЕНОС]» / «Перенос» в начале или «Перенос на …» в тексте — перенос. Префиксы из имени срезаются."""
    raw = (raw or '').strip()
    cancelled = bool(CANCEL_RE.match(raw))
    name = CANCEL_RE.sub('', raw, count=1) if cancelled else raw
    moved = bool(MOVED_RE.match(name)) or bool(re.search(r'перенос\s+на\b', name, re.I))
    name = MOVED_RE.sub('', name, count=1).strip()
    return cancelled, moved, name

def patch(D, new, fresh):
    old = {t['id']: t for t in D['tournaments']}
    rep = {'moved': [], 'added': [], 'removed': [], 'status': [], 'fields': 0, 'regs': 0}
    out = []
    for tid, n in new.items():
        nd = n['start_date'][:10]
        if tid in old:
            t = dict(old[tid])
            if t.get('start') != nd:
                rep['moved'].append('%s: %s → %s (%s)' % (t.get('city'), t.get('start'), nd, t.get('name', '')[:34]))
            t['start'] = nd
            pairs = [('city', 'city', str), ('country', 'country', str), ('name', 'name', str),
                     ('no_of_stars', 'stars', int), ('expected_participants', 'exp', int),
                     ('total_prize', 'prize', float), ('prize_currency', 'prizeCur', str)]
            for src, dst, cast in pairs:
                v = n.get(src)
                v = (num(v, cast) if cast is not str else (v or None))
                if src == 'no_of_stars':
                    v = v or 0
                if v is not None and t.get(dst) != v:
                    t[dst] = v
                    rep['fields'] += 1
            t['kind'] = kind_of(n)
            t['serialKey'] = n.get('parent_tournament_id')
            c, mv, _ = name_status(n.get('name'))
            if c != bool(t.get('cancelled')) or mv != bool(t.get('moved')):
                rep['status'].append('%s %s: %s' % (t.get('start'), (n.get('name') or '')[:40], 'отменён' if c else ('перенос' if mv else 'снова в силе')))
            t['cancelled'], t['moved'] = c, mv
            # «сыгран» пересчитываем каждый прогон (раньше ставился только при добавлении и навсегда оставался false)
            t['played'] = nd < TODAY and not t.get('cancelled')
        else:
            par = n.get('parent_tournament_id')
            sn = (old.get(par) or {}).get('serialName') \
                 or (((new.get(par) or {}).get('name') or '').split('·')[0].strip()[:14] or None)
            t = {'id': tid, 'name': n['name'], 'stars': n.get('no_of_stars') or 0, 'kind': kind_of(n),
                 'serialKey': par, 'serialName': sn, 'start': nd, 'days': None,
                 'city': n.get('city'), 'country': n.get('country'), 'online': n.get('online') or 0,
                 'exp': num(n.get('expected_participants'), int), 'fee': None, 'feeCur': None,
                 'prize': num(n.get('total_prize'), float), 'prizeCur': n.get('prize_currency') or 'EUR',
                 'club': None, 'regOpen': 1 if nd >= TODAY else 0, 'pts': 0, 'plab': 'без баллов',
                 'played': nd < TODAY and not name_status(n['name'])[0], 'cancelled': name_status(n['name'])[0],
                 'moved': name_status(n['name'])[1], 'regs': []}
            rep['added'].append('%s %s %s★ — %s' % (nd, t['city'], t['stars'], n['name'][:40]))
        if tid in fresh:
            if (t.get('regs') or []) != fresh[tid]:
                rep['regs'] += 1
            t['regs'] = fresh[tid]
        t['name'] = name_status(t['name'])[2]
        out.append(t)
    for tid, t in old.items():
        if tid not in new:
            rep['removed'].append('%s %s — %s' % (t.get('start'), t.get('city'), (t.get('name') or '')[:40]))
    out.sort(key=lambda t: (t['start'], t['id']))
    D['tournaments'] = out
    D['snapshot'] = TODAY
    return rep

# ── 4 · сводка сезона ─────────────────────────────────────────────────────────
def build_season(D):
    KIND = {'regular': 0, 'serial': 1, 'serial_final': 2, 'teams': 3}
    T = D['tournaments']
    rows = sorted([[t['start'], KIND[t['kind']], t.get('stars') or 0, t.get('country') or '']
                   for t in T if not t.get('cancelled')])
    players = {r[0] for t in T for r in (t.get('regs') or [])}
    S = {'snap': D['snapshot'], 'players': len(players),
         'cities': len({t['city'] for t in T if t.get('city')}),
         'serials': len({t['serialKey'] for t in T if t.get('serialKey')}),
         'rows': rows}
    io.open(SEASON, 'w', encoding='utf-8').write(
        '/* season.js — сводка сезона: снимок %s, %d турниров.\n'
        '   Формат rows: [дата, тип (0 турнир, 1 этап серии, 2 финал серии, 3 командный), звёзды, страна].\n'
        '   Генератор: .github/scripts/refresh_mafgame.py. Руками не править. */\n'
        'window.SEASON=%s;\n' % (D['snapshot'], len(rows),
                                 json.dumps(S, ensure_ascii=False, separators=(',', ':'))))
    return S

# ── 5 · даты и версия кэша ────────────────────────────────────────────────────
def bump_meta_and_sw(bump_sw=True):
    d = datetime.date.today().strftime('%d.%m.%Y')
    m = io.open(META, encoding='utf-8').read()
    m2 = re.sub(r"calendarSnapshot:\s*'[^']*'", "calendarSnapshot: '%s'" % d, m)
    if m2 != m:
        io.open(META, 'w', encoding='utf-8').write(m2)
    s = io.open(SW, encoding='utf-8').read()
    mm = re.search(r"const CACHE_VERSION = 'dovod-v(\d+)';", s)
    if not mm:
        fail('в sw.js не найден CACHE_VERSION')
    cur = int(mm.group(1))
    if not bump_sw:
        return cur
    io.open(SW, 'w', encoding='utf-8').write(
        s.replace(mm.group(0), "const CACHE_VERSION = 'dovod-v%d';" % (cur + 1)))
    return cur + 1

# ── 7 · составы страниц набора (v1.4) ─────────────────────────────────────────
def _mtier(v, th):
    if v is None:
        return None
    for k in ['L', 'S', 'A', 'B', 'C', 'D', 'E']:
        if v >= th[k]:
            return k
    return 'F'

CTRY = {'Czech Republic': ('CZ', 'Чехия', '🇨🇿'), 'Poland': ('PL', 'Польша', '🇵🇱'), 'Germany': ('DE', 'Германия', '🇩🇪'),
        'Ukraine': ('UA', 'Украина', '🇺🇦'), 'Netherlands': ('NL', 'Нидерланды', '🇳🇱'), 'Belgium': ('BE', 'Бельгия', '🇧🇪'),
        'Republic of Moldova': ('MD', 'Молдова', '🇲🇩'), 'Moldova': ('MD', 'Молдова', '🇲🇩'), 'Israel': ('IL', 'Израиль', '🇮🇱'),
        'Portugal': ('PT', 'Португалия', '🇵🇹'), 'Switzerland': ('CH', 'Швейцария', '🇨🇭'), 'Spain': ('ES', 'Испания', '🇪🇸'),
        'Cyprus': ('CY', 'Кипр', '🇨🇾'), 'Austria': ('AT', 'Австрия', '🇦🇹'), 'Serbia': ('RS', 'Сербия', '🇷🇸'),
        'Turkey': ('TR', 'Турция', '🇹🇷'), 'Romania': ('RO', 'Румыния', '🇷🇴'), 'Georgia': ('GE', 'Грузия', '🇬🇪'),
        'Lithuania': ('LT', 'Литва', '🇱🇹'), 'Latvia': ('LV', 'Латвия', '🇱🇻'), 'Estonia': ('EE', 'Эстония', '🇪🇪'),
        'Slovakia': ('SK', 'Словакия', '🇸🇰'), 'Hungary': ('HU', 'Венгрия', '🇭🇺')}
CTRY.update({v[1]: v for v in list(CTRY.values())})

def refresh_participants():
    """Каждый незавершённый турнир с файлом data/participants_{id}.json сверяется с mafgame:
    новые игроки добавляются (MMR из data/mmr.json, ELO из реестра — до прогонов роботов),
    выписавшиеся убираются, статус заявка/подтверждён обновляется. Архив (ms_frozen) не трогаем.
    Пустой ответ платформы при непустом составе — не пишем (предохранитель)."""
    import csv, glob
    try:
        MMR = json.load(io.open('data/mmr.json', encoding='utf-8')).get('players', {})
        th = json.load(io.open('data/research/mmr_tiers.json', encoding='utf-8'))['thresholds']
    except Exception as e:
        log('  составы: нет mmr.json/mmr_tiers.json (%s) — пропуск' % e)
        return []
    ELO, REG = {}, {}
    try:
        for r in csv.DictReader(io.open('data/registry/elo_history.csv', encoding='utf-8')):
            if r.get('elo_all'):
                u = r['mafgame_uid']
                if u not in ELO or r['snapshot'] >= ELO[u]['snapshot']:
                    ELO[u] = r
        for r in csv.DictReader(io.open('data/registry/players.csv', encoding='utf-8')):
            REG[r['mafgame_uid']] = r
    except Exception:
        pass
    changes = []
    for f in sorted(glob.glob('data/participants_*.json')):
        try:
            tid = int(re.search(r'_(\d+)\.json$', f).group(1))
            d = json.load(io.open(f, encoding='utf-8'))
        except Exception:
            continue
        m = d.get('meta') or {}
        if m.get('ms_frozen') or not m.get('start') or m['start'] < TODAY:
            continue
        p = RAW.get(tid)
        if p is None:
            try:
                p = fetch_page('/tournaments/%d/participants' % tid)
                time.sleep(PAUSE)
            except Exception as e:
                log('  состав %d: пропуск (%s)' % (tid, e))
                continue
        rows, seen = [], set()
        for x in (p.get('players') or []):
            if isinstance(x, dict) and x.get('user_id') and x['user_id'] not in seen:
                seen.add(x['user_id'])
                rows.append((x['user_id'], x.get('nickname') or (x.get('user') or {}).get('nickname') or '',
                             x.get('user') or {}, 'confirmed', x.get('player_number')))
        for a in (p.get('applications') or []) + (p.get('no_team_applications') or []):
            if not isinstance(a, dict) or not a.get('user_id') or a['user_id'] in seen:
                continue
            if a.get('status') not in (None, 'applied', 'confirmed'):
                continue   # отклонённые/отозванные заявки не показываем
            seen.add(a['user_id'])
            us = a.get('user') or {}
            rows.append((a['user_id'], us.get('nickname') or '', us,
                         'confirmed' if a.get('status') == 'confirmed' else 'applied', None))
        old = {pl['uid']: pl for pl in d.get('players', [])}
        if not rows and old:
            log('  состав %d: платформа отдала пустой список при %d в файле — не трогаю' % (tid, len(old)))
            continue
        out, added, upd = [], [], []
        for uid, nick, us, st, pn in rows:
            pl = old.get(uid)
            if pl:
                if pl.get('status') != st:
                    upd.append('%s → %s' % (pl.get('nick'), 'подтверждён' if st == 'confirmed' else 'заявка'))
                    pl['status'] = st
                if pn is not None:
                    pl['player_number'] = pn
                if us.get('avatar') and not pl.get('av'):
                    pl['av'] = us['avatar']
                out.append(pl)
                continue
            mm = MMR.get(str(uid)) or {}
            e = ELO.get(str(uid))
            rg = REG.get(str(uid)) or {}
            cl = us.get('club') or {}
            out.append({'nick': nick, 'uid': uid, 'real': us.get('display_name'), 'av': us.get('avatar'),
                        'status': st, 'club': cl.get('name') or rg.get('club') or None,
                        'cc': (CTRY.get(rg.get('country')) or (None,))[0],
                        'country': (CTRY.get(rg.get('country')) or (None, rg.get('country') or None))[1],
                        'flag': (CTRY.get(rg.get('country')) or (None, None, None))[2],
                        'markery_id': int(e['markery_id']) if e and e.get('markery_id') else None,
                        'r_elo_cur': round(float(e['elo_all'])) if e else None,
                        'r_tier': e.get('tier') if e else None, 'r_elo_ly': None, 'mg_rank': None, 'm_rank': None,
                        'player_number': pn, 'mk_match': 'id' if e else None,
                        'elo_snap': e['snapshot'] if e else None,
                        'series': None, 'series_place': None, 'series_score': None, 'ms': None,
                        'r_ms_mmr': mm.get('mmr'), 'r_ms_rank': mm.get('rank'), 'r_ms_tier': _mtier(mm.get('mmr'), th),
                        'added': TODAY})
            added.append(nick)
        gone = [pl.get('nick') for u, pl in old.items() if u not in seen]
        if not (added or gone or upd):
            continue
        conf = sum(1 for o in out if o['status'] == 'confirmed')
        m['players_confirmed'] = conf
        m['roster_snap'] = TODAY
        d['meta'], d['players'] = m, out
        io.open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
        line = '%s (%d): подтв. %d, всего %d' % (m.get('name', tid), tid, conf, len(out))
        if added: line += ' · +' + ', '.join(added)
        if gone:  line += ' · выписались: ' + ', '.join(gone)
        if upd:   line += ' · ' + ', '.join(upd)
        changes.append(line)
    return changes

# ── 6 · прогон ────────────────────────────────────────────────────────────────
def main():
    log('Реестр турниров %d с mafgame:' % YEAR)
    new = fetch_listing()
    log('всего получено: %d' % len(new))
    if len(new) < MIN_TOURNAMENTS:
        fail('получено %d турниров, ожидалось не меньше %d — похоже на сбой платформы' % (len(new), MIN_TOURNAMENTS))

    s, i, j, D = load_dataset()
    old_ids = {t['id'] for t in D['tournaments']}
    gone = old_ids - set(new)
    if len(gone) > MAX_DISAPPEARED:
        fail('из листинга исчезло %d турниров (порог %d) — на прод не выкатываю, нужен человек' % (len(gone), MAX_DISAPPEARED))

    # свежие заявки: ВСЕ будущие турниры, начиная с ближайших.
    # 0★-миникапы тоже спрашиваем — они пятая часть календаря, и их лобби людям видно.
    fut = sorted([t for t in new.values() if t['start_date'][:10] >= TODAY],
                 key=lambda t: t['start_date'])[:MAX_PARTICIPANTS]
    fresh = {}
    log('Составы (%d турниров):' % len(fut))
    for t in fut:
        tid = int(t['id'])
        try:
            fresh[tid] = fetch_regs(tid)
        except Exception as e:
            log('  пропуск %d: %s' % (tid, e))
        time.sleep(PAUSE)
    log('составов получено: %d' % len(fresh))

    rep = patch(D, new, fresh)
    rosters = refresh_participants()
    io.open(CAL, 'w', encoding='utf-8').write(s[:i + 8] + json.dumps(D, ensure_ascii=False) + s[j + 1:])
    S = build_season(D)
    # оболочку сбрасываем только когда поменялся сам календарь: новые/снятые турниры,
    # переносы дат, правки полей. Ежедневное движение заявок доедет само
    # (service worker отдаёт кэш и тут же обновляет его в фоне) — иначе приложение
    # каждую ночь перекачивало бы страницу целиком без причины.
    material = bool(rep['added'] or rep['moved'] or rep['removed'] or rep['status'] or rep['fields'])
    ver = bump_meta_and_sw(bump_sw=material)

    lines = ['## Обновление данных mafgame · %s' % TODAY, '',
             'Турниров в реестре: **%d** · строк в сводке: %d · игроков: %d · версия кэша: dovod-v%d%s' %
             (len(new), len(S['rows']), S['players'], ver, '' if material else ' (не менялась: правились только заявки)'), '']
    def block(title, items):
        if not items:
            return
        lines.append('**%s (%d):**' % (title, len(items)))
        lines.extend('- ' + x for x in items[:25])
        if len(items) > 25:
            lines.append('- …и ещё %d' % (len(items) - 25))
        lines.append('')
    block('Новые турниры', rep['added'])
    block('Переносы дат', rep['moved'])
    block('Снято с календаря', rep['removed'])
    block('Статус отмена/перенос', rep['status'])
    block('Составы страниц набора', rosters)
    lines.append('Обновлено полей: %d · составов: %d' % (rep['fields'], rep['regs']))
    summary = '\n'.join(lines)
    log('')
    log(summary)
    path = os.environ.get('GITHUB_STEP_SUMMARY')
    if path:
        io.open(path, 'a', encoding='utf-8').write(summary + '\n')

if __name__ == '__main__':
    main()
