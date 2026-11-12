import format_sim as sim
sim.P['c']=0.065; sim.P['sd']=0.2
def show(tag,N,fmt,reps=600):
    m=sim.metrics(N,fmt,reps,seed=5)
    print(f"{tag:34s} N={N:3d} | top10→финал {m['top10']:.2f} | сильнейший в финале {m['bestfin']:.2f} | сильнейший побеждает {m['win']:.2f} | победитель из топ-3 {m['wintop3']:.2f} | MMR финала {m['finmmr']:.0f} | MMR победителя {m['winmmr']:.0f}",flush=True)
print('== Q1 размер, формат как сейчас (кратно 10: 12+4; кратно 11: 10+4)')
for N in (30,33,40,44,50,55,60,66,80,100,120,150): show('сейчас',N,{})
print('== Q1b 33/44/55 с полуфиналом (10 квал + ПФ 20 чел 2 игры + финал 4)')
for N in (33,44,55,66): show('10+ПФ2+4',N,{'sf':20,'sfG':2})
