#!/usr/bin/env python3
"""update_top50.py · v1.0 · 2026-09-21 — подтягивает официальный рейтинг mafgame (data/research/ledger/ratings.json, снимок робота)
в D.top50 календаря (calendar.html) и ставит дату рейтинга в data/meta.js (ratingUpdated).
Раньше делалось руками при каждой выгрузке — в подвалах висела старая дата рядом со свежим снимком гонки."""
import json, re, os, sys, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.environ.get('GD_REPO') or os.path.abspath(os.path.join(HERE,'..','..','..'))
T=os.environ.get('GD_T') or datetime.date.today().isoformat()
RT=json.load(open(os.path.join(REPO,'data/research/ledger/ratings.json'),encoding='utf-8'))
year=str(datetime.date.fromisoformat(T).year); rows=RT.get(year) or []
if len(rows)<50: sys.exit(f'рейтинг {year}: только {len(rows)} строк — не трогаем')
top=[{'pos':r['position'],'uid':r['uid'],'nick':r['nick'],'pts':r['rating']} for r in rows[:50]]
p=os.path.join(REPO,'calendar.html'); s=open(p,encoding='utf-8').read()
m=re.search(r'"top50":\s*\[.*?\]',s,re.S)
if not m: sys.exit('D.top50 в calendar.html не найден')
old=json.loads(m.group(0)[len('"top50":'):])
new_s=s[:m.start()]+'"top50": '+json.dumps(top,ensure_ascii=False)+s[m.end():]
changed=old!=top
if changed: open(p,'w',encoding='utf-8').write(new_s)
d=datetime.date.fromisoformat(T).strftime('%d.%m.%Y')
mp=os.path.join(REPO,'data','meta.js'); ms=open(mp,encoding='utf-8').read()
ms2=re.sub(r"ratingUpdated:\s*'[^']*'",f"ratingUpdated: '{d}'",ms)
if ms2!=ms: open(mp,'w',encoding='utf-8').write(ms2)
diff=sum(1 for a,b in zip(old,top) if (a['uid'],a['pts'])!=(b['uid'],b['pts']))
print(f'top50: {"обновлён" if changed else "без изменений"} ({diff} строк отличались), рейтинг на {d}')
