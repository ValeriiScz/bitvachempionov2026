"""whatif.py · v1.0 · 2026-10-21 — «Сценарии»: 10 «что если» для гонки за дюжину (Валерий, 21.10).
Каждый сценарий — та же модель (gd_sim + gd_strength2), в которой меняется одно условие: отменён турнир, все записались,
финал сыгран без игроков гонки и т. п. На выходе для каждого: планка 12-го (сырая и ×1.07), состав дюжины словами,
кто заходит/выпадает по сравнению с базой. Пишет OUTP('whatif.json'); build_race.py кладёт его в RACE.whatif.
Запуск: из data/research/model, GD_T=… python3 whatif.py"""
import numpy as np, json, copy, gd_data as g, gd_sim, gd_strength2, calendar_expert, players_expert
from gd_cfg import T, out as OUTP
from gd_sim import Season
gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP30_MEAN=4.0; gd_sim.TARGET_TOP20_MEAN=5.5; gd_sim.PLAYER_TARGET=players_expert.TARGET
Season.FINALISTS_PLAY=True
S=1200
uid={v['nick']:int(u) for u,v in g.L.items()}
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
def ev_id(name_part, kind=None):
    for t in fut:
        if name_part.lower() in t['name'].lower() and (kind is None or t['kind']==kind): return t['id']
    return None
BRUSSELS=ev_id('Black circle'); CYPRUS_W=ev_id('Cyprus Open 26'); MGP=ev_id('Mediterranean'); GMC=664; MCL=757
FIN2=[645,685,670,749,740]
def base_season(): return Season(2026,T,cal_future=fut,verbose=False)
BASE=base_season()
mid=g.standings(2026,T); rank={u:i+1 for i,(s,u) in enumerate(mid)}; top30=[u for s,u in mid[:30]]
def refresh(se):
    for ev in se.events:
        if ev['type']!='contour': ev['pv']=np.array([ev['p'][u] for u in se.pool]); ev['unreg']=np.array([ev['regs'].get(u) is None for u in se.pool])
def force(se, users, ev_ids=None, stars_min=None, p=0.95):
    for ev in se.events:
        if ev['type']=='contour': continue
        if (ev_ids and ev['id'] in ev_ids) or (stars_min and ev['stars']>=stars_min):
            for u in users:
                if u in ev['p']: ev['p'][u]=p; ev['regs'][u]=1
    refresh(se)
def drop(se, ids): se.events=[e for e in se.events if e['id'] not in set(ids)]
def run(se):
    r=se.run(S=S,seed=7,frailty=None); thr=r['thr']; pool=r['pool']
    p12={pool[i]:float(r['p12'][i]) for i in range(len(pool))}; ex={pool[i]:float(r['sums'][:,i].mean()) for i in range(len(pool))}
    return {'thr':float(np.median(thr)),'thr10':float(np.percentile(thr,10)),'thr90':float(np.percentile(thr,90)),'p12':p12,'ex':ex}
def scen_only_regs():
    se=copy.deepcopy(BASE)
    for ev in se.events:
        if ev['type']=='contour': continue
        for u in se.pool:
            if ev['regs'].get(u) is None: ev['p'][u]=0.0
    refresh(se); return se
def scen_all_cyprus():
    se=copy.deepcopy(BASE); force(se,top30,ev_ids={CYPRUS_W}); return se
def scen_drop(ids):
    def f():
        se=copy.deepcopy(BASE); drop(se,ids); return se
    return f
def scen_gmc_outsiders():
    se=copy.deepcopy(BASE)
    for ev in se.events:
        if ev['id']==GMC and ev['type']=='contour': ev['race_pen']=8.0
    return se
def scen_flash_tommy():
    se=copy.deepcopy(BASE); force(se,[uid.get('Flash'),uid.get('Tommy')],stars_min=4); return se
def scen_leaders_rest():
    se=copy.deepcopy(BASE)
    L=[uid.get(n) for n in ('YeS','Tripok','LogisticPro')]
    for ev in se.events:
        if ev['type']=='contour': continue
        for u in L:
            if u in ev['p']: ev['p'][u]=0.0; ev['regs'].pop(u,None)
    refresh(se); return se
def scen_form():
    old=gd_strength2.RHO_FORM; gd_strength2.RHO_FORM=1.0
    try: se=base_season()
    finally: gd_strength2.RHO_FORM=old
    return se
SCEN=[
 ('base','Как сейчас','Обычный ритм: записанные едут по срокам, остальные дозаписываются как в 2024–25; финалы серийников играют все, кто прошёл.',lambda: copy.deepcopy(BASE)),
 ('regs','Никто больше не записывается','Играют только те, кто уже записан (с поправкой на срок), плюс финалы серийников.',scen_only_regs),
 ('cyp','Весь топ-30 едет на Кипр 12.12','Four Seasons Cyprus Open: Winter (4★) — все из топ-30 гонки записываются и едут.',scen_all_cyprus),
 ('bru','Брюссель 07.11 отменён','Four Seasons: Black circle (4★, Бельгия) не состоялся.',scen_drop([BRUSSELS])),
 ('mgp','Mediterranean 31.10 отменён','Mediterranean Grand-Prix (5★, Кипр) — самый крупный турнир осени — не состоялся.',scen_drop([MGP])),
 ('cypx','Кипр-зима 12.12 отменён','Four Seasons Cyprus Open: Winter (4★) не состоялся.',scen_drop([CYPRUS_W])),
 ('gmc','GMC: топ-10 — все не из гонки','В финале GMC (14.11) первые места забирают игроки вне топ-40 гонки; игрокам гонки остаются места с 11-го.',scen_gmc_outsiders),
 ('mcl','MCL-финал перенесён на 2027','Финал MCL Europe (21.11, 4★, 10 финалистов) в сезон 2026 не идёт.',scen_drop([MCL])),
 ('fin2','Финалы 2★ не в зачёт','White Mafia, Arena Moldova, Васлуй, ЛЗГ и Benelux не дают баллов в 2026.',scen_drop(FIN2)),
 ('ft','Flash и Tommy едут на все 4–5★','Оба записываются на каждый оставшийся турнир 4–5★.',scen_flash_tommy),
 ('rest','Лидеры отдыхают','YeS, Tripok и LogisticPro больше не играют обычные турниры (финалы серийников — играют).',scen_leaders_rest),
 ('form','Форма важнее истории','Сезон 2026 переносится вперёд целиком (а не наполовину): кто в форме — сильнее, кто просел — слабее.',scen_form),
]
out=[]; base=None
for key,title,desc,fn in SCEN:
    se=fn(); r=run(se)
    if base is None: base=r
    top=sorted(r['p12'].items(),key=lambda x:-x[1])
    dozen=[{'nick':g.NICK[u],'uid':u,'rank':rank.get(u),'p12':round(p,3),'ex':round(r['ex'][u],1)} for u,p in top[:16]]
    moves=[]
    for u in set(list(r['p12'])):
        d=r['p12'][u]-base['p12'].get(u,0)
        if abs(d)>=0.08 and (r['p12'][u]>=0.15 or base['p12'].get(u,0)>=0.15): moves.append({'nick':g.NICK[u],'uid':u,'d':round(d,3),'p12':round(r['p12'][u],3),'p0':round(base['p12'].get(u,0),3)})
    moves.sort(key=lambda m:-abs(m['d']))
    out.append({'key':key,'title':title,'desc':desc,'thr':round(r['thr'],1),'thr10':round(r['thr10'],1),'thr90':round(r['thr90'],1),'dozen':dozen,'moves':moves[:8]})
    print(f"{title:38s} планка {r['thr']:.0f} (×1.07 {r['thr']*1.07:.0f}) | дюжина: {', '.join(d['nick'] for d in dozen[:12])} | сдвиги: {', '.join(m['nick']+f'{m[chr(100)]:+.2f}' for m in moves[:5])}")
json.dump({'T':T,'S':S,'scen':out},open(OUTP('whatif.json'),'w'),ensure_ascii=False)
