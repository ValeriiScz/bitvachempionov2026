import numpy as np, sys, time, gd_data as g
from gd_sim import Season
year=int(sys.argv[1]); T=f'{year}-09-14'; S=int(sys.argv[2]) if len(sys.argv)>2 else 1500
t0=time.time(); se=Season(year,T)
for ev in se.events:
    if ev['type']=='contour': print(f"  контур {ev['id']} {ev['name'][:30]} {ev['date']}: финалистов {len(ev['fin'])} (ожид {sum(ev['fin'].values()):.1f}) кандидатов {len(ev['cand'])} (ожид {sum(ev['cand'].values()):.1f}), участников контура {len(ev['part'])}")
res=se.run(S=S,seed=1); print(f'симуляций {S}, {time.time()-t0:.0f} c')
fin=g.standings(year); fin12=[u for s,u in fin[:12]]; finpos={u:i+1 for i,(s,u) in enumerate(fin)}; finsum={u:s for s,u in fin}
mid=g.standings(year,T); midpos={u:i+1 for i,(s,u) in enumerate(mid)}
pool=res['pool']; order=np.argsort(-res['p12'])
print(f"\n=== бэктест {year}: срез {T} → факт 31.12 ===")
print(f"порог 12-го: факт {fin[11][0]:.0f}; модель медиана {np.median(res['thr']):.0f}, 80% коридор {np.percentile(res['thr'],10):.0f}–{np.percentile(res['thr'],90):.0f}")
pred12=[pool[i] for i in order[:12]]
print(f"дюжина по вероятности: попали в фактическую {len(set(pred12)&set(fin12))}/12  (наивный 'топ-12 на 14.09 остаётся': {len(set(u for s,u in mid[:12])&set(fin12))}/12)")
print(f"\n{'ник':14s} {'14.09':>6} {'P12':>5} {'ожΣ':>5} {'факт':>5} {'м.факт':>6}")
for i in order[:25]:
    u=pool[i]; print(f"{g.NICK[u]:14s} {midpos.get(u,'-'):>6} {res['p12'][i]*100:4.0f}% {res['sums'][:,i].mean():5.0f} {finsum.get(u,0):5.0f} {finpos.get(u,'-'):>6}  {'★' if u in fin12 else ''}")
print('\nфактическая дюжина, которой модель дала мало:')
for u in fin12:
    i=pool.index(u); 
    if res['p12'][i]<0.3: print(f"  {g.NICK[u]:14s} место 14.09 {midpos.get(u)} → {finpos[u]}, P12 {res['p12'][i]*100:.0f}%, ожΣ {res['sums'][:,i].mean():.0f} факт {finsum[u]:.0f}, ожид.турниров {res['played'][i]:.1f}")
# Brier / log score по всем игрокам
y=np.array([1 if u in fin12 else 0 for u in pool]); p=res['p12']
print(f"\nBrier top-12 по пулу: {((p-y)**2).mean():.4f}; сумма P12 = {p.sum():.1f} (должно ≈12); наивная база (12/N): {((12/len(pool)-y)**2).mean():.4f}")
