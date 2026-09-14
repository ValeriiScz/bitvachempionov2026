"""gd_sim · v1.0 · 2026-09-14 — Монте-Карло остатка сезона mafgame: явка × сила (Plackett-Luce) × сетка баллов × серийники → Σ=best10(≤2 serial) → топ-12."""
import numpy as np, datetime, collections
import gd_data as g
from gd_strength import rankings_before, fit_pl
from gd_attend import Attend

LAM, C = 0.1, 1.1
RACE_BOOST = 1.0   # калибровочный множитель явки для мест 1–25 гонки (подбирается на бэктесте)
GRID_2S=[30,27,25,22,20,18,16,14,12,10,8,6]
GRID_4S=[42,39,37,34,32,30,28,26,24,22,20,16,14,10,8]
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
TARGET_TOP30_MEAN=None   # если задано — явка масштабируется так, чтобы у топ-30 гонки среднее число обычных турниров = это

class Season:
    def __init__(self, year, T, cal_future=None, verbose=True, att_T=None):
        self.year, self.T = year, T
        # пул: игроки леджера, у которых есть хоть одна запись до T (иначе на дату T их в гонке не существовало)
        self.pool=[int(u) for u in g.L if any(r[2]<T for r in g.L[u]['rp'])]
        # сила
        self.beta=fit_pl(rankings_before(T), lam=LAM)
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
                if t['kind']=='serial_final': self.events.append(self.contour(t['id'],t['stars'],t['start'],t['name']))
                else:
                    regs={u:f for u,n,f in t['regs']}
                    self.events.append({'type':t['kind'],'id':t['id'],'date':t['start'],'stars':t['stars'],'country':t['country'],'N':t['exp'] or 30,'name':t['name'],'regs':regs})
        self.events.sort(key=lambda e:e['date'])
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
        if TARGET_TOP30_MEAN:
            top=[u for u,r in self.race.items() if r<=30 and u in set(self.pool)]
            cur=sum(ev['p'][u] for ev in regs for u in top)/max(1,len(top))
            k=TARGET_TOP30_MEAN/cur
            for ev in regs:
                for u in self.pool:
                    if ev['regs'].get(u) is None: ev['p'][u]=min(0.97,ev['p'][u]*k)
        for ev in regs: ev['pv']=np.array([ev['p'][u] for u in self.pool])
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
        size = 30 if pid in (277,) else 10 if stars==2 or rule=='mcl' else 55 if pid==664 else 10
        # если кандидатов больше мест — ужимаем явку тех, кто НЕ в гонке
        exp_top=sum(p for u,p in fin.items() if self.race.get(u,999)<=40)+sum(p for u,p in cand.items() if self.race.get(u,999)<=40)
        exp_rest=sum(p for u,p in fin.items() if self.race.get(u,999)>40)+sum(p for u,p in cand.items() if self.race.get(u,999)>40)
        scale=min(1.0,(size-exp_top)/exp_rest) if exp_rest>0 and size>exp_top else (0.3 if exp_rest>0 else 1)
        sc=lambda u,p: p*(1 if self.race.get(u,999)<=40 else scale)
        grid = GRID_4S if stars>=4 else GRID_2S if stars==2 else [round(x*0.75) for x in GRID_4S]
        base = 4.0 if stars>=4 else 3.0 if stars==3 else 2.0
        return {'type':'contour','id':pid,'date':date,'stars':stars,'name':name,'fin':{u:sc(u,p) for u,p in fin.items()},
                'cand':{u:sc(u,p) for u,p in cand.items()},'part':part,'grid':grid,'base':base}

    def grid_pts(self, stars, kind, n):
        cands=self.grids.get((stars,kind)) or self.grids.get((stars,'regular')) or self.grids.get((3,'regular'))
        N,pts=min(cands,key=lambda c:abs(c[0]-n))
        return pts

    def run(self, S=3000, seed=0, force=None, frailty=2.0):
        """force: {uid: set(event ids)} — принудительная явка. Возвращает результаты."""
        rng=np.random.default_rng(seed)
        pool=self.pool; idx={u:i for i,u in enumerate(pool)}; n=len(pool)
        beta=np.array([self.beta.get(u,self.default) for u in pool])*C
        top12=np.zeros(n); top30=np.zeros(n); sums=np.zeros((S,n)); thr=np.zeros(S); played=np.zeros(n); new_reg=np.zeros(n); new_ser=np.zeros(n)
        base_recs=[list(self.base[u]) for u in pool]
        for s in range(S):
            recs=[list(b) for b in base_recs]
            gam=rng.gamma(frailty,1/frailty,size=n) if frailty else np.ones(n)   # индивидуальная 'форма явки' сезона
            for ev in self.events:
                if ev['type']=='contour':
                    ids=[u for u,p in ev['fin'].items() if rng.random()<p]+[u for u,p in ev['cand'].items() if rng.random()<p]
                    ids=list(dict.fromkeys(ids))
                    if not ids: continue
                    b=np.array([self.beta.get(u,self.default)*C for u in ids])
                    perf=b+rng.gumbel(size=len(b)); order=np.argsort(-perf)
                    got=set()
                    for rank,i in enumerate(order):
                        u=ids[i]
                        if rank<len(ev['grid']) and u in idx: recs[idx[u]].append((ev['grid'][rank],1)); got.add(u); new_ser[idx[u]]+=ev['grid'][rank]
                        elif u in idx: recs[idx[u]].append((ev['base'],1)); got.add(u); new_ser[idx[u]]+=ev['base']
                    for u in ev['part']:
                        if u in idx and u not in got: recs[idx[u]].append((ev['base'],1)); new_ser[idx[u]]+=ev['base']
                    continue
                pv=ev['pv']*gam; ids=[pool[i] for i in np.nonzero(rng.random(n)<pv)[0]]
                if force:
                    for u,evs in force.items():
                        if ev['id'] in evs and u not in ids: ids.append(u)
                k=len(ids); nbg=max(0,ev['N']-k)
                b=np.concatenate([beta[[idx[u] for u in ids]], rng.choice(self.bg,nbg)*C]) if nbg else beta[[idx[u] for u in ids]]
                perf=b+rng.gumbel(size=len(b)); ranks=np.empty(len(b),int); ranks[np.argsort(-perf)]=np.arange(1,len(b)+1)
                pts=self.grid_pts(ev['stars'],ev['type'],k+nbg)
                for j,u in enumerate(ids):
                    r=ranks[j]; recs[idx[u]].append((pts[min(r,len(pts))-1],0)); played[idx[u]]+=1; new_reg[idx[u]]+=pts[min(r,len(pts))-1]
            tot=np.array([g.best10(r) for r in recs]); sums[s]=tot
            order=np.argsort(-tot); top12[order[:12]]+=1; top30[order[:30]]+=1; thr[s]=tot[order[11]]
        return {'pool':pool,'p12':top12/S,'p30':top30/S,'sums':sums,'thr':thr,'played':played/S,'new_reg':new_reg/S,'new_ser':new_ser/S}
