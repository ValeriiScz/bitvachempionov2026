#!/usr/bin/env python3
"""mmr_calibrate.py · v1.0 · 2026-11-06 — калибровка тиров по MMR (mafiastats) через вероятность выйти в финал.
Данные: места рейтинговых турниров mafgame (data/research/ledger/points.json) × MMR игроков (data/mmr.json).
Берём турниры с 01.09.2025, ≥12 игроков, не командные, покрытие MMR ≥85% (нет MMR → 1350).
Модель: Plackett–Luce по топ-10 итоговой таблицы, сила игрока θ = β·(MMR−1500)/100; места разыгрываются как θ + шум Гумбеля.
Тир = шанс выйти в финал (топ-10) на ТИПИЧНОМ турнире: 30 игроков, соперники — случайные участники обычных 4★ турниров.
Уровни: L ≥75% · S ≥60% · A ≥45% · B ≥33% · C ≥22% · D ≥13% · E ≥7% · F <7%.
ОГОВОРКА: MMR — текущий снимок, а турниры уже прошли (их результаты в MMR учтены) → оценка качества завышена;
честная проверка — прогнозы, сохранённые ДО турнира (data/research/predictions/<id>.json).
Выход: data/research/mmr_tiers.json (β, пороги, таблица «MMR → шанс финала/топ-5/победы», качество)."""
import json, os, numpy as np
from scipy.optimize import minimize
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))+'/'
M=json.load(open(R+'data/mmr.json'))['players']; P=json.load(open(R+'data/research/ledger/points.json')); T=json.load(open(R+'data/research/ledger/tournaments.json'))
TID={str(t['id']):t for y in T for t in T[y]}; MISS=1350.0; FROM='2025-09-01'
ev=[]
for tid,rows in P.items():
    t=TID.get(tid)
    if not t or not rows or len(rows)<12 or t.get('teams') or t['start_date']<FROM: continue
    rows=sorted(rows,key=lambda r:r[2]); m=[M.get(str(r[0]),{}).get('mmr') for r in rows]
    if sum(1 for x in m if x)/len(m)<0.85: continue
    ev.append(dict(id=tid,date=t['start_date'],stars=int(t['no_of_stars'] or 0),serial=bool(t.get('serial')),pos=[r[2] for r in rows],mmr=[x or MISS for x in m]))
def nll(b,E,K=10):
    s=0
    for e in E:
        th=b*(np.array(e['mmr'])-1500)/100; th=th[np.argsort(e['pos'],kind='stable')]
        rev=np.logaddexp.accumulate(th[::-1])[::-1]; s-=np.sum((th-rev)[:K])
    return s
fit=lambda E:float(minimize(lambda p:nll(p[0],E),[0.3],method='Nelder-Mead').x[0])
def score(b,E,seed=2,S=4000):
    rng=np.random.default_rng(seed); L=[];L0=[]
    for e in E:
        th=b*(np.array(e['mmr'])-1500)/100;n=len(th);rk=np.argsort(-(th[None,:]+rng.gumbel(size=(S,n))),axis=1);top=np.zeros(n)
        for k in range(10): np.add.at(top,rk[:,k],1)
        p=np.clip(top/S,1e-3,1-1e-3);y=(np.array(e['pos'])<=10).astype(float);p0=np.full(n,min(10/n,.999))
        L.append(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)));L0.append(-np.mean(y*np.log(p0)+(1-y)*np.log(1-p0)))
    return float(np.mean(L)),float(np.mean(L0))
b=fit(ev); tr=[e for e in ev if e['date']<'2026-06-01']; te=[e for e in ev if e['date']>='2026-06-01']
bh=fit(tr); hold=score(bh,te)
pool=np.array([x for e in ev if e['stars']==4 and not e['serial'] for x in e['mmr']]); rng=np.random.default_rng(3)
def pf(m,S=8000,N=30):
    f=rng.choice(pool,size=(S,N-1));th=b*(np.concatenate([np.full((S,1),m),f],1)-1500)/100;perf=th+rng.gumbel(size=th.shape);r=(perf>perf[:,:1]).sum(1)
    return float((r<10).mean()),float((r<5).mean()),float((r<1).mean())
tab=[(int(m),)+pf(m) for m in range(800,2451,25)]
LV=[('L',.75),('S',.60),('A',.45),('B',.33),('C',.22),('D',.13),('E',.07)]
thr={t:next(m for m,a,_,_ in tab if a>=lv) for t,lv in LV}
thr={t:int(round(v/25)*25) for t,v in thr.items()}
out={'version':'1.0','date':__import__('datetime').date.today().isoformat(),'beta':round(b,4),'miss':MISS,'levels':dict(LV),'thresholds':thr,
     'ref':'типичный турнир: 30 игроков, соперники — участники обычных 4★ (медиана MMR %d)'%np.median(pool),
     'sample':{'tournaments':len(ev),'entries':sum(len(e['pos']) for e in ev),'from':FROM},
     'holdout':{'train':len(tr),'test':len(te),'beta':round(bh,4),'logloss':round(hold[0],4),'logloss_no_rating':round(hold[1],4)},
     'curve':[[m,round(a,3),round(c,3),round(w,4)] for m,a,c,w in tab]}
json.dump(out,open(R+'data/research/mmr_tiers.json','w'),ensure_ascii=False,indent=1)
print('β',round(b,3),'пороги',thr,'holdout',out['holdout'])
