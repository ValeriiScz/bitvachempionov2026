import numpy as np, json, gd_data as g, gd_sim, calendar_expert, players_expert
gd_sim.PLAYER_TARGET=players_expert.TARGET
from gd_cfg import T, out as OUTP
from gd_sim import Season
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
mid=g.standings(2026,T); top=[u for s,u in mid[:30]]
out={}
for name,k,shift in (('1 обычный ритм',(5.5,4.0),0.0),('2 активно и стараются',(6.0,5.0),0.35),('3 как звери',(6.5,6.0),0.7)):
    gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP20_MEAN,gd_sim.TARGET_TOP30_MEAN=k; gd_sim.RACE_BETA_SHIFT=shift
    se=Season(2026,T,cal_future=fut,verbose=False); res=se.run(S=2500,seed=5,frailty=None); thr=res['thr']*1.07; pool=res['pool']
    # средняя доля топ-10 у топ-30 при таком сдвиге (для описания сценария)
    order=np.argsort(-res['p12']); groups={'внутри':[g.NICK[pool[i]] for i in order if res['p12'][i]>=0.85],'скорее':[g.NICK[pool[i]] for i in order if 0.55<=res['p12'][i]<0.85],'борьба':[g.NICK[pool[i]] for i in order if 0.2<=res['p12'][i]<0.55]}
    print(f"\n### сценарий {name}: топ-20 ≈ {k[0]}, места 21–30 ≈ {k[1]} турниров, сдвиг силы +{shift}")
    print(f"   планка (с поправкой +7%): медиана {np.median(thr):.0f}, 50% {np.percentile(thr,25):.0f}–{np.percentile(thr,75):.0f}, 80% {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}")
    for kk,v in groups.items(): print(f"   {kk} ({len(v)}): {v}")
    out[name]={'k':k,'shift':shift,'thr_med':float(np.median(thr)),'thr25':float(np.percentile(thr,25)),'thr75':float(np.percentile(thr,75)),'thr10':float(np.percentile(thr,10)),'thr90':float(np.percentile(thr,90)),'groups':groups}
json.dump(out,open(OUTP('scenarios3.json'),'w'),ensure_ascii=False,indent=1)
