#!/usr/bin/env python3
"""
timing_692 · v1.0 · 2026-10-17
Назначение: «Расписание план/факт» Central Cup 2026 (mafgame 692). Каждые 5 минут смотрит протоколы
столов и запоминает, КОГДА впервые появился результат стола (res — победа красных/чёрных) и когда
появились баллы/допы (pts). mafgame времени не отдаёт — время = момент, когда робот это увидел
(точность ±5 мин + задержка запуска GitHub). Страница t692.html (раздел «Расписание») считает из этого
конец столов и туров, отклонение от плана (data/schedule_692.json) и прогноз конца дня.

Оглавление: 1 настройки · 2 чтение game_results · 3 какие столы готовы · 4 запись data/timing_692.json
Предохранители: страница не распарсилась / мест меньше MIN_SEATS — выходим, ничего не пишем.
Уже записанное время никогда не перезаписывается (первое появление — и есть факт).
"""
import datetime, html, json, re, sys, time, urllib.request

T = '692'
FROM_DATE, TO_DATE = datetime.date(2026, 10, 17), datetime.date(2026, 10, 18)
MIN_SEATS = 300
HOSTS = ['https://mafgame.org', 'https://dovod-mafia.com/mafgame']
OUT = 'data/timing_692.json'
UA = 'DOVOD-bot/1.0 (+https://dovod-mafia.com; Central Cup 2026 schedule)'

def log(m): print(m, flush=True)

def fetch(path):
    last = None
    for host in HOSTS:
        for _ in (1, 2):
            try:
                req = urllib.request.Request(host + path, headers={'User-Agent': UA, 'Accept': 'text/html'})
                with urllib.request.urlopen(req, timeout=45) as r:
                    return r.read().decode('utf-8', 'replace')
            except Exception as e:
                last = e; time.sleep(2)
    raise SystemExit('не прочитать %s: %s' % (path, last))

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    today = (now + datetime.timedelta(hours=2)).date()   # Прага (CEST)
    if not (FROM_DATE <= today <= TO_DATE) and '--force' not in sys.argv:
        log('вне окна турнира — выходим'); return
    page = fetch('/tournaments/%s/game_results' % T)
    m = re.search(r'data-page="([^"]+)"', page)
    if not m: raise SystemExit('нет data-page')
    g = json.loads(html.unescape(m.group(1)))['props']['games']
    seats = g.get('seats') or {}
    if len(seats) < MIN_SEATS: raise SystemExit('мало мест: %d' % len(seats))
    res = g.get('results') or {}
    outc = g.get('game_outcomes') or {}
    tabs = {}
    for k, s in seats.items():
        p = k.split('-')
        if len(p) != 4 or not s or not s.get('original_nickname'): continue
        key = '-'.join(p[:3])
        t = tabs.setdefault(key, {'n': 0, 'pts': False})
        t['n'] += 1
        if any(abs(float(s.get(f) or 0)) > 1e-9 for f in ('game_points', 'game_bonus', 'best_move_bonus', 'penalty')):
            t['pts'] = True
    try: D = json.load(open(OUT, encoding='utf-8'))
    except Exception: D = {'tournament_id': 692, 'tables': {}}
    TT = D.setdefault('tables', {})
    stamp = now.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    changed = []
    for key, t in tabs.items():
        r = res.get(key) if isinstance(res, dict) else None
        has_res = r in ('red', 'black') or (isinstance(outc, dict) and outc.get(key) in ('red', 'black'))
        e = TT.setdefault(key, {})
        if has_res and 'res' not in e: e['res'] = stamp; changed.append(key + ' res')
        if t['pts'] and 'pts' not in e: e['pts'] = stamp; changed.append(key + ' pts')
        if not e: TT.pop(key)
    if not changed: log('новых столов нет'); return
    D['last_change'] = stamp
    D['note'] = 'Время — когда робот впервые увидел результат (res) и баллы/допы (pts) стола на mafgame; шаг 5 мин, UTC.'
    json.dump(D, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    log('записано: ' + ', '.join(changed))

if __name__ == '__main__': main()
