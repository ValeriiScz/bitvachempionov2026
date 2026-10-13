"""bt_calibrate.py · v1.0 · 2026-10-13 — бэктест калибровки модели дюжины: срез 14.09 → факт 31.12.
Запуск из data/research/model: python3 bt_calibrate.py <год> <RACE_BOOST> [frailty] [RECENT 0/1] [C]
Выводит: порог 12-го (модель/факт), старты топ-30 (модель/факт), угадано из 12, Brier, корреляцию стартов модель↔факт."""
import numpy as np, sys, gd_data as g, gd_sim, gd_attend
gd_attend.RECENT=(sys.argv[4]=="1") if len(sys.argv)>4 else True
gd_sim.C=float(sys.argv[5]) if len(sys.argv)>5 else gd_sim.C
year=int(sys.argv[1]); gd_sim.RACE_BOOST=float(sys.argv[2]); fr=float(sys.argv[3]) if len(sys.argv)>3 else 2.0
from gd_sim import Season
T=f'{year}-09-14'; se=Season(year,T,verbose=False); res=se.run(S=1500,seed=1,frailty=fr if fr>0 else None)
fin=g.standings(year); fin12=[u for s,u in fin[:12]]; pool=res['pool']
order=np.argsort(-res['p12']); hit=len(set(pool[i] for i in order[:12])&set(fin12))
y=np.array([1 if u in fin12 else 0 for u in pool]); br=((res['p12']-y)**2).mean()
mid=g.standings(year,T); top=[u for s,u in mid[:30]]; i=[pool.index(u) for u in top if u in pool]
act={}
for e in g.EV.values():
    if e['year']==year and e['date']>=T and e['kind']!='serial_final':
        for r in e['rows']: act[r[0]]=act.get(r[0],0)+1
ll=np.mean([np.log(max(res['p12'][pool.index(u)],1e-3)) for u in fin12])
print(f"{year} boost {gd_sim.RACE_BOOST} fr {fr}: порог мод {np.median(res['thr']):.0f} [{np.percentile(res['thr'],10):.0f}–{np.percentile(res['thr'],90):.0f}] факт {fin[11][0]:.0f} | стартов топ-30 {res['played'][i].mean():.2f} факт {np.mean([act.get(u,0) for u in top]):.2f} | попаданий {hit}/12 | Brier {br:.4f} | logP дюжины {ll:.2f}")
pm=res['played'][i]; pa=np.array([act.get(u,0) for u in top if u in pool])
print(f"   корреляция стартов модель↔факт по топ-30: {np.corrcoef(pm,pa)[0,1]:.2f}; средняя ошибка на игрока {np.abs(pm*pa.sum()/pm.sum()-pa).mean():.2f}")
