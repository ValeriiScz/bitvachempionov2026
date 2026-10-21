"""gd_sim · v2.4 · 2026-10-20 (финалы серийников: поле добирается до объявленного размера заменяющими из серий/фоном; GMC-финал 40 человек; заменяющие получают баллы по месту) · v2.2 · 2026-10-20 (явка v2: статус заявки × дни до старта по истории календаря 26.08–19.10 (подтверждён 0.97/0.92/0.82/0.62, заявка 1.0/1.0/0.88/0.75, НЕ записан 0.00/0.01/0.04/0.10 по горизонтам ≤7/≤14/≤28/29+ дней); для незаписанных — модельная p, сжатая к этим уровням; петля R1 внутри розыгрыша: незаписанный турнир с горизонтом 15+ дней — p ×1.6 если игрок по ходу сезона в 25 баллах от планки, ×0.6 если дальше 55 (ГИПОТЕЗА); нормировка TARGET_* отключается при LEAD_RULE) · v2.1 · 2026-10-20 (C 1.4→1.0 по калибровке верха: модель завышала долю топ-5 у топ-40 в 1,5 раза — calib_top5.py) · v2.0 · 2026-10-19 (сила v2: gd_strength2 — ELO-prior, усадка по числу турниров, σ силы тянется в каждом розыгрыше, форма сезона; один турнир в день на игрока; фильтр «Отмена» в названии; переключатель STRENGTH) · v1.4 · 2026-10-13 (финалы серийников 2026 — сетка федерации) · v1.3 · 2026-10-13 (калибровка C=1.4, RACE_BOOST=1.5 по бэктесту 2024+2025; явка со «свежим темпом» gd_attend v1.1) · v1.2 · 2026-09-21 (TARGET_TOP20_MEAN: явка топ-20 отдельно) · v1.1 (финалы серийников: 10 призовых мест у 2★, поле финала 20, GMC 17 мест; PLAYER_TARGET — планы игроков) · v1.0 · 2026-09-14 — Монте-Карло остатка сезона mafgame: явка × сила (Plackett-Luce) × сетка баллов × серийники → Σ=best10(≤2 serial) → топ-12."""
import numpy as np, datetime, collections
import gd_data as g
from gd_strength import rankings_before, fit_pl
from gd_attend import Attend

LAM, C = 0.1, 1.0
STRENGTH='v2'     # 'v1' — старый PL с L2 к нулю; 'v2' — gd_strength2 (ELO-prior + σ + форма)
STRENGTH_SIGMA=True   # v2: тянуть силу из N(β,σ²) в каждом розыгрыше (неопределённость оценки)
# v1.3 (13.10.2026): C 1.1→1.4 и RACE_BOOST 1.0→1.5 — подобраны бэктестом с 14.09 на 2024 и 2025 (bt_calibrate.py):
#   явка топ-30 осенью у модели была 2.8/3.4 старта против факта 4.0/4.2 (−30/−20 %), порог 12-го занижен на 15/10 %.
#   После калибровки: старты 3.9/4.1, порог 106/134 при факте 113/144 (остаток ≈7 % закрывает поправка ×1.07 в сценариях),
#   Brier дюжины 0.0337→0.0321 (2024) и 0.0175→0.0152 (2025), угадано 9→9 и 9→11 из 12.
RACE_BOOST = 1.5   # калибровочный множитель явки для мест 1–25 гонки (подобран на бэктесте 2024+2025)
# сетки финалов серийников — FACT по финалам 2025 (леджер): 2★ — баллы только у 10 мест (PSP-2025: 12 мест, 8 и 6), остальные финалисты — база 2;
# 4★ GMC-2025: 17 мест 42…8, остальные база 4; MCL — 10 финалистов, все с баллами. Заменяющие (не прошедшие с серии) — только база.
GRID_2S=[30,27,25,22,20,18,16,14,12,10]
GRID_2S_12=[30,27,25,22,20,18,16,14,12,10,8,6]
GRID_4S=[42,39,37,34,32,30,28,26,24,22,20,18,16,14,12,10,8]
# v1.4 (13.10.2026): сезон 2026 — официальная сетка финалов серийников от федерации (gd_data.SERIAL_GRID_2026); сетки выше — для бэктестов 2024/2025
GRID26={k:v for k,v in g.SERIAL_GRID_2026.items()}
# размер поля финала (Валерий 21.09: у 2★ финалы на 20 человек, кроме польского (12) и MCL (10)); GMC 50–60
FINAL_SIZE={664:40,277:30,757:10,259:10,639:12,251:12,740:10,279:10}
FINAL_SIZE_2S=20
PLAYER_TARGET={}   # uid → ожидаемое число обычных турниров до конца года (players_expert.py); поверх TARGET_TOP30_MEAN
RULES={664:'top2',277:'top2',757:'mcl',259:'mcl',639:'top2',251:'top2',645:'top2',685:'top1mvp',478:'top1mvp',740:'sum2',279:'sum2',749:'top2',530:'top2',670:'top2',509:'top2',579:'top2',132:'top2',694:'top2'}
IL={'Ramat Gan','Haifa'}; CY={'Limassol'}

def cand_from_future(future):
    out=set()
    for s in future:
        us=[r[0] for r in s['rows']] if s['rows'] else [r[0] for r in s['regs']]
        out|=set(us)
    return out

# экспертный календарь явки (Валерий, 14.09.2026): множитель привлекательности турнира поверх модели.
# 1.5 = «все поедут», 1.0 = обычный, 0.5 = «маловероятно соберётся», 0.3 = «туда не едут»
EVENT_WEIGHT={}
TARGET_TOP30_MEAN=None   # среднее число обычных турниров до конца года у мест 21–30 гонки
TARGET_TOP20_MEAN=None   # то же для мест 1–20 (Валерий 21.09: «у топ-20 явка будет под 5–6, реалистично»); None → как топ-30
LEAD_RULE=True   # v2.2: явка по заявкам и срокам (см. шапку); False — старая нормировка TARGET_*
LEAD_CONF={7:0.97,14:0.92,28:0.82,999:0.62}; LEAD_APP={7:1.0,14:1.0,28:0.88,999:0.75}; LEAD_NONE={14:0.01,28:0.04,999:0.10}   # FACT: история календаря, 11 турниров, топ-40
LEAD_NONE_MULT=1.0   # сценарии планки: множитель к уровню явки незаписанных (1 / 1.5 / 2.5)
R1_NEAR,R1_FAR,R1_UP,R1_DOWN,R1_MINLEAD=25,55,1.6,0.6,15   # ГИПОТЕЗА: петля «близко к планке → едет чаще» для незаписанных турниров
THR_REF=None   # ориентир планки для петли R1 (баллы); None → 1.3 × текущая Σ 12-го
RACE_BETA_SHIFT=0.0   # сценарии «стараются»/«звери»: сдвиг силы топ-30 относительно фона   # если задано — явка масштабируется так, чтобы у топ-30 гонки среднее число обычных турниров = это

class Season:
    def __init__(self, year, T, cal_future=None, verbose=True, att_T=None):
        self.year, self.T = year, T
        # пул: игроки леджера, у которых есть хоть одна запись до T (иначе на дату T их в гонке не существовало)
        self.pool=[int(u) for u in g.L if any(r[2]<T for r in g.L[u]['rp'])]
        # сила
        if STRENGTH=='v2':
            import gd_strength2 as s2
            self.strength=s2.Strength(T,year)
            self.beta={u:self.strength.fwd(u) for u in self.strength.beta}; self.sigma={u:self.strength.sd(u) for u in self.strength.beta}
            self.default=self.strength.default; self.default_sigma=self.strength.default_sigma
        else:
            self.beta=fit_pl(rankings_before(T), lam=LAM); self.sigma={}; self.default_sigma=0.0
            vals=np.array(list(self.beta.values())); self.default=float(np.percentile(vals,30))
        poolset=set(self.pool)
        self.bg=np.array([b for u,b in self.beta.items() if u not in poolset]+[self.default]*int(0.6*len(self.beta)))
        # явка
        self.att=Attend(self.pool,att_T or T,g.COUNTRY)
        if att_T: self.att.rate,self.att.n_ev,self.att.byc=__import__('gd_attend').player_rates(self.pool,T)
        # база леджера до T и место в гонке на T
        self.base={u:g.ledger_recs(u,year,T) for u in self.pool}
        self.race={u:i+1 for i,(s,u) in enumerate(g.standings(year,T))}
        # сетки баллов
        self.grids=collections.defaultdict(list)
        for e in g.EV.values():
            if e['N'] and e['kind']!='serial_final' and e['date']<T:
                rows=sorted([r for r in e['rows'] if r[2] and r[2]<1000],key=lambda r:r[2])
                if rows: self.grids[(e['stars'],e['kind'])].append((len(rows),[r[3] for r in rows]))
        # будущие события
        self.events=[]
        if cal_future is None:   # бэктест: фактические турниры года после T
            for e in g.EV.values():
                if e['year']==year and e['date']>=T and e['date']<f'{year+1}-01-01':
                    if e['kind']=='serial_final': self.events.append(self.contour(e['id'],e['stars'],e['date'],e['name']))
                    elif e['N']: self.events.append({'type':e['kind'],'id':e['id'],'date':e['date'],'stars':e['stars'],'country':e['country'],'N':e['N'],'name':e['name'],'regs':{}})
        else:
            for t in cal_future:
                if t['name'].strip().lower().startswith('отмена'): continue   # v2.0: календарь иногда пишет «Отмена …» в названии без флага cancelled
                if t['kind']=='serial_final': self.events.append(self.contour(t['id'],t['stars'],t['start'],t['name']))
                else:
                    regs={u:f for u,n,f in t['regs']}
                    self.events.append({'type':t['kind'],'id':t['id'],'date':t['start'],'stars':t['stars'],'country':t['country'],'N':t['exp'] or 30,'name':t['name'],'regs':regs})
        self.events.sort(key=lambda e:(e['date'],-e['stars']))   # в один день — сначала крупнее: игрок играет один турнир в день
        # p явки для regular/teams
        for ev in self.events:
            if ev['type']=='contour': continue
            fake={'year':year,'date':ev['date'],'country':ev['country'],'stars':ev['stars'],'kind':ev['type']}
            p={}
            for u in self.pool:
                pu=self.att.p(u,fake)
                if self.race.get(u,999)<=25: pu=min(0.97,pu*RACE_BOOST)
                f=ev['regs'].get(u)
                if f==1: pu=max(pu,0.9)
                elif f==0: pu=max(pu,0.6)
                p[u]=pu
            ev['p']=p; ev['pv']=np.array([p[u] for u in self.pool])
        # экспертные веса турниров + нормировка на целевую явку топ-30
        regs=[ev for ev in self.events if ev['type']!='contour']
        for ev in regs:
            a=EVENT_WEIGHT.get(ev['id'],1.0)
            for u in self.pool:
                f=ev['regs'].get(u)
                if f is None: ev['p'][u]=min(0.97,ev['p'][u]*a)
        if TARGET_TOP30_MEAN and not (LEAD_RULE and cal_future is not None):
            ps=set(self.pool)
            groups=[([u for u,r in self.race.items() if r<=20 and u in ps], TARGET_TOP20_MEAN or TARGET_TOP30_MEAN),
                    ([u for u,r in self.race.items() if 20<r<=30 and u in ps], TARGET_TOP30_MEAN)]
            # общий множитель считаем по топ-30, а для мест 1–20 — свой, если задан TARGET_TOP20_MEAN
            top=[u for u,r in self.race.items() if r<=30 and u in ps]
            k_all=TARGET_TOP30_MEAN/max(1e-9,sum(ev['p'][u] for ev in regs for u in top)/max(1,len(top)))
            for ev in regs:
                for u in self.pool:
                    if ev['regs'].get(u) is None: ev['p'][u]=min(0.97,ev['p'][u]*k_all)
            for grp,target in groups:
                if not grp or not target: continue
                for _ in range(4):
                    cur=sum(ev['p'][u] for ev in regs for u in grp)/len(grp)
                    if cur<=0: break
                    k=target/cur
                    for ev in regs:
                        for u in grp:
                            if ev['regs'].get(u) is None: ev['p'][u]=min(0.97,ev['p'][u]*k)
        # планы конкретных игроков (players_expert): подгоняем сумму p по обычным турнирам к сказанному числу
        poolset2=set(self.pool)
        for u,target in PLAYER_TARGET.items():
            if u not in poolset2: continue
            for _ in range(4):
                cur=sum(ev['p'][u] for ev in regs)
                if cur<=0: break
                k=target/cur
                for ev in regs:
                    f=ev['regs'].get(u); floor=0.9 if f==1 else 0.6 if f==0 else 0.0
                    ev['p'][u]=max(floor,min(0.97,ev['p'][u]*k))
        if LEAD_RULE and cal_future is not None:
            import datetime as _dt
            Td=_dt.date.fromisoformat(T); top40=set(u for u,r in self.race.items() if r<=40)
            def _lv(tab,lead):
                for k in sorted(tab):
                    if lead<=k: return tab[k]
                return tab[max(tab)]
            for ev in regs:
                lead=(_dt.date.fromisoformat(ev['date'])-Td).days; ev['lead']=lead
                # записанные — по статусу и сроку
                for u in self.pool:
                    f=ev['regs'].get(u)
                    if f==1: ev['p'][u]=_lv(LEAD_CONF,lead)
                    elif f==0: ev['p'][u]=_lv(LEAD_APP,lead)
                # незаписанные: сжимаем модельную p так, чтобы среднее по незаписанным из топ-40 = эмпирический уровень горизонта
                un=[u for u in top40 if ev['regs'].get(u) is None and u in self.pool]
                tgt=_lv(LEAD_NONE,lead)*LEAD_NONE_MULT; cur=np.mean([ev['p'][u] for u in un]) if un else 0
                k=(tgt/cur) if cur>0 else 0
                for u in self.pool:
                    if ev['regs'].get(u) is None: ev['p'][u]=min(0.6,ev['p'][u]*k)
        for ev in regs: ev['pv']=np.array([ev['p'][u] for u in self.pool]); ev['unreg']=np.array([ev['regs'].get(u) is None for u in self.pool])
        self.thr_ref=THR_REF or 1.3*(g.standings(year,T)[11][0] if len(g.standings(year,T))>11 else 100)
        if verbose:
            print(f'Season {year} T={T}: событий {len(self.events)} (контуров {sum(1 for e in self.events if e["type"]=="contour")}), пул {len(self.pool)}, сила из {len(self.beta)} игроков')

    FINALISTS_PLAY=False   # 2026: прошедшие в финал играют его почти наверняка (Валерий)
    def contour(self, pid, stars, date, name):
        """серийный финал: финалисты с вероятностями явки, кандидаты, сетка, база"""
        d=g.SER.get(pid); rule=RULES.get(pid,'top2')
        fin={}; part=set(); cand={}
        if d:
            played=[s for s in d['series'] if s['rows'] and s['start_date']<self.T and s['start_date']>=f'{self.year-1}-10-01']
            future=[s for s in d['series'] if s['start_date']>=self.T or not s['rows']]
            for s in played:
                for r in s['rows']: part.add(r[0])
            q=set()
            if rule=='top2':
                for s in played: q|={s['rows'][0][0],s['rows'][1][0]}
            elif rule=='top1mvp':
                for s in played:
                    r=s['rows']; w=r[0][0]; m=max(r,key=lambda x:(x[7] or 0))[0]; q.add(w); q.add(m if m!=w else r[1][0])
            elif rule=='sum2':
                agg=collections.defaultdict(list)
                for s in played:
                    for r in s['rows']: agg[r[0]].append(r[4])
                tab=sorted([(sum(sorted(v,reverse=True)[:2]),u) for u,v in agg.items() if len(v)>=2],reverse=True); q={u for s,u in tab[:10]}
            elif rule=='mcl':
                conf=collections.defaultdict(lambda: collections.defaultdict(list))
                for s in played:
                    c='IL' if s['city'] in IL else 'CY' if s['city'] in CY else 'CE'
                    for r in s['rows']: conf[c][r[0]].append(r[4])
                quotas=(('CE',6),('IL',3),('CY',1)) if self.year>=2026 else (('CE',6),('IL',2),('CY',2))
                for c,k in quotas:
                    tab=sorted([(sum(v)/len(v),u) for u,v in conf[c].items() if len(v)>=2],reverse=True); q|={u for s,u in tab[:k]}
            # явка финалиста: игроки в гонке (топ-40 на T) едут почти всегда (GMC-2025: 12/14), остальные — реже (16/40)
            for u in q: fin[u]=(0.95 if self.race.get(u,999)<=40 else 0.75) if self.FINALISTS_PLAY else (0.85 if self.race.get(u,999)<=40 else 0.45)
            # кандидаты из будущих серий: заявленные (2026) или фактические участники (бэктест); шанс пройти ~2/10 × доехать
            for u in cand_from_future(future):
                if u not in fin: cand[u]=0.2*(0.85 if self.race.get(u,999)<=40 else 0.45); part.add(u)
        size = FINAL_SIZE.get(pid, FINAL_SIZE_2S if stars==2 else 10)
        # если кандидатов больше мест — ужимаем явку тех, кто НЕ в гонке
        exp_top=sum(p for u,p in fin.items() if self.race.get(u,999)<=40)+sum(p for u,p in cand.items() if self.race.get(u,999)<=40)
        exp_rest=sum(p for u,p in fin.items() if self.race.get(u,999)>40)+sum(p for u,p in cand.items() if self.race.get(u,999)>40)
        scale=min(1.0,(size-exp_top)/exp_rest) if exp_rest>0 and size>exp_top else (0.3 if exp_rest>0 else 1)
        sc=lambda u,p: p*(1 if self.race.get(u,999)<=40 else scale)
        if self.year>=2026 and int(stars) in GRID26:
            full=GRID26[int(stars)]; base=float(full[-1])
            # баллы выше базы — только у мест, где сетка ещё не дошла до базы (2★: 9 мест, 3★: 13, 4★: 18)
            grid=[x for x in full if x>base] or full[:1]
        else:
            grid = GRID_4S if stars>=4 else (GRID_2S_12 if pid in (639,251) else GRID_2S) if stars==2 else [round(x*0.75) for x in GRID_4S]
            base = 4.0 if stars>=4 else 3.0 if stars==3 else 2.0
        return {'type':'contour','id':pid,'date':date,'stars':stars,'name':name,'fin':{u:sc(u,p) for u,p in fin.items()},
                'cand':{u:sc(u,p) for u,p in cand.items()},'part':part,'grid':grid,'base':base,'size':size}

    def grid_pts(self, stars, kind, n):
        cands=self.grids.get((stars,kind)) or self.grids.get((stars,'regular')) or self.grids.get((3,'regular'))
        N,pts=min(cands,key=lambda c:abs(c[0]-n))
        return pts

    def run(self, S=3000, seed=0, force=None, frailty=2.0):
        """force: {uid: set(event ids)} — принудительная явка. Возвращает результаты."""
        rng=np.random.default_rng(seed)
        pool=self.pool; idx={u:i for i,u in enumerate(pool)}; n=len(pool)
        beta0=np.array([self.beta.get(u,self.default)+(RACE_BETA_SHIFT if self.race.get(u,999)<=30 else 0) for u in pool])*C
        sig0=np.array([self.sigma.get(u,self.default_sigma) for u in pool])*C if (STRENGTH=='v2' and STRENGTH_SIGMA) else np.zeros(n)
        top12=np.zeros(n); top30=np.zeros(n); sums=np.zeros((S,n)); ser_by=collections.defaultdict(lambda: np.zeros(n)); ser_play=collections.defaultdict(lambda: np.zeros(n)); thr=np.zeros(S); played=np.zeros(n); new_reg=np.zeros(n); new_ser=np.zeros(n)
        base_recs=[list(self.base[u]) for u in pool]
        for s in range(S):
            recs=[list(b) for b in base_recs]
            gam=rng.gamma(frailty,1/frailty,size=n) if frailty else np.ones(n)   # индивидуальная 'форма явки' сезона
            beta=beta0+sig0*rng.standard_normal(n)   # v2: сила этого розыгрыша — из апостериора; у игрока с 7 стартами разброс широкий
            bmap=dict(zip(pool,beta)); busy=set()
            for ev in self.events:
                if ev['type']=='contour':
                    ids=[u for u,p in ev['fin'].items() if rng.random()<p]+[u for u,p in ev['cand'].items() if rng.random()<p]
                    ids=list(dict.fromkeys(ids))
                    if not ids: continue
                    # v2.4: поле финала добирается до объявленного размера заменяющими — игроками серий этого контура
                    # (не прошедшими), а если их не хватает — фоном. Раньше финал играли только прошедшие (10–14 человек
                    # на 2★ при поле 20) → у сильных выходили почти гарантированные топ-5 и раздутые баллы.
                    fill=max(0,int(ev.get('size') or 0)-len(ids))
                    if fill:
                        pool_rep=[u for u in ev['part'] if u not in set(ids)]
                        rng.shuffle(pool_rep); rep=pool_rep[:fill]; ids=ids+rep; fill-=len(rep)
                    b=np.array([bmap.get(u,self.beta.get(u,self.default)*C) for u in ids])
                    if fill: b=np.concatenate([b,rng.choice(self.bg,fill)*C])
                    if ev.get('race_pen'):   # сценарий «в топ-10 финала — все, кто не в гонке»: штраф силы игрокам топ-40 гонки
                        for j,u in enumerate(ids):
                            if self.race.get(u,999)<=40: b[j]-=ev['race_pen']
                    perf=b+rng.gumbel(size=len(b)); order=np.argsort(-perf)
                    for u in ids: busy.add((u,ev['date']))
                    got=set()
                    for rank,i in enumerate(order):
                        if i>=len(ids): continue
                        u=ids[i]
                        if rank<len(ev['grid']) and u in idx: recs[idx[u]].append((ev['grid'][rank],1)); got.add(u); new_ser[idx[u]]+=ev['grid'][rank]; ser_by[ev['id']][idx[u]]+=ev['grid'][rank]; ser_play[ev['id']][idx[u]]+=1
                        elif u in idx: recs[idx[u]].append((ev['base'],1)); got.add(u); new_ser[idx[u]]+=ev['base']; ser_by[ev['id']][idx[u]]+=ev['base']; ser_play[ev['id']][idx[u]]+=1
                    for u in ev['part']:
                        if u in idx and u not in got: recs[idx[u]].append((ev['base'],1)); new_ser[idx[u]]+=ev['base']
                    continue
                pv=ev['pv']*gam
                if LEAD_RULE and ev.get('lead',0)>=R1_MINLEAD and ev.get('unreg') is not None:
                    cur=np.array([g.best10(r) for r in recs]); gap=self.thr_ref-cur
                    m=np.where(gap<=R1_NEAR,R1_UP,np.where(gap<=R1_FAR,1.0,R1_DOWN)); pv=np.where(ev['unreg'],np.minimum(0.6,pv*m),pv)
                ids=[pool[i] for i in np.nonzero(rng.random(n)<pv)[0]]
                if force:
                    for u,evs in force.items():
                        if ev['id'] in evs and u not in ids: ids.append(u)
                ids=[u for u in ids if (u,ev['date']) not in busy]   # один турнир в день
                for u in ids: busy.add((u,ev['date']))
                k=len(ids); nbg=max(0,ev['N']-k)
                b=np.concatenate([beta[[idx[u] for u in ids]], rng.choice(self.bg,nbg)*C]) if nbg else beta[[idx[u] for u in ids]]
                perf=b+rng.gumbel(size=len(b)); ranks=np.empty(len(b),int); ranks[np.argsort(-perf)]=np.arange(1,len(b)+1)
                pts=self.grid_pts(ev['stars'],ev['type'],k+nbg)
                for j,u in enumerate(ids):
                    r=ranks[j]; recs[idx[u]].append((pts[min(r,len(pts))-1],0)); played[idx[u]]+=1; new_reg[idx[u]]+=pts[min(r,len(pts))-1]
            tot=np.array([g.best10(r) for r in recs]); sums[s]=tot
            order=np.argsort(-tot); top12[order[:12]]+=1; top30[order[:30]]+=1; thr[s]=tot[order[11]]
        return {'pool':pool,'p12':top12/S,'p30':top30/S,'sums':sums,'thr':thr,'played':played/S,'new_reg':new_reg/S,'new_ser':new_ser/S,'ser_by':{k:v/S for k,v in ser_by.items()},'ser_play':{k:v/S for k,v in ser_play.items()}}
