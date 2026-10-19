"""bt_v2.py · 2026-10-19 — бэктест дюжины v1 против v2 (срез 14.09 → факт 31.12) на 2024 и 2025. python3 bt_v2.py [S=1500]"""
import sys, numpy as np, gd_data as g, gd_sim
S=int(sys.argv[1]) if len(sys.argv)>1 else 1500
def run(year, strength, sigma=True, C=1.4, rho=None):
    gd_sim.STRENGTH=strength; gd_sim.STRENGTH_SIGMA=sigma; gd_sim.C=C
    import gd_strength2 as s2
    if rho is not None: s2.RHO_FORM=rho
    from gd_sim import Season
    T=f'{year}-09-14'; se=Season(year,T,verbose=False); res=se.run(S=S,seed=1,frailty=2.0)
    fin=g.standings(year); fin12=[u for s,u in fin[:12]]; pool=res['pool']
    order=np.argsort(-res['p12']); hit=len(set(pool[i] for i in order[:12])&set(fin12))
    y=np.array([1 if u in fin12 else 0 for u in pool]); br=((res['p12']-y)**2).mean()
    ll=np.mean([np.log(max(res['p12'][pool.index(u)],1e-3)) for u in fin12])
    thr=np.median(res['thr'])
    return dict(hit=hit,brier=br,logp=ll,thr=thr,fact=fin[11][0],res=res,pool=pool,fin12=fin12)
for year in (2025,2024):
    print(f'\n=== {year}')
    for name,kw in (('v1',dict(strength='v1')),('v2 без σ',dict(strength='v2',sigma=False)),('v2 с σ',dict(strength='v2')),('v2 с σ, ρ=0.5',dict(strength='v2',rho=0.5)),('v2 с σ, C=1.2',dict(strength='v2',C=1.2,rho=1.0))):
        r=run(year,**kw)
        print(f"  {name:16s} попаданий {r['hit']}/12  Brier {r['brier']:.4f}  logP дюжины {r['logp']:.2f}  порог {r['thr']:.0f} (факт {r['fact']:.0f})")
