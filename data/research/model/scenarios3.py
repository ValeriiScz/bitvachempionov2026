"""scenarios3 · v2.0 · 2026-10-13 — планки гонки: сценарии 0 (только заявки), 1 (обычный ритм), 2 (ездят активно), 3 (по максимуму); различаются только явкой, порог ×1.07 (остаток недооценки на бэктесте 2024/2025)."""
import numpy as np, json, gd_data as g, gd_sim, calendar_expert, players_expert
gd_sim.PLAYER_TARGET=players_expert.TARGET
from gd_cfg import T, out as OUTP
from gd_sim import Season
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
mid=g.standings(2026,T); top=[u for s,u in mid[:30]]
out={}
# v2.0 (13.10.2026): сценарии различаются ТОЛЬКО явкой, без «сдвига силы».
#   Проверка по леджерам: топ-30 гонки после 14.09 играли не лучше, а хуже, чем до (2025: место 32 %→41 % поля, топ-5 38 %→23 %;
#   2024: 35 %→39 %, 35 %→21 %). Порог 12-го растёт от числа стартов и финалов серийников, а не от «заиграли выше головы».
#   Сценарий 0 — «только заявки»: обычные турниры только у уже записанных (+ финалы серийников) → нижняя планка «пол».
for name,k,shift in (('1 обычный ритм',(5.5,4.0),0.0),('2 ездят активно',(6.5,5.0),0.0),('3 ездят по максимуму',(7.5,6.0),0.0)):
    gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP20_MEAN,gd_sim.TARGET_TOP30_MEAN=k; gd_sim.RACE_BETA_SHIFT=shift
    se=Season(2026,T,cal_future=fut,verbose=False); res=se.run(S=2500,seed=5,frailty=None); thr=res['thr']*1.07; pool=res['pool']
    # средняя доля топ-10 у топ-30 при таком сдвиге (для описания сценария)
    order=np.argsort(-res['p12']); groups={'внутри':[g.NICK[pool[i]] for i in order if res['p12'][i]>=0.85],'скорее':[g.NICK[pool[i]] for i in order if 0.55<=res['p12'][i]<0.85],'борьба':[g.NICK[pool[i]] for i in order if 0.2<=res['p12'][i]<0.55]}
    print(f"\n### сценарий {name}: топ-20 ≈ {k[0]}, места 21–30 ≈ {k[1]} турниров, сдвиг силы +{shift}")
    print(f"   планка (с поправкой +7%): медиана {np.median(thr):.0f}, 50% {np.percentile(thr,25):.0f}–{np.percentile(thr,75):.0f}, 80% {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}")
    for kk,v in groups.items(): print(f"   {kk} ({len(v)}): {v}")
    out[name]={'k':k,'shift':shift,'thr_med':float(np.median(thr)),'thr25':float(np.percentile(thr,25)),'thr75':float(np.percentile(thr,75)),'thr10':float(np.percentile(thr,10)),'thr90':float(np.percentile(thr,90)),'groups':groups}
# сценарий 0: только уже записанные (без прогноза явки незаписанных)
gd_sim.EVENT_WEIGHT={}; gd_sim.TARGET_TOP20_MEAN=None; gd_sim.TARGET_TOP30_MEAN=None; gd_sim.RACE_BETA_SHIFT=0; _pt=gd_sim.PLAYER_TARGET; gd_sim.PLAYER_TARGET={}
se=Season(2026,T,cal_future=fut,verbose=False)
for ev in se.events:
    if ev['type']=='contour': continue
    for u in se.pool:
        if ev['regs'].get(u) is None: ev['p'][u]=0.0
    ev['pv']=np.array([ev['p'][u] for u in se.pool])
res=se.run(S=2500,seed=5,frailty=None); thr=res['thr']*1.07
print(f"\n### сценарий 0 только заявки: планка медиана {np.median(thr):.0f}, 80% {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}")
out['0 только заявки']={'k':None,'shift':0,'thr_med':float(np.median(thr)),'thr25':float(np.percentile(thr,25)),'thr75':float(np.percentile(thr,75)),'thr10':float(np.percentile(thr,10)),'thr90':float(np.percentile(thr,90))}
gd_sim.PLAYER_TARGET=_pt
json.dump(out,open(OUTP('scenarios3.json'),'w'),ensure_ascii=False,indent=1)
