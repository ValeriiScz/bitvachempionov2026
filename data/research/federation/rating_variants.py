"""rating_variants.py · v1.0 · 2026-11-12 — «а что было бы»: рейтинг MafGame 2026 (и 2025) при других правилах (Валерий, 10–11.11.2026).
Запуск из data/research/model:  python3 ../federation/rating_variants.py [scales|cutoff|serial] [YYYY-MM-DD]
- scales: те же турниры, другая раздача баллов (сумма за турнир та же, кроме more/im1): cur, lin (ровно), sq (круто),
  more (1-е как сейчас, ×r до 5% у последнего), im (форма iMafia), im1 (форма iMafia, 1-е как сейчас). Финалы серий не трогаем.
- cutoff: в зачёт 5…15 лучших (≤2 серийных).
- serial: серийники — cur / max1 (≤1 в зачёте) / asreg (как обычный турнир тех же звёзд) / imafia (×1,2 обычного, форма iMafia) / none.
Метрика силы: средний MMR (data/mmr.json, mafiastats) дюжины, топ-20, топ-30.
Шкала iMafia — по вкладке «Баллы» турниров imafia.org (Over Hype 1797, Kraków Supreme 1532, ЧЕ 1366): медали ×2,1/1,8/1,6 к 10-му, 4–10 −2,5%/место, 11-е −38%, далее −4%/место."""
import sys, json, numpy as np, collections
sys.path.insert(0,'.')
import gd_data as g
MODE=(sys.argv[1] if len(sys.argv)>1 else 'scales'); T=(sys.argv[2] if len(sys.argv)>2 else '2026-12-31'); Y=int(T[:4])
MM=json.load(open('../../mmr.json'))['players']; mmr=lambda u:(MM.get(str(u)) or {}).get('mmr')
REG={4:[27,24,22,19,17,15,13,11,9,7,5,4],3:[24,21,19,16,14,12,10,8,6,4,3,3],2:[19,16,14,11,9,7,5,3,2,2,2,2],1:[14,11,9,6,4,2,1,1,1,1,1,1]}
BASE={4:4,3:3,2:2,1:1}
def imshape(N):
    w=[]
    for k in range(1,N+1):
        if k<=3: w.append([1.775,1.552,1.332][k-1])
        elif k<=10: w.append(1-0.0255*(k-4))
        else: w.append(0.847*0.617*0.958**(k-11))
    return np.array(w)
def dist(m,N,S,P1):
    k=np.arange(1,N+1)
    if m=='lin': w=(N+1-k).astype(float); return S*w/w.sum()
    if m=='sq': w=((N+1-k)**2).astype(float); return S*w/w.sum()
    if m=='more': r=0.05**(1/max(N-1,1)); return P1*r**(k-1)
    if m=='im': w=imshape(N); return S*w/w.sum()
    if m=='im1': w=imshape(N); return P1*w/w[0]
def best(recs,K=10,ms=2):
    recs=sorted(recs,key=lambda r:-r[0]); t=n=s=0
    for p,se in recs:
        if n>=K: break
        if se:
            if s>=ms: continue
            s+=1
        t+=p; n+=1
    return t
def regular_new(m):
    newp={}
    for tid,ev in g.EV.items():
        if ev['year']!=Y or ev['kind']!='regular' or not ev['rows'] or str(ev['date'])>T: continue
        rs=sorted(ev['rows'],key=lambda r:(r[2] or 999)); n=len(rs); s=sum(r[3] for r in rs); p1=max(r[3] for r in rs)
        d=dist(m,n,s,p1); bp={}
        for i,r in enumerate(rs): bp.setdefault(r[2],[]).append(d[i])
        for r in rs: newp[(tid,r[0])]=float(np.mean(bp[r[2]]))
    return newp
ntot=collections.Counter(r[1] for v in g.L.values() for r in v['rp'] if r[0]==Y and r[5])
def ser(var,tid,pos,orig):
    st=int(g.TID[tid]['no_of_stars'])
    if var in ('cur','max1'): return orig
    if var=='none': return 0
    if var=='asreg': return REG[st][min(pos,12)-1] if pos else BASE[st]
    if var=='imafia':
        w=imshape(max(ntot[tid],30)); sc=1.2*REG[st][0]/w[0]
        return float(sc*w[pos-1]) if pos else float(sc*w[min(len(w)-1,25)])
def table(variant):
    out={}
    for u,v in g.L.items():
        recs=[]; K=10; ms=2
        if MODE=='cutoff': K=variant
        if MODE=='serial': ms={'max1':1,'none':0}.get(variant,2)
        for r in v['rp']:
            if r[0]!=Y or r[2]>T: continue
            if r[5]: recs.append((ser(variant,r[1],r[3],r[4]) if MODE=='serial' else r[4],1))
            else: recs.append(((NEWP.get((r[1],int(u)),r[4]) if MODE=='scales' else r[4]),0))
        s=best(recs,K,ms)
        if s>0: out[int(u)]=s
    return out
VARS={'scales':['cur','lin','sq','more','im','im1'],'cutoff':list(range(5,16)),'serial':['cur','max1','asreg','imafia','none']}[MODE]
R={}
for v in VARS:
    NEWP=regular_new(v) if (MODE=='scales' and v!='cur') else {}
    R[v]=table(v)
rk={v:{u:i+1 for i,u in enumerate(sorted(R[v],key=lambda u:(-R[v][u],g.NICK[u])))} for v in VARS}
base=VARS[0] if MODE!='cutoff' else 10
print('MMR дюжины / топ-20 / топ-30:')
for v in VARS:
    o=sorted(R[v],key=lambda u:-R[v][u]); print(' ',v,[round(np.mean([mmr(u) for u in o[:N] if mmr(u)])) for N in (12,20,30)])
names=set()
for v in VARS: names|={u for u in rk[v] if rk[v][u]<=20}
for u in sorted(names,key=lambda u:rk[base].get(u,999)):
    print(f"{g.NICK[u]:14s}",' '.join(f"{round(R[v].get(u,0)):4d}#{rk[v].get(u,0):<3d}" for v in VARS))
