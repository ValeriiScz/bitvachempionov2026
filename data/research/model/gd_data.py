"""gd_data · v1.0 · 2026-09-14 — загрузка данных «золотой дюжины»: леджеры, таблицы, листинги, серийники, календарь."""
import json, collections, datetime
R='/tmp/claude-0/-home-claude/a54b72ce-f72e-5c02-98ee-5f25f1671c21/scratchpad/repo/'
D=R+'data/research/ledger/'
L=json.load(open(D+'ledgers.json')); P=json.load(open(D+'points.json')); T=json.load(open(D+'tournaments.json')); RT=json.load(open(D+'ratings.json'))
SER_IX=json.load(open(R+'data/research/series/index.json'))
SER={p['id']:json.load(open(R+'data/research/series/'+p['file'])) for p in SER_IX['parents']}
_s=open(R+'calendar.html',encoding='utf-8').read(); _i=_s.find('const D=');_j=_s.find('};',_i); CAL=json.loads(_s[_i+8:_j+1])

TID={int(t['id']):dict(t,year=int(y)) for y in T for t in T[y]}
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
