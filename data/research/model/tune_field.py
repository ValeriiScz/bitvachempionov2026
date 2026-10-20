"""tune_field.py · v1.0 · 2026-10-20 — нужен ли вес турнира по размеру поля и силе поля при оценке силы/формы (gd_strength2).
Вес турнира в Plackett-Luce: w = w_давности × (N/30)^A × exp(B·z), z — стандартизованная сила поля (средняя «сырая» β участников).
Отдельно — «срез топ-10»: в полях < 25 места ниже 5-го собираются в один хвост (PL по топ-5 + «остальные»), CUT_SMALL=True.
Проверка: обучение до 14.09 года Y, ll мест топ-40 гонки на турнирах 14.09–31.12 (hold-out), калибровка топ-5. Запуск: python3 tune_field.py"""
import numpy as np, datetime, gd_data as g, gd_strength2 as s2
rng=np.random.default_rng(0)
class Cut(list):
    k=5   # список-рейтинг, в котором порядок значим только для первых k мест
_orig=s2.rankings_before
def make_rb(A,B,cut_small,zmap):
    def rb(T,since=None,flat=False):
        out=[];Td=datetime.date.fromisoformat(T)
        for e in g.EV.values():
            if not e['N'] or e['date']>=T or (since and e['date']<since): continue
            age=(Td-datetime.date.fromisoformat(e['date'])).days
            w=1.0 if flat else (1.0 if age<=365 else 0.5 if age<=730 else 0.25)
            rows=[r for r in e['rows'] if r[2] is not None and r[2]<1000]; rows.sort(key=lambda r:r[2])
            if len(rows)<6: continue
            n=len(rows); w*=(n/30.0)**A*np.exp(B*zmap.get(e['id'],0.0))
            r=[x[0] for x in rows]
            if cut_small and n<25: r=Cut(r)
            out.append((w,r))
        return out
    return rb
# fit_map с поддержкой «срезанных» рейтингов: PL только по первым 5 местам (остальные — неупорядоченный хвост)
_fit=s2.fit_map
def fit_map_cut(rankings,mu,tau,iters=400,lr=0.5):
    full=[]
    for w,r in rankings:
        full.append((w,list(r),r.k if isinstance(r,Cut) else len(r)))
    uids=sorted({u for w,r,k in full for u in r}); idx={u:i for i,u in enumerate(uids)}; n=len(uids)
    MU=np.array([mu[u] if isinstance(mu,dict) else mu for u in uids]); TAU=np.array([tau[u] if isinstance(tau,dict) else tau for u in uids]); prec=1/TAU**2
    R=[(w,np.array([idx[u] for u in r]),k) for w,r,k in full]
    beta=MU.copy(); neff=np.zeros(n)
    for w,r,k in R: neff[r]+=w
    pre=prec+0.5*neff+0.5
    for it in range(iters):
        grad=np.zeros(n)
        for w,r,k in R:
            b=beta[r]; m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
            inv=1.0/cs
            if k<len(r): inv[k:]=0   # места ниже k — без порядка
            cum_inv=np.cumsum(inv)
            gr=np.zeros(len(r)); gr[:k]=1.0; gr-=ex*cum_inv
            grad[r]+=w*gr
        grad-=(beta-MU)*prec; beta+=lr*grad/pre
    H=prec.copy()
    for w,r,k in R:
        b=beta[r]; m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
        inv=1/cs; inv2=1/cs**2
        if k<len(r): inv[k:]=0; inv2[k:]=0
        H[r]+=w*(ex*np.cumsum(inv)-ex**2*np.cumsum(inv2))
    sigma=1/np.sqrt(np.maximum(H,1e-6))
    return dict(zip(uids,beta)),dict(zip(uids,sigma)),dict(zip(uids,neff))
def field_z(T):
    b0,_,_=_fit(_orig(T),0.0,1.0); z={}
    for e in g.EV.values():
        rows=[r for r in e['rows'] if r[2] is not None and r[2]<1000]
        if len(rows)>=6 and e['N']: z[e['id']]=np.mean([b0.get(r[0],0.0) for r in rows])
    v=np.array(list(z.values())); return {k:(x-v.mean())/v.std() for k,x in z.items()}
def holdout(Y):
    T=f'{Y}-09-14'; test=[]
    for e in g.EV.values():
        if e['N'] and T<=e['date']<f'{Y+1}-01-01' and e['kind']!='serial_final':
            rows=sorted([r for r in e['rows'] if r[2] is not None and r[2]<1000],key=lambda r:r[2])
            if len(rows)>=6: test.append((1.0,[r[0] for r in rows]))
    TOP=set(u for s,u in g.standings(Y,T)[:40]); return T,test,TOP
def run(Y,A,B,cut,zmap,T,test,TOP):
    s2.rankings_before=make_rb(A,B,cut,zmap); s2.fit_map=fit_map_cut
    try:
        S=s2.Strength(T)
        ll=s2.loglik(test,S.fwd,1.0,only=TOP)
    finally: s2.rankings_before=_orig; s2.fit_map=_fit
    return ll,S
if __name__=='__main__':
    for Y in (2025,2024):
        T,test,TOP=holdout(Y); zmap=field_z(T)
        print(f'\n=== {Y}: hold-out {len(test)} турниров')
        res=[]
        for cut in (False,True):
            for A in (0.0,0.5,1.0,1.5):
                for B in (0.0,0.3,0.6):
                    ll,S=run(Y,A,B,cut,zmap,T,test,TOP); res.append((ll,A,B,cut))
        res.sort(reverse=True)
        base=[r for r in res if r[1]==0 and r[2]==0 and not r[3]][0][0]
        print(f'база (без весов) ll40={base:.4f}')
        for ll,A,B,cut in res[:8]: print(f'  ll40={ll:.4f} ({ll-base:+.4f})  A={A} B={B} срез<25={cut}')
        print('  среднее по A:',{A:round(float(np.mean([r[0] for r in res if r[1]==A])),4) for A in (0.0,0.5,1.0,1.5)},' по B:',{B:round(float(np.mean([r[0] for r in res if r[2]==B])),4) for B in (0.0,0.3,0.6)},' срез:',{c:round(float(np.mean([r[0] for r in res if r[3]==c])),4) for c in (False,True)})
