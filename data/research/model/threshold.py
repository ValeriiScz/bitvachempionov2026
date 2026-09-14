import numpy as np, json, gd_data as g, gd_sim, calendar_expert
from gd_sim import Season
T='2026-09-14'; Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
mid=g.standings(2026,T); top=[u for s,u in mid[:30]]; nick=lambda u:g.NICK[u]
uidof={g.NICK[int(u)]:int(u) for u in g.L}
def build(target, weights=True, only_regs=False, overrides=None):
    gd_sim.EVENT_WEIGHT=calendar_expert.W if weights else {}; gd_sim.TARGET_TOP30_MEAN=target
    se=Season(2026,T,cal_future=fut,verbose=False)
    regs=[e for e in se.events if e['type']!='contour']
    if only_regs:
        for e in regs:
            for u in se.pool:
                f=e['regs'].get(u); e['p'][u]=0.95 if f==1 else 0.7 if f==0 else 0.0
    if overrides:   # {uid: k} — масштабируем p игрока так, чтобы ожидаемое число турниров = k (заявки не трогаем)
        for u,k in overrides.items():
            fixed=sum(e['p'][u] for e in regs if e['regs'].get(u) is not None); free=[e for e in regs if e['regs'].get(u) is None]
            cur=sum(e['p'][u] for e in free); need=max(0,k-fixed)
            sc=need/cur if cur>0 else 0
            for e in free: e['p'][u]=min(0.97,e['p'][u]*sc)
    for e in regs: e['pv']=np.array([e['p'][u] for u in se.pool])
    return se
def report(name, se, S=2500):
    res=se.run(S=S,seed=3,frailty=None); thr=res['thr']; pool=res['pool']
    k30=np.mean([res['played'][pool.index(u)] for u in top])
    order=np.argsort(-res['p12']); sure=[nick(pool[i]) for i in order if res['p12'][i]>=0.9]; likely=[nick(pool[i]) for i in order if 0.6<=res['p12'][i]<0.9]; fight=[nick(pool[i]) for i in order if 0.25<=res['p12'][i]<0.6]
    print(f"\n### {name}: топ-30 играют в среднем {k30:.1f} обычных турниров")
    print(f"  порог 12-го: медиана {np.median(thr):.0f}, 50% {np.percentile(thr,25):.0f}–{np.percentile(thr,75):.0f}, 80% {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}   (без поправки на занижение)")
    print(f"  почти наверняка внутри ({len(sure)}): {sure}")
    print(f"  скорее внутри ({len(likely)}): {likely}")
    print(f"  в борьбе ({len(fight)}): {fight}")
    return res
print('текущая таблица: ', [(i+1,nick(u),int(s)) for i,(s,u) in enumerate(mid[:16])])
r0=report('S0 — играют ТОЛЬКО уже заявленные (+ финалы серийников)', build(None,only_regs=True))
r1=report('S1 — заявки + очень скромный добор (топ-30 ≈ 2 турнира)', build(2.0))
r2=report('S2 — заявки + добор (топ-30 ≈ 3 турнира)', build(3.0))
ov={uidof[n]:k for n,k in (('DOVOD',5.5),('Саботаж',0),('RAMZES',3),('Сью',3.5),('Flame',2),('ParadoXx',5),('KEX',3),('YeS',3),('LogisticPro',3),('Магнат',5))}
rv=report('SV — сценарий Валерия (база 3, поимённо: DOVOD 5.5, Саботаж 0, RAMZES 3, Сью 3.5, Flame 2, ParadoXx 5, KEX/YeS/LP 3, Магнат 5)', build(3.0,overrides=ov))
r3=report('S3 — модель с календарём (топ-30 ≈ 4 турнира)', build(4.0))
