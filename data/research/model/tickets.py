"""tickets.py — «поеду X, нужно Y финалов и Z топ-5»: минимальные комбинации результатов до планок сценариев. Финал 4★ (6–10 место) ≈ 12 баллов, топ-5 4★ ≈ 24, 3★: финал ≈ 7, топ-5 ≈ 17."""
import numpy as np, json, itertools, gd_data as g, gd_sim
from gd_sim import Season
T='2026-09-14'; Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
gd_sim.EVENT_WEIGHT={}; gd_sim.TARGET_TOP30_MEAN=None; gd_sim.RACE_BETA_SHIFT=0
se=Season(2026,T,cal_future=fut,verbose=False)
mid=g.standings(2026,T); top=[u for s,u in mid[:34]]
FIN,TOP5=12,24
def finals_min(u):
    out=[]
    for c in se.events:
        if c['type']=='contour' and u in c['fin']:
            n_fin=len(c['fin'])+int(sum(c['cand'].values())); grid=c['grid']
            out.append(((grid[min(n_fin,len(grid))-1] if n_fin<=len(grid) else c['base']), grid[min(len(grid)-1,max(0,n_fin//2-1))], c['name'][:10]))
    return out
def combo(u, target, fin_mode='min'):
    """минимальная (по числу результатов) комбинация Z топ-5 + Y финалов; при равенстве — меньше топ-5"""
    fm=finals_min(u); base=list(se.base[u])+[((lo if fin_mode=='min' else md),1) for lo,md,_ in fm]
    best=None
    for tot in range(0,9):
        for z in range(0,tot+1):
            y=tot-z
            if g.best10(base+[(TOP5,0)]*z+[(FIN,0)]*y)>=target: best=(z,y); break
        if best: break
    return best or (9,9)
def rates(u):
    rows=[r for r in g.L[str(u)]['rp'] if r[2]>='2025-09-14' and not r[5] and r[3] is not None and r[3]<1000]
    n=len(rows); t10=sum(1 for r in rows if r[3]<=10); t5=sum(1 for r in rows if r[3]<=5)
    # сглаживание к топ-30 средним (40% / 20%) с k0=8
    return n, (t10+0.40*8)/(n+8), (t5+0.20*8)/(n+8)
print(f"{'#':>2} {'ник':13s} {'Σ':>4} | {'топ-10%':>7} {'топ-5%':>6} | до 130: топ-5+финал → турниров | до 140 | до 150 | до 160 | финалы(мин/сред)")
rows=[]
for i,u in enumerate(top):
    n,r10,r5=rates(u); s=g.best10(se.base[u]); fm=finals_min(u)
    cells=[]; rec={'uid':u,'nick':g.NICK[u],'rank':i+1,'sigma':s,'n12m':n,'p10':r10,'p5':r5,'finals':[{'name':nm,'min':lo,'mid':md} for lo,md,nm in fm],'need':{}}
    for tgt in (130,140,150,160):
        z,y=combo(u,tgt)
        # сколько турниров: нужно z топ-5 (частота r5) и y финалов-не-топ5 (частота r10-r5): X = max(z/r5, (z+y)/r10) округлённо
        X=int(np.ceil(max(z/max(r5,0.05),(z+y)/max(r10,0.1)))) if (z+y)>0 else 0
        cells.append(f"{z}+{y} → {X:2d}"); rec['need'][tgt]={'top5':z,'final':y,'tournaments':X}
    print(f"{i+1:>2} {g.NICK[u]:13s} {s:4.0f} | {r10*100:6.0f}% {r5*100:5.0f}% | {cells[0]:>12} | {cells[1]:>9} | {cells[2]:>9} | {cells[3]:>9} | {', '.join(f'{nm} {lo:.0f}/{md:.0f}' for lo,md,nm in fm) or '—'}")
    rows.append(rec)
json.dump({'T':T,'FIN':FIN,'TOP5':TOP5,'rows':rows},open('tickets2026.json','w'),ensure_ascii=False,indent=0)
