"""calib_top5.py · 20.10.2026 — калибровка «верха»: предсказанная моделью доля топ-5/топ-10 у топ-40 гонки на 14.09 против факта осени. По бинам предсказания."""
import sys, numpy as np, gd_data as g, gd_strength2 as s2, gd_sim
rng=np.random.default_rng(0)
def implied(beta,sd,bg,C,grid_n=40,S=2000):
    t5=t10=0
    for _ in range(S):
        b=(beta+sd*rng.standard_normal())*C; perf=np.concatenate([[b],rng.choice(bg,grid_n-1)*C])+rng.gumbel(size=grid_n); r=int((perf>perf[0]).sum())+1; t5+=r<=5; t10+=r<=10
    return t5/S,t10/S
for Y in (2025,2024):
    T=f'{Y}-09-14'; top=[u for s,u in g.standings(Y,T)[:40]]
    act={}
    for u in top:
        rs=[(e['N'],r[2]) for e in g.EV.values() if e['N'] and T<=e['date']<f'{Y+1}-01-01' and e['kind']!='serial_final' for r in e['rows'] if r[0]==u and r[2] and r[2]<1000]
        if len(rs)>=2: act[u]=(np.mean([p<=5 for N,p in rs]),np.mean([p<=10 for N,p in rs]),len(rs))
    for tau,C in ((0.4,1.4),(0.25,1.4),(0.4,1.0),(0.25,1.0),(0.15,1.0)):
        S=s2.Strength(T,tau=tau,rho=0.5); 
        vals=np.array([S.beta[u] for u in S.beta]); pool=set(top)
        bg=np.array([b for u,b in S.beta.items() if u not in pool]+[S.default]*int(0.6*len(S.beta)))
        pred={u:implied(S.fwd(u),S.sd(u),bg,C,S=600) for u in act}
        p5=np.array([pred[u][0] for u in act]); a5=np.array([act[u][0] for u in act]); n=np.array([act[u][2] for u in act])
        p10=np.array([pred[u][1] for u in act]); a10=np.array([act[u][1] for u in act])
        hi=p5>=0.5
        print(f"{Y} τ={tau} C={C}: игроков {len(act)}; топ-5 предск {np.average(p5,weights=n):.2f} факт {np.average(a5,weights=n):.2f} | у кого предск ≥0.5 ({hi.sum()}): предск {np.average(p5[hi],weights=n[hi]) if hi.any() else 0:.2f} факт {np.average(a5[hi],weights=n[hi]) if hi.any() else 0:.2f} | топ-10 предск {np.average(p10,weights=n):.2f} факт {np.average(a10,weights=n):.2f} | max предск топ-5 {p5.max():.2f}")
