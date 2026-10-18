"""gd_data · v1.3.1 · 2026-10-19 (ручной перезапуск пересбора после Central Cup 692: GitHub задержал воскресный cron) · v1.3 · 2026-10-14 (сверка: mafgame 13.10 пересчитал финалы PSP-639 и CEC-694 ровно по SERIAL_GRID_2026 — леджеры/рейтинг/страницы турниров; страница /pages/mafgame_points ещё со старой таблицей серийников. Поправка оставлена страховкой для будущих финалов: при совпадении ничего не меняет) · v1.2 · 2026-10-13 (финалы серийников 2026 — баллы по сетке федерации SERIAL_GRID_2026, а не как начислил сайт mafgame) · v1.1 · 2026-09-21 (путь репо: GD_REPO или относительно файла) · v1.0 · 2026-09-14 — загрузка данных «золотой дюжины»: леджеры, таблицы, листинги, серийники, календарь."""
import json, collections, datetime, os
_here=os.path.dirname(os.path.abspath(__file__))
_guess=os.path.abspath(os.path.join(_here,'..','..','..'))  # data/research/model → корень репо
R=(os.environ.get('GD_REPO') or (_guess if os.path.exists(os.path.join(_guess,'calendar.html')) else '/tmp/claude-0/-home-claude/a54b72ce-f72e-5c02-98ee-5f25f1671c21/scratchpad/repo')).rstrip('/')+'/'
D=R+'data/research/ledger/'
L=json.load(open(D+'ledgers.json')); P=json.load(open(D+'points.json')); T=json.load(open(D+'tournaments.json')); RT=json.load(open(D+'ratings.json'))
SER_IX=json.load(open(R+'data/research/series/index.json'))
SER={p['id']:json.load(open(R+'data/research/series/'+p['file'])) for p in SER_IX['parents']}
_s=open(R+'calendar.html',encoding='utf-8').read(); _i=_s.find('const D=');_j=_s.find('};',_i); CAL=json.loads(_s[_i+8:_j+1])

TID={int(t['id']):dict(t,year=int(y)) for y in T for t in T[y]}
# v1.2 (13.10.2026): сетка баллов за ФИНАЛЫ СЕРИЙНИКОВ сезона 2026 — официально от главы федерации (сообщение, переслано Валерием 13.10):
#   «в прошлом сезоне 2★ были ошибочно внесены с повышенными баллами, в этом сезоне понерфены, сайт mafgame это не отразил;
#    за эту серию (как и за все другие серии) баллы в рейтинг гонки за Дюжину начисляются так, а не как на сайте».
#   Места 1–20; дальше и у не-финалистов (место 65535) — последнее значение сетки.
SERIAL_GRID_2026={1:[14,11,9,6,4,2]+[1]*14,
                  2:[22,19,17,14,12,10,8,6,4]+[2]*11,
                  3:[30,27,25,22,20,18,16,14,12,10,8,6,4]+[3]*7,
                  4:[40,37,35,32,30,28,26,24,22,20,18,16,14,12,10,8,6,4,4,4]}
def serial_pts_2026(stars,pos):
    g=SERIAL_GRID_2026.get(int(stars or 0))
    if not g: return None
    return float(g[min(int(pos),len(g))-1]) if pos and int(pos)>0 else float(g[-1])
_SER26={int(t['id']):int(t['no_of_stars'] or 0) for y in T for t in T[y] if int(y)==2026 and t.get('serial') and t.get('parent_tournament_id') in (None,0) and 1<=int(t['no_of_stars'] or 0)<=5}
SER_FIX={}   # tid → [(uid, было, стало)] для отчёта
for _u,_v in L.items():
    for _r in _v['rp']:
        if _r[0]==2026 and _r[1] in _SER26:
            _n=serial_pts_2026(_SER26[_r[1]],_r[3])
            if _n is not None and _n!=_r[4]: SER_FIX.setdefault(_r[1],[]).append((int(_u),_r[4],_n)); _r[4]=_n
for _tid,_rows in list(P.items()):
    if int(_tid) in _SER26:
        P[_tid]=[[r[0],r[1],r[2],serial_pts_2026(_SER26[int(_tid)],r[2])]+list(r[4:]) for r in _rows]

def is_rating(t): return (t['parent_tournament_id'] in (None,0)) and 1<=int(t['no_of_stars'] or 0)<=5
def kind(t):
    if t.get('teams'): return 'teams'
    if t.get('serial'): return 'serial_final'
    return 'regular'
# события с таблицами: {tid: {date, stars, kind, year, N, rows:[(uid,nick,pos,pts)]}}
EV={}
for tid,t in TID.items():
    if not is_rating(t): continue
    rows=P.get(str(tid)) or []
    EV[tid]={'id':tid,'date':t['start_date'],'stars':int(t['no_of_stars']),'kind':kind(t),'year':t['year'],'country':t.get('country'),
             'name':t['name'],'N':len(rows),'rows':[(r[0],r[1],r[2],r[3]) for r in rows]}
NICK={}
for u,v in L.items(): NICK[int(u)]=v['nick']
for e in EV.values():
    for uid,nick,pos,pts in e['rows']: NICK.setdefault(uid,nick)
COUNTRY={int(u):v['country'] for u,v in L.items()}

def best10(recs):
    """recs: list of (pts, serial) → Σ по правилу 10 лучших, ≤2 серийных"""
    recs=sorted(recs,key=lambda r:-r[0]); tot=0;n=0;ser=0
    for p,s in recs:
        if n>=10: break
        if s:
            if ser>=2: continue
            ser+=1
        tot+=p; n+=1
    return tot
def ledger_recs(uid, year, upto=None):
    v=L.get(str(uid)); 
    if not v: return []
    return [(r[4],r[5]) for r in v['rp'] if r[0]==year and (upto is None or r[2]<=upto)]
def standings(year, upto=None):
    out=[]
    for u in L:
        s=best10(ledger_recs(int(u),year,upto))
        if s>0: out.append((s,int(u)))
    out.sort(reverse=True); return out
