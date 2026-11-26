#!/usr/bin/env python3
"""check_cards.py · v1.0 · 2026-11-26 - автопроверка карточек и страниц турниров по канону.
Канон: Obsidian, «Методология сайта/11 - Канон карточки и страницы турнира». Краткая копия - CLAUDE.md, раздел «Канон карточки и страницы турнира».
Что проверяет (ничего не правит):
  карточка в data/tournaments.js - обязательные поля по состоянию, форматы приза/дат/названия, соответствие статуса датам,
  файлы - обложка, страница, смотровая, состав, tournament_{id}.json, сила состава,
  страница t{id}.html - свой id в CFG, своя обложка, START = start_iso, нет чужих названий из шаблона.
Выход: печать отчёта (в Actions - в сводку шага и предупреждения); с флагом --write ещё и data/cards_report.json. Код возврата 0 всегда: проверка не блокирует роботов.
Запуск: python3 .github/scripts/check_cards.py [--today 2026-11-26] [--write]"""
import json, re, os, io, sys, datetime, subprocess

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TODAY = sys.argv[sys.argv.index('--today') + 1] if '--today' in sys.argv else (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).date().isoformat()
CANON_SINCE = '2026-11-01'      # страницы турниров проверяем по канону с этой даты старта; более ранние - архив на старых шаблонах
ex = lambda *p: os.path.exists(os.path.join(BASE, *p))
rd = lambda *p: io.open(os.path.join(BASE, *p), encoding='utf-8').read()

def load_cards():
    js = "global.window={};require(%s);process.stdout.write(JSON.stringify(window.TOURNAMENTS_DB.tournaments))" % json.dumps(os.path.join(BASE, 'data', 'tournaments.js'))
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)

def state(t):
    if t.get('status') == 'finished': return 'finished'
    a = t.get('liveFrom') or t.get('start'); b = t.get('liveTo') or a
    if a and b and a <= TODAY <= b: return 'live'
    if b and TODAY > b: return 'played'
    return 'gathering' if t.get('status') == 'gathering' else 'upcoming'

PRIZE = re.compile(r'^\d[\d ]* [€$₸](( \+ [^—–]+)?)$')
DATES = re.compile(r'^\d{1,2}(-\d{1,2})? [а-я]+( - \d{1,2} [а-я]+)? \d{4}$')

def check(t, strength):
    E, W = [], []; tid = str(t.get('id')); st = state(t); start = t.get('start') or ''
    need = ['id', 'name', 'dates', 'city', 'country', 'players', 'days', 'stars', 'status', 'statusLabel', 'start', 'mafgame']
    for f in need:
        if t.get(f) in (None, ''): (W if f in ('country', 'days', 'mafgame') and st == 'finished' else E).append('нет поля %s' % f)
    for f in ('name', 'dates', 'statusLabel', 'prize'):
        if any(c in str(t.get(f) or '') for c in '—–'): W.append('длинное тире в %s' % f)
    if t.get('dates') and not DATES.match(t['dates']): W.append('даты не по формату «28-29 ноября 2026»: %s' % t['dates'])
    if t.get('prize') and not PRIZE.match(t['prize']): W.append('приз не по формату «1200 €»: %s' % t['prize'])
    if st == 'played': E.append('турнир сыгран (%s), а карточка не закрыта: нужны status finished, чемпион, топ-3' % (t.get('liveTo') or start))
    if st != 'finished':
        for f in ('liveFrom', 'liveTo'):
            if not t.get(f): W.append('нет %s - состояние «идёт» не включится само' % f)
        if not str(t.get('statusLabel') or '').startswith(('Скоро', 'Сбор', 'Идёт')): W.append('statusLabel начинается не со «Скоро / Сбор / Идёт»')
        if not ex('data', 'participants_%s.json' % tid): E.append('нет состава data/participants_%s.json' % tid)
        if t.get('mmrAvg') is None: W.append('нет mmrAvg (ждёт робота MMR)')
        if not t.get('strength') and tid not in strength: W.append('нет силы состава (ни в карточке, ни в data/strength.js)')
        if not t.get('prize'): W.append('не указан приз')
        if not t.get('art'): W.append('нет обложки (art)')
    else:
        if not str(t.get('statusLabel') or '').startswith('Завершён'): W.append('statusLabel завершённого начинается не с «Завершён»')
        if start >= CANON_SINCE:
            if not t.get('champion') and not t.get('paired'): E.append('завершён, но нет чемпиона')
            if not t.get('top3') and not t.get('paired'): W.append('завершён, но нет топ-3')
            if not t.get('mvp'): W.append('завершён, но нет MVP')
    for f in ('art', 'thumb'):
        if t.get(f) and not ex(t[f]): E.append('файл %s не найден: %s' % (f, t[f]))
    if t.get('art') and not t.get('thumb') and start >= CANON_SINCE: W.append('есть обложка, но нет уменьшенной (thumb) для списка «Дальше» на главной')
    for f in ('page', 'watch'):
        if t.get(f) and not ex(t[f].split('?')[0]): E.append('файл %s не найден: %s' % (f, t[f]))
    # страница турнира по канону
    if t.get('page') and start >= CANON_SINCE and re.match(r'^t\d+\.html$', t['page']) and ex(t['page']):
        s = rd(t['page'])
        if not re.search(r"const CFG=\{id:'%s'" % tid, s): E.append('страница %s: в CFG чужой id' % t['page'])
        if not t.get('watch'): W.append('есть страница, но нет смотровой')
        if not ex('data', 'tournament_%s.json' % tid): E.append('нет data/tournament_%s.json' % tid)
        else:
            tj = json.loads(rd('data', 'tournament_%s.json' % tid))
            m = re.search(r"const START='([^']+)'", s)
            if m and tj.get('start_iso') and m.group(1) != tj['start_iso']: W.append('страница: START (%s) не совпадает со start_iso (%s)' % (m.group(1), tj['start_iso']))
            if st in ('upcoming', 'live') and not tj.get('chief_referee'): W.append('в tournament_%s.json нет главного судьи' % tid)
            if st == 'finished' and not tj.get('closed'): W.append('карточка завершена, а tournament_%s.json не закрыт (заморозка freeze_tournament не сделана)' % tid)
            if st == 'finished' and not ex('data', 'games_%s_current.json' % tid): W.append('нет замороженных протоколов data/games_%s_current.json' % tid)
        m = re.search(r'<div class="poster[^"]*"><img src="([^"]+)"', s)
        if m and not ex(m.group(1)): E.append('страница: обложка не найдена: %s' % m.group(1))
        if m and t.get('art') and m.group(1) != t['art']: W.append('обложка на странице (%s) и на карточке (%s) разные' % (m.group(1), t['art']))
        key = re.sub(r'[:·].*$', '', str(t.get('name') or '')).strip().split(' 20')[0]
        if key and key.lower() not in s.lower(): W.append('на странице нет названия турнира «%s» - возможно, остались тексты шаблона' % key)
        if st != 'finished' and not ex('data', 'streams_%s.json' % tid): W.append('нет data/streams_%s.json (число игр первого дня и эфиры)' % tid)
    return st, E, W

def main():
    cards = load_cards()
    try: strength = set(re.findall(r'"(\d+)":\{', rd('data', 'strength.js')))
    except Exception: strength = set()
    rep = []; ne = nw = 0
    for t in cards:
        st, E, W = check(t, strength); ne += len(E); nw += len(W)
        if E or W: rep.append({'id': str(t.get('id')), 'name': t.get('name'), 'state': st, 'errors': E, 'warnings': W})
    out = {'snap': TODAY, 'cards': len(cards), 'errors': ne, 'warnings': nw, 'items': rep}
    if '--write' in sys.argv:   # файл отчёта - только по флагу: в Actions не пишем, чтобы не плодить ежедневные коммиты
        io.open(os.path.join(BASE, 'data', 'cards_report.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    lines = ['### Канон карточек: %d турниров, ошибок %d, замечаний %d (%s)' % (len(cards), ne, nw, TODAY)]
    for r in rep:
        lines.append('- **%s · %s** (%s)' % (r['id'], r['name'], r['state']))
        lines += ['  - ❌ ' + x for x in r['errors']] + ['  - ⚠️ ' + x for x in r['warnings']]
    txt = '\n'.join(lines); print(txt)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        io.open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write(txt + '\n')
        for r in rep:
            for x in r['errors']: print('::warning title=Канон карточки %s::%s' % (r['id'], x))

if __name__ == '__main__':
    try: main()
    except Exception as e: print('check_cards: не отработал (%s)' % e)
    sys.exit(0)
