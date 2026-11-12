"""format_sim.py · v1.0 · 2026-11-11 — модель форматов турнира спортивной мафии (Валерий, 10–11.11.2026).
Игра: 10 за столом, роли случайно (7 красных/3 чёрных); P(победа красных)=σ(a+b·(Σz_красных−Σz_чёрных)); очки = победа + доп(сила).
Сила z = (MMR−μ)/σ из mmr.json (список MMR активных; см. data/mmr.json). Поле: выборка с весом exp(γz) — сильные ездят чаще.
Калибровка (11.11): c=0.065, sd=0.2 → сильнейший по MMR выигрывает 35%, в финале 82%, топ-10→финал 53% (реально по 53 турнирам MG 2025–26: 34/78/53).
Форматы: G — игр в отборе, swiss — швейцарка с тура N, sf/sfG — полуфинал (размер/игры), FG — игр финала, freset — финал с нуля. Финал ×1,3 с переносом очков.
Запуск: python3 format_sim.py (калибровка); эксперименты — exp_sizes.py, exp_formats.py N..."""
import numpy as np, json, sys
POOL=np.array(json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'mmr_active.json')))); MU,SD=POOL.mean(),POOL.std()
Z=(POOL-MU)/SD
P=dict(a=0.15, b=0.06, c=0.12, mu=0.18, sd=0.22, gam=0.5, fcoef=1.3)
def field(N,rng):
    w=np.exp(P['gam']*Z); w/=w.sum()
    idx=rng.choice(len(Z),N,replace=False,p=w); return Z[idx]
def play(z,players,rng,score):
    # players: array of 10 indices
    r=rng.permutation(10); black=players[r[:3]]; red=players[r[3:]]
    pr=1/(1+np.exp(-(P['a']+P['b']*(z[red].sum()-z[black].sum()))))
    redwin=rng.random()<pr
    win=np.zeros(10); win[3:]=redwin; win[:3]=not redwin
    pl=players[r]
    dop=np.maximum(0,P['mu']+P['c']*z[pl]+0.1*win+P['sd']*rng.standard_normal(10))
    score[pl]+=win+dop
def rounds(z,group,G,rng,score,swiss_from=None):
    n=len(group); T=n//10; R=int(np.ceil(G*n/(10*T)))
    played=np.zeros(n)
    for rd in range(R):
        # who plays: those with fewest games (rotation)
        order=np.lexsort((rng.random(n),played)); act=order[:T*10]
        played[act]+=1
        if swiss_from is not None and rd>=swiss_from:
            act=act[np.argsort(-score[group[act]]+1e-6*rng.random(len(act)))]
        else:
            act=rng.permutation(act)
        for t in range(T): play(z,group[act[t*10:(t+1)*10]],rng,score)
    # normalize for unequal games (rotation leftovers): per-game avg * G
    return played
def tourney(N,fmt,rng):
    z=field(N,rng); score=np.zeros(N); allp=np.arange(N)
    G=fmt.get('G', 12 if N%10==0 else 10)
    pl=rounds(z,allp,G,rng,score,fmt.get('swiss'))
    score=score/np.maximum(pl,1)*G
    if fmt.get('sf'):
        top=np.argsort(-score)[:fmt['sf']]; s2=np.zeros(N)
        rounds(z,top,fmt.get('sfG',2),rng,s2); score=score+s2*fmt.get('sfcoef',1.0)
        if fmt.get('sfreset'): score=np.where(np.isin(allp,top),s2,-1e9)
    fin=np.argsort(-score)[:10]; s3=np.zeros(N)
    for g in range(fmt.get('FG',4)): play(z,fin,rng,s3)
    tot=score.copy(); tot[fin]+=P['fcoef']*s3[fin]
    if fmt.get('freset'): tot=np.where(np.isin(allp,fin),s3+1e3,tot)
    order=np.argsort(-tot)
    return z,order,fin
def metrics(N,fmt,reps=600,seed=1):
    rng=np.random.default_rng(seed); M=[]
    for _ in range(reps):
        z,order,fin=tourney(N,fmt,rng)
        true=np.argsort(-z); best=true[0]
        place=np.empty(N,int); place[order]=np.arange(1,N+1)
        rho=np.corrcoef(place,np.argsort(np.argsort(-z))+1)[0,1]
        M.append((order[0]==best, place[best]<=10, len(set(fin)&set(true[:10]))/10, z[fin].mean()*SD+MU, z[order[0]]*SD+MU, order[0] in true[:3], rho))
    M=np.array(M,float); return dict(win=M[:,0].mean(),bestfin=M[:,1].mean(),top10=M[:,2].mean(),finmmr=M[:,3].mean(),winmmr=M[:,4].mean(),wintop3=M[:,5].mean(),rho=M[:,6].mean())
if __name__=='__main__':
    for c in (0.08,0.12,0.16,0.2):
        P['c']=c; m=metrics(33,{},400); print(c,{k:round(v,2) for k,v in m.items()})
