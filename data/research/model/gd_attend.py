"""gd_attend · v1.0 — модель явки: P(игрок i сыграет турнир t) без заявки. Логит по темпу игрока, стране, звёздам, типу."""
import numpy as np, datetime, collections
import gd_data as g

def shift(T, days):
    return (datetime.date.fromisoformat(T)+datetime.timedelta(days=days)).isoformat()

def player_rates(pool, T):
    """темп за год до T: доля рейтинговых турниров (regular+teams), которые игрок сыграл; + число"""
    T0=shift(T,-365)
    evs=[e for e in g.EV.values() if e['N'] and T0<=e['date']<T and e['kind']!='serial_final']
    n_ev=len(evs); played=collections.Counter()
    byc=collections.defaultdict(collections.Counter)  # игрок → страна → сыграно
    for e in evs:
        for uid,_,_,_ in e['rows']:
            played[uid]+=1; byc[uid][e['country']]+=1
    return {u:(played[u]+0.5, n_ev) for u in pool}, n_ev, byc

_RACE={}
def race_rank(uid, e):
    """место игрока в годовом рейтинге на дату турнира (по леджеру до этой даты)"""
    key=(e['year'],e['date'])
    if key not in _RACE:
        st=g.standings(e['year'],e['date']); _RACE[key]={u:i+1 for i,(s,u) in enumerate(st)}
    return _RACE[key].get(uid,999)
def features(uid, e, rate, byc, home):
    rk=race_rank(uid,e); q4=1.0 if e['date'][5:7]>='09' else 0.0
    b1=1.0 if rk<=6 else 0.0; b2=1.0 if 6<rk<=12 else 0.0; b3=1.0 if 12<rk<=25 else 0.0; b4=1.0 if 25<rk<=40 else 0.0
    hm=1.0 if (home.get(uid) and home[uid]==e['country']) else 0.0
    been=1.0 if byc.get(uid,{}).get(e['country'],0)>0 else 0.0
    cnt,n_ev=rate
    x=[1.0, np.log(cnt), np.log(max(n_ev,1)), hm, (e['stars']-3)/1.0, 1.0 if e['kind']=='teams' else 0.0, been,
       b1,b2,b3,b4, (b1+b2+b3+b4)*q4, q4, 1.0 if (hm==0 and been==0) else 0.0, 1.0 if e['stars']<=1 else 0.0]
    return x

_RATES={}
def rates_at(pool, date):
    """темп за 365 дней до даты (кэш по месяцу)"""
    key=date[:7]
    if key not in _RATES: _RATES[key]=player_rates(pool, date[:7]+'-01')
    return _RATES[key]
def build_xy(pool, T_from, T_to, home):
    """пары (i,t) для турниров в [T_from,T_to): темп игрока — за скользящий год до месяца турнира (без заглядывания вперёд)."""
    X=[];y=[]
    for e in g.EV.values():
        if not e['N'] or not (T_from<=e['date']<T_to) or e['kind']=='serial_final': continue
        rate,n_ev,byc=rates_at(pool,e['date'])
        played={r[0] for r in e['rows']}
        for u in pool:
            X.append(features(u,e,rate[u],byc,home)); y.append(1 if u in played else 0)
    return np.array(X),np.array(y)

def fit_logit(X,y,l2=1e-3,iters=500,lr=0.1):
    w=np.zeros(X.shape[1])
    for _ in range(iters):
        p=1/(1+np.exp(-X@w)); grad=X.T@(p-y)/len(y)+l2*w
        w-=lr*grad*5
    return w

class Attend:
    def __init__(self,pool,T,home):
        # обучение на году до T с признаками из предыдущего года
        self.pool=pool; self.home=home
        X,y=build_xy(pool,shift(T,-365),T,home)
        self.w=fit_logit(X,y); self.X=X;self.y=y
        self.rate,self.n_ev,self.byc=player_rates(pool,T)
    def p(self,uid,e):
        x=np.array(features(uid,e,self.rate[uid],self.byc,self.home))
        return 1/(1+np.exp(-x@self.w))

if __name__=='__main__':
    T='2025-09-14'
    pool=[int(u) for u in g.L]
    A=Attend(pool,T,g.COUNTRY)
    print('обучение: пар',len(A.y),'явок',A.y.sum(),'веса [const, log count, log n_ev, home, stars, teams, был в стране, r1-6, r7-12, r13-25, r26-40, race×Q4, Q4, чужая страна, 1★]:',np.round(A.w,2))
    # тест: турниры после T до конца 2025
    X,y=[],[]
    for e in g.EV.values():
        if e['N'] and T<=e['date']<'2026-01-01' and e['kind']!='serial_final':
            played={r[0] for r in e['rows']}
            for u in pool: X.append(A.p(u,e)); y.append(1 if u in played else 0)
    X=np.array(X);y=np.array(y)
    print(f'тест: пар {len(y)}, явок факт {y.sum()}, предсказано {X.sum():.0f}; Brier {((X-y)**2).mean():.4f} база {((y.mean()-y)**2).mean():.4f}')
    o=np.argsort(X)
    for q in range(5):
        sl=o[q*len(o)//5:(q+1)*len(o)//5]; print(f'  квинтиль {q+1}: предск {X[sl].mean()*100:5.1f}%  факт {y[sl].mean()*100:5.1f}%')
    # по игрокам топ-30 на T: ожидаемое число турниров vs факт
    st=g.standings(2025,T)[:30]
    evs=[e for e in g.EV.values() if e['N'] and T<=e['date']<'2026-01-01' and e['kind']!='serial_final']
    print('\nтоп-30 на 14.09.2025: ожидание турниров до конца года vs факт')
    for s,u in st:
        exp_=sum(A.p(u,e) for e in evs); fact=sum(1 for e in evs if u in {r[0] for r in e['rows']})
        print(f'  {g.NICK[u]:14s} Σ{s:5.0f} темп {A.rate[u][0]:4.1f}/{A.rate[u][1]}  ожид {exp_:4.1f}  факт {fact}')
