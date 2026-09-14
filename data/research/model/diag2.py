import numpy as np, gd_data as g, sys
from gd_sim import Season
year=int(sys.argv[1]); T=f'{year}-09-14'
se=Season(year,T,verbose=False); se.events=[e for e in se.events if e['id']!=341]
res=se.run(S=500,seed=2); pool=res['pool']; idx={u:i for i,u in enumerate(pool)}
mid=g.standings(year,T); top=[u for s,u in mid[:40]]
fr=fs=0
for u in top:
    for r in g.L[str(u)]['rp']:
        if r[0]==year and r[2]>T: 
            if r[5]: fs+=r[4]
            else: fr+=r[4]
ti=[idx[u] for u in top]
print(f'{year} топ-40 на T: обычные факт {fr:.0f} vs модель {res["new_reg"][ti].sum():.0f}; серийные факт {fs:.0f} vs модель {res["new_ser"][ti].sum():.0f}')
fin=g.standings(year); fin12=[u for s,u in fin[:12]]
print('фактическая дюжина: Σ факт vs ожΣ модели, прирост факт (обыч/сер) vs модель')
for s,u in fin[:12]:
    i=idx[u]; b=g.best10(g.ledger_recs(u,year,T))
    fr_=sum(r[4] for r in g.L[str(u)]['rp'] if r[0]==year and r[2]>T and not r[5]); fs_=sum(r[4] for r in g.L[str(u)]['rp'] if r[0]==year and r[2]>T and r[5])
    print(f"  {g.NICK[u]:14s} база {b:4.0f} → факт {s:4.0f} / модель {res['sums'][:,i].mean():4.0f}   прирост факт {fr_:3.0f}+{fs_:3.0f}  модель {res['new_reg'][i]:3.0f}+{res['new_ser'][i]:3.0f}   турниров факт {sum(1 for r in g.L[str(u)]['rp'] if r[0]==year and r[2]>T and not r[5])} модель {res['played'][i]:.1f}")
print('порог модель',np.median(res['thr']),'факт',fin[11][0])
