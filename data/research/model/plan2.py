"""plan2.py · v2 — «план игрока» для топ-30: перцентили мест (со сглаживанием к пулу) × сетка его вероятных турниров × хвост десятки; серийники — диапазоном; планка — из Монте-Карло."""
import numpy as np, json, sys, collections, gd_data as g, gd_sim, calendar_expert
from gd_sim import Season
gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP30_MEAN=4.0
T='2026-09-14'; rng=np.random.default_rng(0)
F=json.load(open('forecast2026.json')); thr=np.array(F['thr'])*1.07   # +7%: бэктест-2025 занижал порог
PL=(np.percentile(thr,25),np.percentile(thr,50),np.percentile(thr,75)); played_exp={r['uid']:r['played'] for r in F['rows']}
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
se=Season(2026,T,cal_future=fut,verbose=False)
regular=[e for e in se.events if e['type']!='contour']; contours=[e for e in se.events if e['type']=='contour']
mid=g.standings(2026,T); rank={u:i+1 for i,(s,u) in enumerate(mid)}
SINCE='2025-09-14'
def pcts(uid):
    out=[]
    for r in g.L[str(uid)]['rp']:
        if r[2]>=SINCE and not r[5] and r[3] is not None and r[3]<1000 and g.EV.get(r[1]) and g.EV[r[1]]['N']:
            out.append((r[3]-0.5)/g.EV[r[1]]['N'])
    return out
REF=[p for s,u in mid[:40] for p in pcts(u)]   # референс: перцентили мест топ-40 гонки
_SM={}
def smoothed(uid, k0=8):
    if uid in _SM: return _SM[uid]
    _SM[uid]=_smoothed(uid,k0); return _SM[uid]
def _smoothed(uid, k0=8):
    """смесь: доля своих результатов n/(n+k0), остальное — референс топ-40 (бета-биномиальная логика: 5 турниров → 38% своих, 17 → 68%)"""
    own=pcts(uid); n=len(own); w=n/(n+k0) if n else 0
    m=200; n_own=int(round(m*w))
    arr=list(rng.choice(own,n_own)) if n_own else []
    arr+=list(rng.choice(REF,m-n_own))
    return np.array(arr), n
def grid_for(e): return se.grid_pts(e['stars'],e['type'],e['N'])
def sim_sigma(uid, base, k, level, S=4000, with_finals=False):
    if with_finals:
        base=list(base)+[(f[5],1) for f in finals_of(uid)]
    P,n=smoothed(uid); P=np.sort(P)
    if level=='хороший': P=P[:max(3,len(P)//2)]
    if level=='мечта': P=P[:max(2,len(P)//4)]
    evs=sorted(regular,key=lambda e:-(e['p'][uid]*(0.15 if e['stars']<=1 else 1.0)))[:k]   # k самых вероятных для него турниров (1★ — в конец: баллов там нет)
    out=[]
    for _ in range(S):
        new=[]
        for e in evs:
            pc=rng.choice(P); pos=int(pc*e['N'])+1; grid=grid_for(e); new.append((grid[min(pos,len(grid))-1],0))
        out.append(g.best10(list(base)+new))
    return np.array(out), evs
def word(sig):
    p=np.mean(sig[:,None]>=thr[None,:1000]); return ('мимо' if p<0.2 else 'на грани' if p<0.45 else 'проходишь' if p<0.75 else 'уверенно'), p
def finals_of(uid):
    out=[]
    for c in contours:
        if uid in c['fin']:
            grid=c['grid']; n_fin=len(c['fin'])+int(sum(c['cand'].values()))
            lo=grid[min(n_fin,len(grid))-1] if n_fin<=len(grid) else c['base']; hi=grid[0]; mid_=grid[min(len(grid)-1,max(0,n_fin//2-1))]
            out.append((c['name'],c['date'],c['stars'],n_fin,lo,mid_,hi))
    return out
rows=[]
print(f"планка дюжины ≈ {PL[1]:.0f} (коридор {PL[0]:.0f}–{PL[2]:.0f})\n")
print(f"{'#':>2} {'ник':14s} {'Σ':>4} {'хвост':>5} {'надо':>5} {'ист.':>4} {'медиана места':>13} {'ожид.турн':>9} | {'как обычно':^18} | {'хороший':^18} | {'мечта':^18} | {'обычно+финалы':^18} | финалы")
for s0,uid in mid[:30]:
    base=g.ledger_recs(uid,2026,T); ten=sorted([p for p,s in base],reverse=True); tail=sum(ten[5:10]) if len(ten)>=10 else 0
    P,n=smoothed(uid); k=int(round(played_exp.get(uid,6)))
    cells=[];detail={}
    for lvl in ('обычно','хороший','мечта'):
        sig,evs=sim_sigma(uid,base,k,lvl); w,p=word(sig); cells.append(f"Σ≈{np.median(sig):3.0f} {w:9s}"); detail[lvl]={'sigma':float(np.median(sig)),'p':float(p),'word':w}
    sigf,_=sim_sigma(uid,base,k,'обычно',with_finals=True); wf,pf=word(sigf); cells.append(f"Σ≈{np.median(sigf):3.0f} {wf:9s}"); detail['обычно+финалы']={'sigma':float(np.median(sigf)),'p':float(pf),'word':wf}
    fins=finals_of(uid); fstr='; '.join(f"{f[0][:12]} {f[4]:.0f}–{f[6]:.0f}" for f in fins) or '—'
    print(f"{rank[uid]:>2} {g.NICK[uid]:14s} {s0:4.0f} {tail:5.0f} {PL[1]-s0:+5.0f} {n:4d} {np.median(pcts(uid))*100 if pcts(uid) else 0:12.0f}% {k:9d} | "+" | ".join(cells)+f" | {fstr}")
    # таблица турниров×уровень для JSON
    table={}
    for kk in (1,2,3,4,5,6,8):
        table[kk]={}
        for lvl in ('обычно','хороший','мечта'):
            sig,evs=sim_sigma(uid,base,kk,lvl,S=1500); w,p=word(sig); table[kk][lvl]={'sigma':float(np.median(sig)),'p10':float(np.percentile(sig,10)),'p90':float(np.percentile(sig,90)),'word':w,'p':float(p)}
    worst=ten[9] if len(ten)>=10 else 0
    rows.append({'uid':uid,'nick':g.NICK[uid],'rank':rank[uid],'sigma':s0,'ten':ten[:10],'tail':tail,'need':float(PL[1]-s0),'hist_n':n,'hist_median_pct':float(np.median(pcts(uid))) if pcts(uid) else None,
                 'expected_k':k,'detail':detail,'finals':[{'name':f[0],'date':f[1],'stars':f[2],'n_fin':f[3],'lo':f[4],'mid':f[5],'hi':f[6]} for f in fins],'table':table,
                 'one_result':{'4★':{pos:se.grid_pts(4,'regular',40)[pos-1]-worst for pos in (1,3,5,10)},'5★':{pos:se.grid_pts(5,'regular',44)[pos-1]-worst for pos in (1,3,5,10)}},
                 'likely_events':[{'id':e['id'],'name':e['name'],'date':e['date'],'stars':e['stars'],'p':round(e['p'][uid],2)} for e in sorted(regular,key=lambda e:-(e['p'][uid]*(0.15 if e['stars']<=1 else 1.0)))[:8]]})
json.dump({'T':T,'planka':{'p25':PL[0],'p50':PL[1],'p75':PL[2]},'rows':rows},open('plan2026.json','w'),ensure_ascii=False,indent=0)
