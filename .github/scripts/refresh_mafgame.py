#!/usr/bin/env python3
"""
refresh_mafgame · v1.0 · 2026-09-02
Назначение: раз в неделю обновить данные сайта DOVOD из mafgame.org без участия человека.
Запускается GitHub Actions (.github/workflows/refresh-data.yml), работает на серверах GitHub —
ни мак Валерия, ни Claude для этого не нужны.

Оглавление
  1  настройки и предохранители
  2  чтение mafgame (листинг + составы)
  3  патч датасета в calendar.html
  4  пересборка data/season.js
  5  даты в data/meta.js и версия кэша в sw.js
  6  сводка изменений для отчёта Actions

Что делает: тянет реестр турниров года, сверяет с датасетом, вшитым в calendar.html,
обновляет даты/города/звёзды/призовые, добавляет новые турниры, убирает снятые,
подтягивает свежие заявки по будущим рейтинговым турнирам, пересобирает сводку сезона,
поднимает CACHE_VERSION. Если изменений нет — ничего не пишет.

Предохранители (при срабатывании выходит с ошибкой и НЕ коммитит):
  - в листинге меньше MIN_TOURNAMENTS турниров (значит платформа отдала мусор);
  - разом исчезает больше MAX_DISAPPEARED турниров;
  - хоть одна страница листинга не распарсилась.
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

def fetch_regs(tid):
    p = fetch_page('/tournaments/%d/participants' % tid)
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

def patch(D, new, fresh):
    old = {t['id']: t for t in D['tournaments']}
    rep = {'moved': [], 'added': [], 'removed': [], 'fields': 0, 'regs': 0}
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
                 'played': nd < TODAY, 'cancelled': '[ОТМЕНЁН]' in n['name'],
                 'moved': '[ПЕРЕНОС]' in n['name'], 'regs': []}
            rep['added'].append('%s %s %s★ — %s' % (nd, t['city'], t['stars'], n['name'][:40]))
        if tid in fresh:
            if (t.get('regs') or []) != fresh[tid]:
                rep['regs'] += 1
            t['regs'] = fresh[tid]
        t['name'] = re.sub(r'^\s*\[(ОТМЕНЁН|ПЕРЕНОС)\]\s*', '', t['name']).strip()
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
    io.open(CAL, 'w', encoding='utf-8').write(s[:i + 8] + json.dumps(D, ensure_ascii=False) + s[j + 1:])
    S = build_season(D)
    # оболочку сбрасываем только когда поменялся сам календарь: новые/снятые турниры,
    # переносы дат, правки полей. Ежедневное движение заявок доедет само
    # (service worker отдаёт кэш и тут же обновляет его в фоне) — иначе приложение
    # каждую ночь перекачивало бы страницу целиком без причины.
    material = bool(rep['added'] or rep['moved'] or rep['removed'] or rep['fields'])
    ver = bump_meta_and_sw(bump_sw=material)

    lines = ['## Обновление данных mafgame · %s' % TODAY, '',
             'Турниров в реестре: **%d** · строк в сводке: %d · игроков: %d · версия кэша: dovod-v%d%s' %
             (len(new), len(S['rows']), S['players'], ver, '' if material else ' (не менялась: правились только заявки)'), '']
    def block(title, items):
        if not items:
            return
        lines.append('**%s (%d):**' % (title, len(items)))
        lines += ['- ' + x for x in items[:25]]
        if len(items) > 25:
            lines.append('- …и ещё %d' % (len(items) - 25))
        lines.append('')
    block('Новые турниры', rep['added'])
    block('Переносы дат', rep['moved'])
    block('Снято с календаря', rep['removed'])
    lines.append('Обновлено полей: %d · составов: %d' % (rep['fields'], rep['regs']))
    summary = '\n'.join(lines)
    log('')
    log(summary)
    path = os.environ.get('GITHUB_STEP_SUMMARY')
    if path:
        io.open(path, 'a', encoding='utf-8').write(summary + '\n')

if __name__ == '__main__':
    main()
