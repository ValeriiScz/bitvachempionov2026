import numpy as np, gd_data as g, gd_sim, sys
from gd_sim import Season
for year in (2025,2024):
    T=f'{year}-09-14'
    for rb in (1.0,1.2,1.35):
        gd_sim.RACE_BOOST=rb
        se=Season(year,T,verbose=False); se.events=[e for e in se.events if e['id']!=341]
        fin=g.standings(year); fin12=set(u for s,u in fin[:12]); mid=g.standings(year,T)
        pool=se.pool; y=np.array([1 if u in fin12 else 0 for u in pool])
        res=se.run(S=800,seed=5,frailty=None); p=res['p12']; pred12={pool[i] for i in np.argsort(-p)[:12]}
        naive=len(set(u for s,u in mid[:12])&fin12)
        print(f'{year} boost={rb}: порог медиана {np.median(res["thr"]):.0f} [{np.percentile(res["thr"],10):.0f}–{np.percentile(res["thr"],90):.0f}] факт {fin[11][0]:.0f}; hit {len(pred12&fin12)}/12 (наив {naive}); Brier {((p-y)**2).mean():.4f}; топ-25 турниров модель {res["played"][[pool.index(u) for s,u in mid[:25]]].sum():.0f} факт {sum(1 for s,u in mid[:25] for r in g.L[str(u)]["rp"] if r[0]==year and r[2]>T and not r[5])}')
