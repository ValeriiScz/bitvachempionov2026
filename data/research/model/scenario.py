import numpy as np, gd_data as g, gd_sim, sys
from gd_sim import Season
T='2026-09-14'; Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
se=Season(2026,T,cal_future=fut,verbose=False)
nick=sys.argv[1] if len(sys.argv)>1 else 'DOVOD'
uid=[int(u) for u,v in g.L.items() if v['nick']==nick][0]; i=se.pool.index(uid)
evs=[e for e in se.events if e['type']!='contour']
ranked=sorted(evs,key=lambda e:-e['p'][uid])
print(f"{nick}: Σ сейчас {g.best10(se.base[uid]):.0f}, десятка {sorted([p for p,s in se.base[uid]],reverse=True)[:10]}")
print('вероятность явки по турнирам (модель):')
for e in ranked[:14]: print(f"   {e['date']} {e['name'][:34]:34s} {e['stars']}★ N={e['N']:3d} {e['country'][:14]:14s} p={e['p'][uid]*100:3.0f}%")
res0=se.run(S=2500,seed=21,frailty=None); thr=res0['thr']
print(f"\nбаза: P12 {res0['p12'][i]*100:.0f}%, ожид. турниров {res0['played'][i]:.1f}, ожΣ {res0['sums'][:,i].mean():.0f}")
print('\nШанс войти при итоговой Σ (= доля симуляций, где порог ≤ Σ):')
for x in (130,140,145,150,155,160,165,170,180): print(f"   Σ={x}: {np.mean(thr<=x)*100:3.0f}%")
print('\nСценарии явки (форсируем участие в k самых вероятных для игрока турнирах, остальное — как модель):')
for k in (0,4,6,8,10,12):
    force={uid:{e['id'] for e in ranked[:k]}} if k else None
    r=se.run(S=2000,seed=31,frailty=None,force=force); s=r['sums'][:,i]
    print(f"   k={k:2d}: сыграет ~{r['played'][i]:4.1f}  P12 {r['p12'][i]*100:3.0f}%  ожΣ {s.mean():4.0f} [{np.percentile(s,10):.0f}–{np.percentile(s,90):.0f}]  прирост обыч {r['new_reg'][i]:.0f}")
# что нужно по результатам: сколько топ-10 / топ-5 на 4-5★ нужно
print('\nсколько стоит результат (сетка 4★ при N≈33–44, 5★ N≈44):')
for st,n in ((4,40),(5,44),(3,33)):
    pts=se.grid_pts(st,'regular',n); print(f"   {st}★ N={n}: 1-е {pts[0]:.0f}, 3-е {pts[2]:.0f}, 5-е {pts[4]:.0f}, 10-е {pts[9]:.0f}, 15-е {pts[14]:.0f}")
