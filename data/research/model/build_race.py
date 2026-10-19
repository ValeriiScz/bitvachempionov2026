"""build_race.py · v2.0 · 2026-10-19 (сила v2 из gd_strength2: ELO/σ/форма в RACE.rows[].sd; коридор «по результатам ↔ по маркерам» для n_eff<10; пул баллов по выходным RACE.pool; ожидаемые баллы за старт; p12/Σ сервера v2) · v1.5 · 2026-10-13 (рабочая планка: нижняя граница вниз до 5, верхняя вверх, ширина ≥5) · v1.4 · 2026-10-13 (планки считаются из сценариев 0–3; уровни генератора — только явка) · v1.3 · 2026-09-21 (TARGET 4.0, планы игроков players_expert, финалы 2★ на 10 мест) · v1.2 (T/OUT из gd_cfg) · v1.1 · 2026-09-17 (v1.0 — 2026-09-14) — собирает data/race2026.js для страницы «Гонка за золотую дюжину» из результатов модели.
Вход: tickets2026.json, plan2026.json, scenarios3.json, леджеры. Выход: window.RACE = {...}
v1.1: у игроков sim три оценки силы — beta (вся история с 2024, веса 1/.5/.25), b12 (12 месяцев), b26 (только 2026) — для переключателя «Форма» в генераторе."""
import json, collections, numpy as np, gd_data as g, gd_sim, gd_strength2
from gd_sim import Season
from gd_cfg import T, out as OUTP
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
import calendar_expert, players_expert
gd_sim.EVENT_WEIGHT=calendar_expert.W; gd_sim.TARGET_TOP30_MEAN=4.0; gd_sim.TARGET_TOP20_MEAN=5.5; gd_sim.RACE_BETA_SHIFT=0; gd_sim.PLAYER_TARGET=players_expert.TARGET
se=Season(2026,T,cal_future=fut,verbose=False)
SHORT={'German Maf':'GMC','"Mafia Cha':'MCL','Poland Str':'PSP','White Mafi':'White Mafia','Arena Mold':'Arena Moldova','Васлуйская':'Васлуй','ЛЗГ Лига З':'ЛЗГ','Benelux Pl':'Benelux','Cyprus Maf':'Cyprus MS','Central Eu':'CEC'}
TK=json.load(open(OUTP('tickets2026.json'))); F=json.load(open(OUTP('forecast2026.json')))
for r in TK['rows']:
    for f in r['finals']: f['name']=SHORT.get(f['name'],f['name']); PL=json.load(open(OUTP('plan2026.json'))); SC=json.load(open(OUTP('scenarios3.json')))
plan={r['uid']:r for r in PL['rows']}; tick={r['uid']:r for r in TK['rows']}
mid=g.standings(2026,T)
# планки
r5=lambda x:int(5*round(x/5))
S0,S1,S2,S3=SC['0 только заявки'],SC['1 обычный ритм'],SC['2 ездят активно'],SC['3 ездят по максимуму']
# v1.4 (13.10.2026): все планки считаются, а не вписаны руками (раньше floor 115, work 140–150, regs 120–130 стояли константами с 21.09)
import math
_lo=5*math.floor(S1['thr_med']/5); _hi=max(5*math.ceil(S2['thr_med']/5),_lo+5)   # v1.5: вниз/вверх до 5 и не меньше 5 баллов ширины (было «155–155»)
_work=[_lo,_hi]
planks={'floor':round(S0['thr10']),'usual':round(S1['thr_med']),'usual_lo':round(S1['thr10']),'usual_hi':round(S1['thr90']),
        'active':round(S2['thr_med']),'beast':round(S3['thr_med']),'work':_work,'regs':[r5(S0['thr25']),r5(S0['thr75'])],
        'regs_note':'только уже записанные + финалы серийников'}
# турниры впереди
events=[]
for e in sorted(se.events,key=lambda e:e['date']):
    if e['type']=='contour':
        events.append({'id':e['id'],'date':e['date'],'name':e['name'],'stars':e['stars'],'kind':'final','grid_max':e['grid'][0],'grid_min':(e['grid'][min(len(e['grid']),len(e['fin']))-1] if len(e['fin'])<=len(e['grid']) else e['base']) if e['fin'] else e['base'],'field':e.get('size'),'n_fin':len(e['fin']),'fin':[g.NICK.get(u,'?') for u in e['fin'] if se.race.get(u,999)<=40],'short':SHORT.get(e['name'][:10],e['name'])})
    else:
        grid=se.grid_pts(e['stars'],e['type'],e['N'])
        events.append({'id':e['id'],'date':e['date'],'name':e['name'],'stars':e['stars'],'kind':e['type'],'country':e['country'],'N':e['N'],'g1':grid[0],'g5':grid[min(4,len(grid)-1)],'g10':grid[min(9,len(grid)-1)],'regs':[g.NICK.get(u,'?') for u in e['regs'] if se.race.get(u,999)<=30]})
def words(z,y):
    p=[]
    if z: p.append(f"{z} топ-5")
    if y: p.append(f"{y} финал{'а' if y in (2,3,4) else ''}")
    return ' + '.join(p) if p else 'уже есть'
rows=[]
for i,(s,u) in enumerate(mid[:40]):
    t=tick.get(u); p=plan.get(u)
    base=se.base[u]; ten=sorted([x for x,_ in base],reverse=True)
    regs=[{'id':e['id'],'date':e['date'],'name':e['name'],'stars':e['stars'],'N':e['N'],'c':e['regs'].get(u)} for e in se.events if e['type']!='contour' and e['regs'].get(u) is not None]
    rec={'uid':u,'nick':g.NICK[u],'rank':i+1,'sigma':s,'ten':ten[:10],'base':[[p,sflag] for p,sflag in base],'tail':sum(ten[5:10]) if len(ten)>=10 else 0,'free':max(0,10-len(ten)),'country':g.COUNTRY.get(u),'regs':regs}
    if t:
        rec.update({'n12m':t['n12m'],'p10':round(t['p10'],2),'p5':round(t['p5'],2),'finals':t['finals'],
                    'need':{k:{'top5':v['top5'],'final':v['final'],'words':words(v['top5'],v['final']),'of5':min(5,v['top5']+v['final'])} for k,v in t['need'].items()}})
    if p:
        rec.update({'hist_median_pct':p['hist_median_pct'],'expected_k':p['expected_k'],'likely':p['likely_events'][:6],'table':p['table'],'one_result':p['one_result']})
    rows.append(rec)
# ---- v2.0: сила v2, коридор, пул баллов, запасы/потоки ----
ST=se.strength; rank={u:i+1 for i,(s_,u) in enumerate(mid)}
res_main=se.run(S=2000,seed=11,frailty=None); pool_=res_main['pool']; ix={u:i for i,u in enumerate(pool_)}
low=[u for s_,u in mid[:40] if ST.neff.get(u,0)<10]
import copy
se_pr=copy.copy(se); se_pr.beta=dict(se.beta)
for u in low: se_pr.beta[u]=ST.mu.get(u,ST.default)
res_pr=se_pr.run(S=1500,seed=11,frailty=None)
# ожидаемые баллы за один старт на 4★ при поле 40 (сила с σ, фон из пула) — «поток» баллов
rng2=np.random.default_rng(3); grid4=se.grid_pts(4,'regular',40)
def exp_pts(u,S=3000):
    b=se.beta.get(u,se.default); sd=se.sigma.get(u,se.default_sigma); tot=0; t5=0; t10=0
    for _ in range(S):
        bb=(b+sd*rng2.standard_normal())*gd_sim.C; others=rng2.choice(se.bg,39)*gd_sim.C
        perf=np.concatenate([[bb],others])+rng2.gumbel(size=40); r=int((perf>perf[0]).sum())+1
        tot+=grid4[min(r,len(grid4))-1]; t5+=r<=5; t10+=r<=10
    return tot/S, t5/S, t10/S
import gd_attend
rates,n_ev,_byc=gd_attend.player_rates(se.pool,T)
for rec in rows:
    u=rec['uid']; t=ST.table([u])[0]; i=ix[u]
    ep,q5,q10=exp_pts(u)
    rec['sd']={'elo':round(t['elo']) if t['elo'] else None,'tier':None,
        'mu':t['mu'],'beta_long':t['beta_long'],'sigma':t['sigma'],'n_eff':t['n_eff'],'form':t['form'],'n_season':t['n_season'],'beta_fwd':t['beta_fwd'],
        'low_n':u in low,'p12':round(float(res_main['p12'][i]),3),'sum_exp':round(float(res_main['sums'][:,i].mean()),1),'sum_p10':round(float(np.percentile(res_main['sums'][:,i],10)),1),'sum_p90':round(float(np.percentile(res_main['sums'][:,i],90)),1),
        'played_exp':round(float(res_main['played'][i]),2),'new_reg':round(float(res_main['new_reg'][i]),1),'new_ser':round(float(res_main['new_ser'][i]),1),
        'p12_prior':round(float(res_pr['p12'][i]),3) if u in low else None,'sum_prior':round(float(res_pr['sums'][:,i].mean()),1) if u in low else None,
        'pts_per_start':round(ep,1),'q5':round(q5,2),'q10':round(q10,2),
        'starts_365':int(round(rates[u][0]-0.5)),'starts_105':int(round(rates[u][2]-0.5)),'n_ev_365':n_ev,'plan':gd_sim.PLAYER_TARGET.get(u),
        'race_boost':rank.get(u,999)<=25,'no_regs':len([e for e in se.events if e['type']!='contour' and e['regs'].get(u) is not None])==0,'n_regs':len([e for e in se.events if e['type']!='contour' and e['regs'].get(u) is not None]),
        'finals_q':[SHORT.get(c['name'][:10],c['name']) for c in se.events if c['type']=='contour' and u in c['fin']],
        'finals_c':[SHORT.get(c['name'][:10],c['name']) for c in se.events if c['type']=='contour' and u in c['cand']]}
for rec in rows:
    tv=(__import__('gd_strength2').ELO.get(rec['uid']) or {}); rec['sd']['tier']=tv.get('tier'); rec['sd']['elo_date']=tv.get('date_all')
thr_main=res_main['thr']*1.07
# пул баллов по выходным (один турнир в день): лучшее событие даты по топ-5
by_date=collections.OrderedDict()
for e in events:
    by_date.setdefault(e['date'],[]).append(e)
pool_days=[]
for d,evs in by_date.items():
    regs_=[e for e in evs if e['kind']!='final']; fins_=[e for e in evs if e['kind']=='final']
    best=max(regs_,key=lambda e:(e['g5'],e['g1'])) if regs_ else None
    pool_days.append({'date':d,'events':[{'id':e['id'],'short':e.get('short') or e['name'][:28],'name':e['name'],'stars':e['stars'],'kind':e['kind'],'country':e.get('country'),'N':e.get('N'),'g1':e.get('g1'),'g5':e.get('g5'),'g10':e.get('g10'),'grid_max':e.get('grid_max'),'grid_min':e.get('grid_min'),'n_fin':e.get('n_fin'),'field':e.get('field'),'n_regs30':len(e.get('regs') or []),'fin':e.get('fin')} for e in evs],
                      'best':best['id'] if best else None,'max1':best['g1'] if best else 0,'max5':best['g5'] if best else 0,'max10':best['g10'] if best else 0,'finals':[f['id'] for f in fins_]})
RACE_POOL={'days':pool_days,'note':'один турнир в день: в каждую дату берём лучший по сетке; финалы серийников — только тем, кто прошёл'}
hist={'note':'после ЧМ 2024 и 2025: доля прошедших в дюжину по Σ относительно 12-го места на тот момент',
      'bands':[{'band':'выше порога на 35%+','k':8,'n':8},{'band':'выше на 15–35%','k':2,'n':2},{'band':'около порога (−5…+15%)','k':8,'n':14},{'band':'ниже на 5–25%','k':2,'n':10},{'band':'ниже на 25–40%','k':4,'n':19}]}
# ---- данные для клиентского генератора сезонов ----
import numpy as np
regs_ev=[e for e in se.events if e['type']!='contour']; cont_ev=[e for e in se.events if e['type']=='contour']
simpool=[u for s_,u in mid[:60]]
# альтернативные окна оценки силы: 12 месяцев и только 2026 (веса 1.0, та же усадка)
import datetime
from gd_strength import rankings_before, fit_pl
def beta_window(since):
    Td=datetime.date.fromisoformat(T); rk=[]
    for e in g.EV.values():
        if not e['N'] or e['date']>=T or e['date']<since: continue
        rows=[r for r in e['rows'] if r[2] is not None and r[2]<1000]; rows.sort(key=lambda r:r[2])
        if len(rows)<6: continue
        rk.append((1.0,[r[0] for r in rows]))
    b=fit_pl(rk,lam=gd_sim.LAM); d=float(np.percentile(np.array(list(b.values())),30))
    return b,d,len(rk)
B12,D12,N12=beta_window((datetime.date.fromisoformat(T)-datetime.timedelta(days=365)).isoformat())
B26,D26,N26=beta_window('2026-01-01')
print('окна силы: всё',len(se.beta),'игроков; 12м',N12,'турниров; 2026',N26,'турниров')
players=[]
for u in simpool:
    players.append({'uid':u,'nick':g.NICK[u],'rank':se.race.get(u),'base':[[p,sf] for p,sf in se.base[u]],'beta':round(float(se.beta.get(u,se.default)),3),'sig':round(float(se.sigma.get(u,se.default_sigma)),3),
                    'b12':round(float(B12.get(u,D12)),3),'b26':round(float(B26.get(u,D26)),3),
                    'p':[round(float(e['p'][u]),3) for e in regs_ev],'reg':[e['regs'].get(u) if e['regs'].get(u) is not None else -1 for e in regs_ev]})
sim_events=[{'id':e['id'],'date':e['date'],'stars':e['stars'],'N':e['N'],'grid':[float(x) for x in se.grid_pts(e['stars'],e['type'],e['N'])]} for e in regs_ev]
sim_cont=[{'id':c['id'],'name':SHORT.get(c['name'][:10],c['name']),'fin':{str(u):round(p,2) for u,p in c['fin'].items() if u in set(simpool)},'cand':{str(u):round(p,2) for u,p in c['cand'].items() if u in set(simpool)},
           'part':[u for u in c['part'] if u in set(simpool)],'grid':c['grid'],'base':c['base'],'nfin_all':len(c['fin']),'ncand_all':round(sum(c['cand'].values()),1),
           'ext':{'n':len([u for u in c['fin'] if u not in set(simpool)]),'p':round(float(np.mean([p for u,p in c['fin'].items() if u not in set(simpool)])) if any(u not in set(simpool) for u in c['fin']) else 0,2),
                  'beta':round(float(np.mean([se.beta.get(u,se.default) for u in c['fin'] if u not in set(simpool)])) if any(u not in set(simpool) for u in c['fin']) else float(se.default),2),
                  'ncand':round(float(sum(p for u,p in c['cand'].items() if u not in set(simpool))),1)}} for c in cont_ev]
rng=np.random.default_rng(0); bg=[round(float(x),2) for x in rng.choice(se.bg,200)]
SIM={'players':players,'forms':{'all':'вся история (с 2024, свежее — весомее)','y12':'последние 12 месяцев','y26':'только 2026 год'},'events':sim_events,'contours':sim_cont,'bg':bg,'C':gd_sim.C,'top30_mean':2.5,'top20_mean':2.5,'levels':{'обычно':[1.0,0.0],'стараются':[1.5,0.0],'максимум':[2.5,0.0]},
     'server':{'S':F.get('S',3000),'date':T,'p12':{str(r['uid']):round(r['p12'],3) for r in F['rows']}}}
RACE={'snapshot':T,'sim':SIM,'thr12_now':mid[11][0],'planks':planks,'events':events,'rows':rows,'hist':hist,'pool':RACE_POOL,
      'model':{'version':'v2.2 · 20.10.2026','attendance':'заявки × дни до старта (история календаря 26.08–19.10) + петля R1 в розыгрыше','lead_none':gd_sim.LEAD_NONE,'lead_conf':gd_sim.LEAD_CONF,'r1':[gd_sim.R1_NEAR,gd_sim.R1_FAR,gd_sim.R1_UP,gd_sim.R1_DOWN],'strength':'gd_strength2','tau':gd_strength2.TAU,'rho':gd_strength2.RHO_FORM,'C':gd_sim.C,'race_boost':gd_sim.RACE_BOOST,'elo_fit':ST.info,'thr_v2':{'med':float(np.median(thr_main)),'p10':float(np.percentile(thr_main,10)),'p90':float(np.percentile(thr_main,90))},'target':{'top20':5.5,'top30':4.0},'S':2000},
      'method':'Σ = 10 лучших турниров года, не более 2 серийных. Финал = 6–10 место на 4★ ≈ 12 баллов, топ-5 на 4★ ≈ 24. Частоты — за последние 12 месяцев, сглажены к среднему топ-30.'}
open(OUTP('race2026.js'),'w',encoding='utf-8').write('/* race2026.js — данные страницы «Гонка за золотую дюжину». Генератор: _scripts_golden_dozen_v0.9/build_race.py. Руками не править. */\nwindow.RACE='+json.dumps(RACE,ensure_ascii=False,separators=(',',':'))+';\n')
import os; print('race2026.js', os.path.getsize(OUTP('race2026.js'))//1024,'КБ; планки',planks,'; игроков',len(rows),'; событий',len(events))
