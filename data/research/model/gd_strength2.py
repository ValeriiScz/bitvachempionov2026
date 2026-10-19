"""gd_strength2 · v2.1 · 2026-10-20 (τ 0.4→0.26 = остаточное sd β относительно ELO у игроков с 15+ турнирами (эмпирический Байес; данные перевешивают prior с ~15 турниров); калибровка верха, см. calib_top5.py; серия «6 топ-5 из 7» за 3 сезона встречалась дважды, после горячего окна доля топ-5 падает до 0.29) · v2.0 · 2026-10-19 — сила игрока как ЗАПАС с неопределённостью: Plackett-Luce по местам + априорная сила из ELO маркеров
(markery_elo.json) + усадка по числу турниров (байесовский MAP) + апостериорная дисперсия (Лаплас) + «форма» сезона как отдельное
медленное отклонение с затуханием ρ. Заменяет gd_strength.fit_pl в gd_sim (переключатель gd_sim.STRENGTH='v2').

Зачем (19.10.2026): v1 (L2 к нулю, λ=0.1) не различала 7 турниров и 45 — RAMZES (7 обычных стартов, места 3·1·2·3·2·6·2) получал β=1.61,
самую высокую в гонке, KEX (45 турниров, ELO 1501 S) — 1.13. Три исправления: (а) prior из ELO: μ_i = a + b·(ELO_i−1200)/100;
(б) сила прижимается к prior тем сильнее, чем меньше у игрока турниров (τ — ширина prior, подбирается на удержанной осени 2025);
(в) σ_i — ширина апостериора: у игрока с 7 стартами она широкая, и в Монте-Карло сила тянется из N(β_i, σ_i²), а не точкой.
Форма: β_season — та же оценка только по турнирам текущего сезона с prior N(β_long, τ_f²); вперёд берём β_long + ρ·(β_season−β_long).
FACT/ГИПОТЕЗА: формулы — ВЫВОД из стандартной байесовской PL; параметры τ, b, ρ — подобраны на удержанных данных (см. tune_strength2.py)."""
import numpy as np, json, os, datetime, collections
import gd_data as g

HERE=os.path.dirname(os.path.abspath(__file__))
ELO_FILE=os.path.join(HERE,'markery_elo.json')
# --- параметры (подобраны tune_strength2.py 19.10.2026; см. журнал в файле) ---
TAU=0.26        # ширина prior для игроков с ELO (в единицах β)
TAU_NOELO=0.75  # ширина prior без ELO (prior = центр пула)
B_ELO=None      # наклон β на 100 ELO; None → оценить регрессией на первом проходе
TAU_FORM=0.45   # ширина prior «формы» сезона вокруг долгой силы
RHO_FORM=0.5    # какая доля отклонения сезона переносится на остаток года
ELO_CENTER=1200.0

def load_elo():
    if not os.path.exists(ELO_FILE): return {}
    d=json.load(open(ELO_FILE,encoding='utf-8'))['players']
    return {int(u):v for u,v in d.items()}
ELO=load_elo()
YEAR_BLEND=0.5; YEAR_MAX_AGE=60   # ELO сезона идёт в смесь только если снят не старше 60 дней от даты T (иначе он сам «устаревшая форма»)
_T_REF=None
def elo_of(u, year_blend=None):
    """ELO игрока: all-time, с примесью ELO сезона (если снимок свежий); None если нет"""
    v=ELO.get(u)
    if not v or not v.get('elo_all'): return None
    yb=YEAR_BLEND if year_blend is None else year_blend
    if v.get('elo_year') and yb>0 and _T_REF and v.get('date_year'):
        age=(datetime.date.fromisoformat(_T_REF)-datetime.date.fromisoformat(v['date_year'])).days
        if age<=YEAR_MAX_AGE: return (1-yb)*v['elo_all']+yb*v['elo_year']
    return v['elo_all']

def rankings_before(T, since=None, flat=False):
    """(вес, [uid по местам]) по турнирам с датой < T (и ≥ since). Веса по давности 1/0.5/0.25, flat → 1."""
    out=[]; Td=datetime.date.fromisoformat(T)
    for e in g.EV.values():
        if not e['N'] or e['date']>=T or (since and e['date']<since): continue
        age=(Td-datetime.date.fromisoformat(e['date'])).days
        w=1.0 if flat else (1.0 if age<=365 else 0.5 if age<=730 else 0.25)
        rows=[r for r in e['rows'] if r[2] is not None and r[2]<1000]; rows.sort(key=lambda r:r[2])
        if len(rows)<6: continue
        out.append((w,[r[0] for r in rows]))
    return out

def fit_map(rankings, mu, tau, iters=400, lr=0.5):
    """MAP Plackett-Luce с гауссовым prior N(mu_i, tau_i²). mu, tau — dict uid→число (или число).
    Возвращает beta (dict), sigma (dict, Лаплас по диагонали), n_eff (dict, взвешенное число турниров)."""
    uids=sorted({u for w,r in rankings for u in r}); idx={u:i for i,u in enumerate(uids)}; n=len(uids)
    MU=np.array([mu[u] if isinstance(mu,dict) else mu for u in uids]); TAU=np.array([tau[u] if isinstance(tau,dict) else tau for u in uids])
    prec=1.0/TAU**2
    R=[(w,np.array([idx[u] for u in r])) for w,r in rankings]
    beta=MU.copy(); neff=np.zeros(n)
    for w,r in R: neff[r]+=w
    pre=prec+0.5*neff+0.5   # диагональное предобуславливание: шаг ~ grad/H, устойчиво при любом τ
    for it in range(iters):
        grad=np.zeros(n)
        for w,r in R:
            b=beta[r]; m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
            cum_inv=np.cumsum(1.0/cs)
            grad[r]+=w*(1.0-ex*cum_inv)
        grad-=(beta-MU)*prec
        beta+=lr*grad/pre
    # Лаплас: диагональ наблюдённой информации
    H=prec.copy()
    for w,r in R:
        b=beta[r]; m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
        cum_inv=np.cumsum(1.0/cs); cum_inv2=np.cumsum(1.0/cs**2)
        H[r]+=w*(ex*cum_inv-ex**2*cum_inv2)
    sigma=1.0/np.sqrt(np.maximum(H,1e-6))
    return dict(zip(uids,beta)), dict(zip(uids,sigma)), dict(zip(uids,neff))

def elo_prior(rankings, tau=None, tau_noelo=None, b_elo=None, verbose=False):
    """Строит prior: μ_i = a + b·(ELO−1200)/100 по регрессии «сырой» β на ELO у игроков с ≥10 турнирами; без ELO — центр пула.
    Возвращает mu (dict), tau (dict), info."""
    tau=tau or TAU; tau_noelo=tau_noelo or TAU_NOELO
    uids=sorted({u for w,r in rankings for u in r})
    b0,s0,ne=fit_map(rankings,0.0,1.0)          # первый проход: слабый prior к нулю
    xs=[];ys=[];ws=[]
    for u in uids:
        e=elo_of(u)
        if e is not None and ne[u]>=10: xs.append((e-ELO_CENTER)/100); ys.append(b0[u]); ws.append(ne[u])
    xs,ys,ws=map(np.array,(xs,ys,ws))
    if b_elo is None and len(xs)>=8:
        X=np.c_[np.ones_like(xs),xs]; W=np.diag(ws); coef=np.linalg.solve(X.T@W@X,X.T@W@ys); a,b=coef
        resid=ys-X@coef; r2=1-np.average(resid**2,weights=ws)/np.average((ys-np.average(ys,weights=ws))**2,weights=ws)
    else:
        b=b_elo if b_elo is not None else 0.0; a=float(np.average(ys-b*xs,weights=ws)) if len(xs) else 0.0; r2=float('nan')
    center=float(np.mean([b0[u] for u in uids if elo_of(u) is None])) if any(elo_of(u) is None for u in uids) else a
    mu={}; tv={}
    for u in uids:
        e=elo_of(u)
        if e is None: mu[u]=center; tv[u]=tau_noelo
        else: mu[u]=a+b*(e-ELO_CENTER)/100; tv[u]=tau
    info={'a':float(a),'b_per100':float(b),'r2':float(r2),'n_fit':int(len(xs)),'center_noelo':center}
    if verbose: print(f"prior из ELO: β ≈ {a:.2f} + {b:.3f}·(ELO−1200)/100, R²={r2:.2f} по {len(xs)} игрокам с ≥10 турнирами; без ELO → {center:.2f}")
    return mu,tv,info

class Strength:
    """Оценка силы на дату T: долгая (β_long, σ_long), сезонная (β_season), прогнозная (β_fwd = β_long + ρ·Δform)."""
    def __init__(self, T, year=None, verbose=False, tau=None, tau_noelo=None, b_elo=None, tau_form=None, rho=None):
        self.T=T; year=year or int(T[:4])
        global _T_REF; _T_REF=T
        rk=rankings_before(T)
        self.mu,self.tau,self.info=elo_prior(rk,tau,tau_noelo,b_elo if b_elo is not None else B_ELO,verbose)
        self.beta,self.sigma,self.neff=fit_map(rk,self.mu,self.tau)
        tf=tau_form or TAU_FORM; self.rho=RHO_FORM if rho is None else rho
        rks=rankings_before(T,since=f'{year}-01-01',flat=True)
        bs,ss,ns=fit_map(rks,{u:self.beta.get(u,self.mu.get(u,0.0)) for u in {x for w,r in rks for x in r}},tf)
        self.beta_season=bs; self.n_season=ns
        self.form={u:bs[u]-self.beta[u] for u in bs if u in self.beta}
        vals=np.array(list(self.beta.values())); self.default=float(np.percentile(vals,30)); self.default_sigma=float(tau_noelo or TAU_NOELO)
    def fwd(self,u):
        return self.beta.get(u,self.default)+self.rho*self.form.get(u,0.0)
    def sd(self,u):
        return self.sigma.get(u,self.default_sigma)
    def table(self, uids):
        rows=[]
        for u in uids:
            rows.append({'uid':u,'nick':g.NICK.get(u,'?'),'elo':elo_of(u),'mu':round(self.mu.get(u,self.default),3),'beta_long':round(self.beta.get(u,self.default),3),
                         'sigma':round(self.sd(u),3),'n_eff':round(self.neff.get(u,0),1),'beta_season':round(self.beta_season.get(u,self.beta.get(u,self.default)),3),
                         'form':round(self.form.get(u,0.0),3),'n_season':round(self.n_season.get(u,0),1),'beta_fwd':round(self.fwd(u),3)})
        return rows

def loglik(rankings, bfun, scale=1.0, only=None):
    """средний лог-правдоподобия места; only — множество uid, по которым суммировать (напр. топ-40 гонки)"""
    ll=0;n=0
    for w,r in rankings:
        b=np.array([bfun(u) for u in r])*scale; m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
        t=b-(np.log(cs)+m)
        if only is not None:
            msk=np.array([u in only for u in r]); ll+=t[msk].sum(); n+=int(msk.sum())
        else: ll+=t.sum(); n+=len(r)
    return ll/max(n,1)

if __name__=='__main__':
    import sys
    T=sys.argv[1] if len(sys.argv)>1 else '2026-10-19'
    S=Strength(T,verbose=True)
    st=g.standings(int(T[:4]),T)
    print(f"{'#':>2} {'ник':14s} {'ELO':>5} {'μ':>6} {'β_long':>7} {'σ':>5} {'n_eff':>5} {'β_сез':>6} {'форма':>6} {'β_fwd':>6}")
    for i,(s,u) in enumerate(st[:30]):
        r=S.table([u])[0]
        print(f"{i+1:2d} {r['nick']:14s} {str(round(r['elo'])) if r['elo'] else '—':>5} {r['mu']:6.2f} {r['beta_long']:7.2f} {r['sigma']:5.2f} {r['n_eff']:5.1f} {r['beta_season']:6.2f} {r['form']:+6.2f} {r['beta_fwd']:6.2f}")
