#!/usr/bin/env python3
"""
wc710_audit · v1.0 · 2026-09-12
Назначение: во время ЧМ-2026 (mafgame t710) каждые 5 минут снимать протоколы всех столов
и вести журнал изменений — кому и когда поменяли балл, роль, доп или штраф (апелляции,
правки судей, замены игроков). Журнал показывается внизу судейского раздела сайта.

Оглавление
  1  настройки и окно работы
  2  чтение game_results с mafgame
  3  нормализация мест (стадия-игра-стол-место)
  4  сравнение со снимком и события журнала
  5  запись data/wc710_live.json и data/wc710_audit.json

Почему снимок, а не «живой» расчёт: mafgame отдаёт текущее состояние, но не историю.
Единственный способ увидеть «было 0.5 — стало 0.3» — самим складывать снимки и сравнивать.

Предохранители: если мест в выгрузке меньше MIN_SEATS или страница не распарсилась —
выходим с ошибкой и НИЧЕГО не пишем (иначе пустая выгрузка затрёт журнал).
"""
import datetime, html, io, json, os, re, sys, time
import urllib.request, urllib.error

T          = '710'
FROM_DATE  = datetime.date(2026, 9, 12)   # окно работы: дни турнира + сутки на апелляции
TO_DATE    = datetime.date(2026, 9, 14)
MIN_SEATS  = 400
MAX_EVENTS = 3000
HOSTS      = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame']
SNAP, AUDIT = 'data/wc710_live.json', 'data/wc710_audit.json'
UA = 'DOVOD-bot/1.0 (+https://dovod-mafia.com; аудит протоколов ЧМ-2026)'

# следим за этими полями; подпись — как показываем человеку
FIELDS = [('name','игрок'),('role','роль'),('gp','баллы за победу'),('gb','доп'),
          ('bmb','лучший ход'),('pen','штраф'),('ci','Ci'),('kf','первый убитый')]
ROLE_RU = {'red':'мирный','sheriff':'шериф','black':'мафия','don':'дон',
           'citizen':'мирный','mafia':'мафия'}

def log(m): print(m, flush=True)

def fetch(path):
    last = None
    for host in HOSTS:
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(host + path, headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=45) as r:
                    return r.read().decode('utf-8', 'replace')
            except Exception as e:
                last = e
                time.sleep(2)
    raise SystemExit('не удалось прочитать %s: %s' % (path, last))

def props(page_html):
    m = re.search(r'data-page="([^"]+)"', page_html)
    if not m:
        raise SystemExit('нет data-page — платформа отдала не ту страницу')
    return json.loads(html.unescape(m.group(1)))['props']

def norm(seats):
    """{'стадия-игра-стол-место': {поля}} — только занятые места."""
    out = {}
    for k, s in (seats or {}).items():
        p = k.split('-')
        if len(p) != 4 or not s or not s.get('original_nickname'):
            continue
        out[k] = {
            'name': s.get('original_nickname'),
            'role': s.get('role'),
            'gp':  round(float(s.get('game_points') or 0), 4),
            'gb':  round(float(s.get('game_bonus') or 0), 4),
            'bmb': round(float(s.get('best_move_bonus') or 0), 4),
            'pen': round(float(s.get('penalty') or 0), 4),
            'ci':  round(float(s.get('Ci') or 0), 4),
            'kf':  int(s.get('killed_first') or 0),
        }
    return out

def human(field, v):
    if field == 'role':  return ROLE_RU.get(str(v).lower(), v if v else '—')
    if field == 'kf':    return 'да' if v else 'нет'
    if v is None:        return '—'
    if isinstance(v, float):
        return ('%g' % round(v, 4))
    return str(v)

def main():
    today = datetime.date.today()
    if not (FROM_DATE <= today <= TO_DATE):
        log('вне окна турнира (%s) — ничего не делаем' % today)
        return

    p = props(fetch('/tournaments/%s/game_results' % T))
    seats = norm((p.get('games') or {}).get('seats'))
    if len(seats) < MIN_SEATS:
        raise SystemExit('в выгрузке всего %d мест — похоже на сбой, снимок не трогаем' % len(seats))

    old = {}
    if os.path.exists(SNAP):
        try: old = json.load(io.open(SNAP, encoding='utf-8')).get('seats', {})
        except Exception: old = {}

    audit = {'updated': None, 'events': []}
    if os.path.exists(AUDIT):
        try: audit = json.load(io.open(AUDIT, encoding='utf-8'))
        except Exception: pass
    events = audit.get('events', [])

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    new_events, filled_tables = [], {}

    for k, cur in seats.items():
        st, gm, tb, seat = k.split('-')
        prev = old.get(k)
        if prev is None:
            continue                       # новое место (первый снимок или посев) — не событие
        scored_before = any(prev.get(f) for f in ('gp','gb','bmb','pen','ci')) or prev.get('role')
        for f, label in FIELDS:
            a, b = prev.get(f), cur.get(f)
            if a == b:
                continue
            kind = 'первичная простановка' if (not scored_before and f != 'name') else 'ИЗМЕНЕНИЕ'
            if not scored_before and f != 'name':
                filled_tables['%s-%s-%s' % (st, gm, tb)] = True
                continue                   # первый ввод протокола не засоряем — пишем одной строкой ниже
            new_events.append({
                'ts': now, 'stage': int(st), 'game': int(gm), 'table': int(tb), 'seat': int(seat),
                'player': cur.get('name') or prev.get('name'), 'field': f, 'label': label,
                'was': human(f, a), 'now': human(f, b), 'kind': kind,
            })

    for key in sorted(filled_tables):
        st, gm, tb = key.split('-')
        new_events.append({'ts': now, 'stage': int(st), 'game': int(gm), 'table': int(tb),
                           'seat': 0, 'player': '', 'field': 'protocol', 'label': 'протокол внесён',
                           'was': '—', 'now': 'внесён', 'kind': 'первичная простановка'})

    gone = [k for k in old if k not in seats]
    for k in sorted(gone)[:20]:
        st, gm, tb, seat = k.split('-')
        new_events.append({'ts': now, 'stage': int(st), 'game': int(gm), 'table': int(tb), 'seat': int(seat),
                           'player': old[k].get('name'), 'field': 'seat', 'label': 'место',
                           'was': old[k].get('name'), 'now': '— (снято)', 'kind': 'ИЗМЕНЕНИЕ'})

    events.extend(new_events)
    events = events[-MAX_EVENTS:]

    io.open(SNAP, 'w', encoding='utf-8').write(json.dumps(
        {'t': T, 'taken': now, 'seats': seats}, ensure_ascii=False))
    io.open(AUDIT, 'w', encoding='utf-8').write(json.dumps(
        {'t': T, 'updated': now, 'events': events}, ensure_ascii=False, indent=0))

    changes = [e for e in new_events if e['kind'] == 'ИЗМЕНЕНИЕ']
    log('мест %d · новых событий %d (из них правок %d) · всего в журнале %d'
        % (len(seats), len(new_events), len(changes), len(events)))
    for e in changes[:20]:
        log('  игра %s стол %s место %s · %s · %s: %s → %s'
            % (e['game'], e['table'], e['seat'], e['player'], e['label'], e['was'], e['now']))

if __name__ == '__main__':
    main()
