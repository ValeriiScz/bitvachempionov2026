import numpy as np, json, gd_data as g, gd_sim, calendar_expert
from gd_sim import Season
gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP30_MEAN=4.0
T='2026-09-14'; Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
se=Season(2026,T,cal_future=fut,verbose=False)
mid=g.standings(2026,T); top=[u for s,u in mid[:30]]
print('ожидаемое число топ-30 на турнирах (после экспертных весов и нормировки на 4.0/игрока):')
for e in sorted([e for e in se.events if e['type']!='contour'],key=lambda e:e['date']):
    k=sum(e['p'][u] for u in top)
    if k>=1.5: print(f"  {e['date']} {e['name'][:34]:34s} {e['stars']}★ топ-30: {k:4.1f}")
res=se.run(S=3000,seed=11,frailty=None); thr=res['thr']; pool=res['pool']
print(f"\nпланка: медиана {np.median(thr):.0f}, 50% {np.percentile(thr,25):.0f}–{np.percentile(thr,75):.0f}, 80% {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}")
midpos={u:i+1 for i,(s,u) in enumerate(mid)}
print('ожидаемое число турниров у топ-30 по модели:',{g.NICK[u]:round(res['played'][pool.index(u)],1) for u in top[:15]})
json.dump({'T':T,'S':3000,'thr':thr.tolist(),'rows':[{'uid':u,'nick':g.NICK[u],'pos':midpos[u],'played':float(res['played'][pool.index(u)]),'p12':float(res['p12'][pool.index(u)])} for s,u in mid[:60]]},open('forecast2026.json','w'),ensure_ascii=False)
