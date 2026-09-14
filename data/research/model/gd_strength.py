"""gd_strength · v1.0 — сила игроков: Plackett-Luce по таблицам мест турниров (до даты T), временные веса, L2-усадка к 0."""
import numpy as np, datetime, collections
import gd_data as g

def rankings_before(T, min_pos_valid=True):
    """Список (weight, [uid по местам]) по турнирам с датой < T. Серийные финалы — только финалисты (pos<1000)."""
    out=[]
    Td=datetime.date.fromisoformat(T)
    for e in g.EV.values():
        if not e['N'] or e['date']>=T: continue
        age=(Td-datetime.date.fromisoformat(e['date'])).days
        w=1.0 if age<=365 else 0.5 if age<=730 else 0.25
        rows=[r for r in e['rows'] if r[2] is not None and r[2]<1000]
        rows.sort(key=lambda r:r[2])
        if len(rows)<6: continue
        out.append((w,[r[0] for r in rows]))
    return out

def fit_pl(rankings, lam=0.02, iters=300, lr=0.5):
    """PL с L2 к 0 (β=log-сила). Возвращает dict uid→β, и множество игроков с данными."""
    uids=sorted({u for w,r in rankings for u in r}); idx={u:i for i,u in enumerate(uids)}
    n=len(uids); beta=np.zeros(n)
    R=[(w,np.array([idx[u] for u in r])) for w,r in rankings]
    for it in range(iters):
        grad=np.zeros(n); 
        for w,r in R:
            b=beta[r]
            # cumulative logsumexp от хвоста: S_k = log Σ_{j≥k} exp b_j
            m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
            # для позиции k: softmax_k(j) = exp(b_j)/cs[k] для j≥k ; grad_j = 1 - Σ_{k≤pos_j} exp(b_j)/cs[k]
            inv=1.0/cs; cum_inv=np.cumsum(inv)  # Σ_{k≤p} 1/cs[k]
            grad[r]+= w*(1.0 - ex*cum_inv)
        grad-=2*lam*beta*len(R)/max(1,len(R))*10  # усадка (λ масштабирована)
        beta+=lr*grad/ max(1,np.sqrt(it+1))
        beta-=beta.mean()*0  # без центрирования: усадка к 0 задаёт шкалу
    return dict(zip(uids,beta))

def loglik(rankings, beta, default, scale=1.0):
    ll=0;n=0
    for w,r in rankings:
        b=np.array([beta.get(u,default) for u in r])*scale
        m=b.max(); ex=np.exp(b-m); cs=np.cumsum(ex[::-1])[::-1]
        ll+= (b - (np.log(cs)+m)).sum(); n+=len(r)
    return ll/n

if __name__=='__main__':
    T='2025-09-14'
    train=rankings_before(T)
    Te='2025-12-31'
    test=[(w,r) for w,r in rankings_before('2026-01-01') if True]
    # тест = турниры между T и конца года
    import gd_data as g2
    test=[]
    for e in g.EV.values():
        if e['N'] and T<=e['date']<'2026-01-01':
            rows=sorted([r for r in e['rows'] if r[2] is not None and r[2]<1000],key=lambda r:r[2])
            if len(rows)>=6: test.append((1.0,[r[0] for r in rows]))
    print('train турниров',len(train),'test',len(test))
    for lam in (0.005,0.01,0.02,0.05,0.1):
        beta=fit_pl(train,lam=lam)
        vals=np.array(list(beta.values())); default=np.percentile(vals,30)
        base=loglik(test,{},0.0)
        res={sc:loglik(test,beta,default,sc) for sc in (0.6,0.8,1.0,1.2,1.4)}
        best=max(res,key=res.get)
        print(f'lam={lam}: β sd {vals.std():.2f} min {vals.min():.2f} max {vals.max():.2f}; test ll/place: random {base:.4f}, ' + ' '.join(f'c={k}:{v:.4f}' for k,v in res.items()), '→ best c',best)
