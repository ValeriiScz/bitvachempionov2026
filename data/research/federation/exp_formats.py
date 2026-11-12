import format_sim as sim, numpy as np
sim.P['c']=0.065; sim.P['sd']=0.2
# multi-stage generic: stage2 = 'sf' with cut and games
F={
 'База 12+4':{'G':12},
 'База 10+4':{'G':10},
 'Швейцарка с 7-го тура':{'G':12,'swiss':6},
 'Швейцарка с 4-го тура':{'G':12,'swiss':3},
 '16+4':{'G':16},
 '20+4':{'G':20},
 '12+6 финал':{'G':12,'FG':6},
 '12+8 финал':{'G':12,'FG':8},
 '12+4 финал с нуля':{'G':12,'freset':1},
 '10+ПФ(20ч,2)+4':{'G':10,'sf':20,'sfG':2},
 '10+ПФ(20ч,4)+4':{'G':10,'sf':20,'sfG':4},
 '3 дня: 16+ПФ(20ч,4)+6':{'G':16,'sf':20,'sfG':4,'FG':6},
 '3 дня швейц: 16шв+ПФ(20,4)+6':{'G':16,'swiss':6,'sf':20,'sfG':4,'FG':6},
 '2 этапа: 12 → топ-30 ещё 8 → финал 6':{'G':12,'sf':30,'sfG':8,'FG':6},
}
import sys
for N in [int(x) for x in sys.argv[1:]]:
    print('== N',N,flush=True)
    for k,f in F.items():
        m=sim.metrics(N,f,1200,seed=9)
        print(f"{k:38s} top10→финал {m['top10']:.2f} | сильнейший в финале {m['bestfin']:.2f} | побеждает {m['win']:.2f} | победитель топ-3 {m['wintop3']:.2f} | MMR финала {m['finmmr']:.0f}",flush=True)
