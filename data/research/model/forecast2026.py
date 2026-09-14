import numpy as np, gd_data as g, gd_sim, json, sys
from gd_sim import Season
T='2026-09-14'; S=int(sys.argv[1]) if len(sys.argv)>1 else 3000
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
se=Season(2026,T,cal_future=fut)
for ev in se.events:
    if ev['type']=='contour': print(f"  контур {ev['id']} {ev['name'][:28]:28s} {ev['date']}: финалистов {len(ev['fin'])} (ожид {sum(ev['fin'].values()):.1f}), кандидатов {len(ev['cand'])} (ожид {sum(ev['cand'].values()):.1f}), сетка до {len(ev['grid'])} мест")
res=se.run(S=S,seed=11,frailty=None)
pool=res['pool']; idx={u:i for i,u in enumerate(pool)}
mid=g.standings(2026,T); midpos={u:i+1 for i,(s,u) in enumerate(mid)}; base={u:s for s,u in mid}
thr=res['thr']
print(f"\n=== ПРОГНОЗ 2026 (срез {T}, {S} симуляций) ===")
print(f"порог дюжины: медиана {np.median(thr):.0f}, 50% коридор {np.percentile(thr,25):.0f}–{np.percentile(thr,75):.0f}, 80% коридор {np.percentile(thr,10):.0f}–{np.percentile(thr,90):.0f}  (бэктест-2025 занижал порог на ~10%)")
order=np.argsort(-res['p12'])
print(f"\n{'#':>3} {'ник':14s} {'Σ сейчас':>8} {'P12':>5} {'P30':>5} {'ожΣ':>5} {'Σ p10–p90':>10} {'турн.':>5} {'+обыч':>5} {'+сер':>5}")
for i in order[:40]:
    u=pool[i]; s=res['sums'][:,i]
    print(f"{midpos.get(u,'-'):>3} {g.NICK[u]:14s} {base.get(u,0):8.0f} {res['p12'][i]*100:4.0f}% {res['p30'][i]*100:4.0f}% {s.mean():5.0f} {np.percentile(s,10):4.0f}–{np.percentile(s,90):<4.0f} {res['played'][i]:5.1f} {res['new_reg'][i]:5.0f} {res['new_ser'][i]:5.0f}")
print('сумма P12 =',res['p12'].sum().round(1))
json.dump({'T':T,'S':S,'thr':thr.tolist(),'rows':[{'uid':pool[i],'nick':g.NICK[pool[i]],'pos':midpos.get(pool[i]),'base':base.get(pool[i],0),'p12':float(res['p12'][i]),'p30':float(res['p30'][i]),'mean':float(res['sums'][:,i].mean()),'p10':float(np.percentile(res['sums'][:,i],10)),'p90':float(np.percentile(res['sums'][:,i],90)),'played':float(res['played'][i]),'new_reg':float(res['new_reg'][i]),'new_ser':float(res['new_ser'][i])} for i in order[:60]]},open('forecast2026.json','w'),ensure_ascii=False)
