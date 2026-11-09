"""whatif.py · v2.2 · 2026-11-09 (крайние сценарии планки — сетка «явка × кто забирает призы»: потолок «ад», максимум явки, топы/гонка/лидеры/чужие берут призы, пол — Валерий) · v2.1 · 2026-11-09 (новые сценарии: DOVOD не едет на Dutch Open; возможный Краков 2★ 21.11 вместо отменённого Вроцлава; оба вместе; стресс — без прошедшего Брюсселя) · v2.0.1 · 2026-11-02 (сценарий Prague Cup: запрещённое слово заменено на «гонка» — правило Валерия 21.10, Глоссарий §5) · v2.0 · 2026-11-02 (после MGP: 13 сценариев по выбору Валерия — явка, Dutch/Кипр/Prague Cup, дуэль Tommy–Сью, исходы финалов GMC и MCL, MCL как 3★) · v1.3 · 2026-10-21 (дюжина: все с шансом ≥5%, до 24; +2 сценария с TOPS; убраны нереалистичные: MGP-отмена, MCL-перенос, 2★ не в зачёт — Валерий) — «Сценарии»: 10 «что если» для гонки за дюжину (Валерий, 21.10).
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
bubble=[u for s_,u in mid[8:16]]
def scen_bubble():
    se=copy.deepcopy(BASE); force(se,bubble,stars_min=4); return se
def scen_all_on(eid):
    def f():
        se=copy.deepcopy(BASE); force(se,top30,ev_ids={eid}); return se
    return f
N=lambda *ns:[uid[n] for n in ns if n in uid]
DUTCH=ev_id('Dutch Open'); PRAGUE=ev_id('Prague Cup')
top20=[u for s_,u in mid[:20]]
GROUP=N('Lюц','Магнат','Tommy','TOPS','Сью','Грешник')
def contour_of(se,pid):
    for ev in se.events:
        if ev['type']=='contour' and ev['id']==pid: return ev
def scen_stress():
    se=copy.deepcopy(BASE); force(se,top20,stars_min=4); return se
def scen_group_prague():
    se=copy.deepcopy(BASE); force(se,GROUP,ev_ids={PRAGUE}); return se
def scen_duel():
    se=copy.deepcopy(BASE); force(se,N('Tommy','Сью'),stars_min=3); return se
def scen_gmc_outsiders():
    se=copy.deepcopy(BASE); contour_of(se,GMC)['race_pen']=8.0; return se
def scen_final_boost(pid,users,val):
    def f():
        se=copy.deepcopy(BASE); ev=contour_of(se,pid)
        for u in users: ev['fin'][u]=1.0
        ev['boost']={u:val for u in users}; return se
    return f
def scen_mcl3():
    se=copy.deepcopy(BASE); ev=contour_of(se,MCL); full=g.SERIAL_GRID_2026[3]; base=float(full[-1])
    ev['stars']=3; ev['grid']=[x for x in full if x>base]; ev['base']=base; return se
def scen_skip(nicks, eid):
    def f():
        se=copy.deepcopy(BASE)
        for ev in se.events:
            if ev['type']!='contour' and ev['id']==eid:
                for u in N(*nicks):
                    ev['regs'].pop(u,None)
                    if u in ev['p']: ev['p'][u]=0.0
        refresh(se); return se
    return f
def scen_extra(extra_ids, then=None):
    def f():
        ex=[e for e in getattr(g,'EXTRA',[]) if e['id'] in extra_ids]
        for e in ex: calendar_expert.W.setdefault(e['id'],0.7)
        se=Season(2026,T,cal_future=fut+ex,verbose=False)
        if then: then(se)
        return se
    return f
def _no_dovod_dutch(se):
    for ev in se.events:
        if ev['type']!='contour' and ev['id']==DUTCH:
            for u in N('DOVOD'):
                ev['regs'].pop(u,None)
                if u in ev['p']: ev['p'][u]=0.0
    refresh(se)
KRAKOW2=99021

# v2.2 крайние сценарии: две оси — явка (только записанные / как сейчас / топ-24 на всё) × кто забирает призы.
# «Забирает призы» = сдвиг силы группы на ±EDGE (сила топов ≈1.0, фон ≈−0.1, шум мест — Гумбель sd 1.28).
EDGE=1.0
LEAD8=[u for s_,u in mid[:8]]; RACE9=[u for s_,u in mid[8:24]]; TOP24=[u for s_,u in mid[:24]]
MAXEV={DUTCH,PRAGUE,CYPRUS_W}   # по одному лучшему турниру на дату: 28.11 Dutch 4★, 5.12 Prague 3★, 12.12 Кипр 4★
def shift(se,users,d):
    for u in users: se.beta[u]=se.beta.get(u,se.default)+d
def scen_grid(att,who,d):
    def f():
        se=copy.deepcopy(BASE)
        if att=='regs':
            for ev in se.events:
                if ev['type']=='contour': continue
                for u in se.pool:
                    if ev['regs'].get(u) is None: ev['p'][u]=0.0
            refresh(se)
        elif att=='max': force(se,TOP24,ev_ids=MAXEV)
        if who: shift(se,who,d)
        return se
    return f
SCEN=[
 ('base','Как сейчас','Обычный ритм: записанные едут по срокам, остальные дозаписываются как в 2024–25. GMC — по фактическим заявкам (Gangster выписался).',base_season),
 ('x_max_all','Ад: топ-24 едут на всё и забирают призы','Потолок планки. Все из топ-24 играют Dutch Open, Prague Cup и Кипр-зиму, и все они — и лидеры, и те, кто бьётся за места, — играют на пике и забирают призы, в том числе в финалах GMC и MCL.',scen_grid('max',TOP24,EDGE)),
 ('x_hell','Топ-24 на всё, гонка берёт призы','Все из топ-24 играют Dutch Open, Prague Cup и Кипр-зиму; игроки с 9-го по 24-е место гонки играют на пике и забирают призы (в том числе в финалах GMC и MCL).',scen_grid('max',RACE9,EDGE)),
 ('x_max','Топ-24 на всё, силы как есть','Максимальная явка: топ-24 едут на Dutch Open, Prague Cup и Кипр-зиму; результаты — по обычной силе.',scen_grid('max',None,0)),
 ('x_race','Обычная явка, гонка берёт призы','Явка как сейчас; игроки с 9-го по 24-е место гонки забирают призы.',scen_grid('base',RACE9,EDGE)),
 ('x_lead','Обычная явка, лидеры берут призы','Явка как сейчас; призы забирают первые восемь гонки, которым баллы почти не нужны.',scen_grid('base',LEAD8,EDGE)),
 ('x_out','Обычная явка, призы берут чужие','Явка как сейчас; все из топ-24 играют ниже своей силы, призы уходят игрокам вне гонки.',scen_grid('base',TOP24,-EDGE)),
 ('x_regs_race','Только записанные, гонка берёт призы','Новых заявок нет, но те, кто бьётся за места, забирают призы.',scen_grid('regs',RACE9,EDGE)),
 ('x_floor','Пол: только записанные, призы берут чужие','Нижняя граница планки. Новых заявок нет, топ-24 играют ниже своей силы, призы — игрокам вне гонки.',scen_grid('regs',TOP24,-EDGE)),
 ('regs','Никто больше не записывается','Играют только те, кто уже записан (с поправкой на срок), плюс финалы серийников.',scen_only_regs),
 ('nodutch_dovod','DOVOD не едет на Dutch Open','Всё как сейчас, но DOVOD снимается с Four Seasons: Dutch Open (28.11, 4★).',scen_skip(['DOVOD'],DUTCH)),
 ('krakow2','Краков 2★ 21.11 вместо Вроцлава','Вроцлав (3★) отменён; вместо него, возможно, будет турнир в Кракове на 2★. Явка — по обычной модели для Польши.',scen_extra({KRAKOW2})),
 ('krakow2_nodutch','Краков 2★ + DOVOD без Dutch Open','Оба условия сразу: в календаре появляется Краков 2★ (21.11), DOVOD не едет в Амстердам.',scen_extra({KRAKOW2},_no_dovod_dutch)),
 ('stress','Топ-20 едут на все 4★','Стресс-тест планки: двадцать лучших гонки играют Dutch Open и Кипр-зиму.',scen_stress),
 ('dutch','Весь топ-30 на Dutch Open 28.11','Four Seasons: Dutch Open (4★, Нидерланды) — все из топ-30 гонки едут.',scen_all_on(DUTCH)),
 ('cyp','Весь топ-30 на Кипр-зиму 12.12','Four Seasons Cyprus Open: Winter (4★) — все из топ-30 гонки едут.',scen_all_on(CYPRUS_W)),
 ('prague','Гонка едет на Prague Cup 5.12','Lюц, Магнат, Tommy, TOPS, Сью и Грешник — шестеро, кто бьётся за последние места дюжины, — играют Prague Cup (3★).',scen_group_prague),
 ('duel','Tommy и Сью едут на всё','Оба записываются на каждый оставшийся турнир 3★ и выше.',scen_duel),
 ('gmc','GMC: топ-10 — все не из гонки','В финале GMC (14.11) первые места забирают игроки вне топ-40 гонки; игрокам гонки остаются места с 11-го.',scen_gmc_outsiders),
 ('gmc_tommy','GMC: Tommy в топ-3','Tommy играет финал GMC и берёт медаль.',scen_final_boost(GMC,N('Tommy'),6.0)),
 ('gmc_gresh','GMC: Грешник в топ-3','Грешник играет финал GMC и берёт медаль.',scen_final_boost(GMC,N('Грешник'),6.0)),
 ('mcl_tops','MCL: TOPS выигрывает','Финал MCL Europe (21.11) — победа TOPS.',scen_final_boost(MCL,N('TOPS'),100.0)),
 ('mcl_low','MCL: KEX и Грешник вне топ-5','KEX и Грешник играют финал MCL, но остаются внизу таблицы.',scen_final_boost(MCL,N('KEX','Грешник'),-100.0)),
 ('mcl3','MCL — трёхзвёздочный','Финал MCL Europe идёт в зачёт как 3★ (30/27/25…), а не 4★ (40/37/35…).',scen_mcl3),
]
out=[]; base=None
import os
ONLY=set(filter(None,os.environ.get('WHATIF_ONLY','').split(',')))
for key,title,desc,fn in SCEN:
    if ONLY and key not in ONLY and key!='base': continue
    se=fn(); r=run(se)
    if base is None: base=r
    top=sorted(r['p12'].items(),key=lambda x:-x[1])
    dozen=[{'nick':g.NICK[u],'uid':u,'rank':rank.get(u),'p12':round(p,3),'ex':round(r['ex'][u],1)} for i,(u,p) in enumerate(top) if i<16 or (p>=0.05 and i<24)]
    moves=[]
    for u in set(list(r['p12'])):
        d=r['p12'][u]-base['p12'].get(u,0)
        if abs(d)>=0.08 and (r['p12'][u]>=0.15 or base['p12'].get(u,0)>=0.15): moves.append({'nick':g.NICK[u],'uid':u,'d':round(d,3),'p12':round(r['p12'][u],3),'p0':round(base['p12'].get(u,0),3)})
    moves.sort(key=lambda m:-abs(m['d']))
    out.append({'key':key,'title':title,'desc':desc,'thr':round(r['thr'],1),'thr10':round(r['thr10'],1),'thr90':round(r['thr90'],1),'dozen':dozen,'moves':moves[:8]})
    dv=uid.get('DOVOD'); print(f"   DOVOD p12 {r['p12'].get(dv,0):.3f} ex {r['ex'].get(dv,0):.1f} | thr10–90 {r['thr10']*1.07:.0f}–{r['thr90']*1.07:.0f}")
    print(f"{title:38s} планка {r['thr']:.0f} (×1.07 {r['thr']*1.07:.0f}) | дюжина: {', '.join(d['nick'] for d in dozen[:12])} | сдвиги: {', '.join(m['nick']+f'{m[chr(100)]:+.2f}' for m in moves[:5])}")
if not ONLY: json.dump({'T':T,'S':S,'scen':out},open(OUTP('whatif.json'),'w'),ensure_ascii=False)
