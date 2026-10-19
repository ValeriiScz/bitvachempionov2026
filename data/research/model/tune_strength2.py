"""tune_strength2.py · v1.0 · 2026-10-19 — подбор τ (ширина prior), ρ и τ_f (форма) и масштаба C для gd_strength2 на удержанной осени:
обучение по турнирам до 14.09 года Y, проверка — лог-правдоподобие мест на турнирах 14.09–31.12 того же года (на место, больше = лучше).
⚠ ELO маркеров снят в 2026 — для бэктестов 2024/2025 это утечка (ELO уже «знает» осень). Поэтому отдельно считаем вариант prior без ELO (только центр пула).
Запуск: python3 tune_strength2.py [год=2025]"""
import sys, numpy as np, gd_data as g, gd_strength2 as s2, itertools
Y=int(sys.argv[1]) if len(sys.argv)>1 else 2025
T=f'{Y}-09-14'
test=[]
for e in g.EV.values():
    if e['N'] and T<=e['date']<f'{Y+1}-01-01' and e['kind']!='serial_final':
        rows=sorted([r for r in e['rows'] if r[2] is not None and r[2]<1000],key=lambda r:r[2])
        if len(rows)>=6: test.append((1.0,[r[0] for r in rows]))
print(f'год {Y}: тест {len(test)} турниров, {sum(len(r) for w,r in test)} мест')
TOP=set(u for s_,u in g.standings(Y,T)[:40])
base=s2.loglik(test,lambda u:0.0); base40=s2.loglik(test,lambda u:0.0,only=TOP)
print(f'случайный порядок: все {base:.4f} · топ-40 гонки {base40:.4f}')
# v1 для сравнения
from gd_strength import fit_pl, rankings_before
b1=fit_pl(rankings_before(T),lam=0.1); d1=float(np.percentile(np.array(list(b1.values())),30))
best1=max(((s2.loglik(test,lambda u:b1.get(u,d1),c),c) for c in (1.0,1.2,1.4,1.6,1.8)))
best1t=max(((s2.loglik(test,lambda u:b1.get(u,d1),c,only=TOP),c) for c in (1.0,1.2,1.4,1.6,1.8)))
print(f'v1 (L2 к нулю, λ=0.1): все {best1[0]:.4f} (C={best1[1]}) · топ-40 {best1t[0]:.4f} (C={best1t[1]})')
def ev(S, rho, scales=(0.6,0.8,1.0,1.2,1.4)):
    S.rho=rho
    a=max(((s2.loglik(test,S.fwd,c),c) for c in scales)); t=max(((s2.loglik(test,S.fwd,c,only=TOP),c) for c in scales))
    return a,t
res=[]
for use_elo in (True,False):
    s2.YEAR_BLEND=0.0
    for tau in (0.25,0.4,0.55,0.8,1.2):
        S=s2.Strength(T,tau=tau,tau_noelo=(0.75 if use_elo else tau),b_elo=(None if use_elo else 0.0),tau_form=0.45,rho=0.0)
        if not use_elo:
            # без ELO: prior = общий центр для всех
            pass
        for tf in (0.3,0.45,0.7):
            S2=s2.Strength(T,tau=tau,tau_noelo=(0.75 if use_elo else tau),b_elo=(None if use_elo else 0.0),tau_form=tf,rho=0.0)
            for rho in (0.0,0.5,1.0):
                (ll,c),(llt,ct)=ev(S2,rho); res.append((round(float(llt),4),ct,round(float(ll),4),c,use_elo,tau,tf,rho))
                if rho==0.0 and tf==0.45: print(f"  ELO={use_elo!s:5s} τ={tau:4.2f} ρ=0: все {ll:.4f} (C={c}) · топ-40 {llt:.4f} (C={ct})  prior a={S2.info['a']:.2f} b={S2.info['b_per100']:.3f} R²={S2.info['r2']:.2f} n={S2.info['n_fit']}")
res.sort(reverse=True)
print('\nтоп-12 по топ-40 (ll40, C40, ll_all, C, ELO, τ, τ_f, ρ):')
for r in res[:12]: print('  ',r)
print('\nлучшее с ELO:',[r for r in res if r[4]][0]); print('лучшее без ELO:',[r for r in res if not r[4]][0])
print('ρ: среднее ll40 по ρ:',{rho:round(float(np.mean([r[0] for r in res if r[7]==rho])),4) for rho in (0.0,0.5,1.0)})
print('τ_f: среднее ll40 по τ_f:',{tf:round(float(np.mean([r[0] for r in res if r[6]==tf and r[7]>0])),4) for tf in (0.3,0.45,0.7)})
