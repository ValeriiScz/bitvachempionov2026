"""build_race.py · v1.3 · 2026-09-21 (TARGET 4.0, планы игроков players_expert, финалы 2★ на 10 мест) · v1.2 (T/OUT из gd_cfg) · v1.1 · 2026-09-17 (v1.0 — 2026-09-14) — собирает data/race2026.js для страницы «Гонка за золотую дюжину» из результатов модели.
Вход: tickets2026.json, plan2026.json, scenarios3.json, леджеры. Выход: window.RACE = {...}
v1.1: у игроков sim три оценки силы — beta (вся история с 2024, веса 1/.5/.25), b12 (12 месяцев), b26 (только 2026) — для переключателя «Форма» в генераторе."""
import json, numpy as np, gd_data as g, gd_sim
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
planks={'floor':115,'usual':round(SC['1 обычный ритм']['thr_med']),'usual_lo':round(SC['1 обычный ритм']['thr10']),'usual_hi':round(SC['1 обычный ритм']['thr90']),
        'active':round(SC['2 активно и стараются']['thr_med']),'beast':round(SC['3 как звери']['thr_med']),'work':[140,150],'regs':[120,130],'regs_note':'только уже записанные + финалы серийников'}
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
    players.append({'uid':u,'nick':g.NICK[u],'rank':se.race.get(u),'base':[[p,sf] for p,sf in se.base[u]],'beta':round(float(se.beta.get(u,se.default)),3),
                    'b12':round(float(B12.get(u,D12)),3),'b26':round(float(B26.get(u,D26)),3),
                    'p':[round(float(e['p'][u]),3) for e in regs_ev],'reg':[e['regs'].get(u) if e['regs'].get(u) is not None else -1 for e in regs_ev]})
sim_events=[{'id':e['id'],'date':e['date'],'stars':e['stars'],'N':e['N'],'grid':[float(x) for x in se.grid_pts(e['stars'],e['type'],e['N'])]} for e in regs_ev]
sim_cont=[{'id':c['id'],'name':SHORT.get(c['name'][:10],c['name']),'fin':{str(u):round(p,2) for u,p in c['fin'].items() if u in set(simpool)},'cand':{str(u):round(p,2) for u,p in c['cand'].items() if u in set(simpool)},
           'part':[u for u in c['part'] if u in set(simpool)],'grid':c['grid'],'base':c['base'],'nfin_all':len(c['fin']),'ncand_all':round(sum(c['cand'].values()),1),
           'ext':{'n':len([u for u in c['fin'] if u not in set(simpool)]),'p':round(float(np.mean([p for u,p in c['fin'].items() if u not in set(simpool)])) if any(u not in set(simpool) for u in c['fin']) else 0,2),
                  'beta':round(float(np.mean([se.beta.get(u,se.default) for u in c['fin'] if u not in set(simpool)])) if any(u not in set(simpool) for u in c['fin']) else float(se.default),2),
                  'ncand':round(float(sum(p for u,p in c['cand'].items() if u not in set(simpool))),1)}} for c in cont_ev]
rng=np.random.default_rng(0); bg=[round(float(x),2) for x in rng.choice(se.bg,200)]
SIM={'players':players,'forms':{'all':'вся история (с 2024, свежее — весомее)','y12':'последние 12 месяцев','y26':'только 2026 год'},'events':sim_events,'contours':sim_cont,'bg':bg,'C':gd_sim.C,'top30_mean':4.0,'top20_mean':5.5,'levels':{'обычно':[1.0,0.0],'стараются':[6/5.5,0.35],'максимум':[6.5/5.5,0.7]},
     'server':{'S':F.get('S',3000),'date':T,'p12':{str(r['uid']):round(r['p12'],3) for r in F['rows']}}}
RACE={'snapshot':T,'sim':SIM,'thr12_now':mid[11][0],'planks':planks,'events':events,'rows':rows,'hist':hist,
      'method':'Σ = 10 лучших турниров года, не более 2 серийных. Финал = 6–10 место на 4★ ≈ 12 баллов, топ-5 на 4★ ≈ 24. Частоты — за последние 12 месяцев, сглажены к среднему топ-30.'}
open(OUTP('race2026.js'),'w',encoding='utf-8').write('/* race2026.js — данные страницы «Гонка за золотую дюжину». Генератор: _scripts_golden_dozen_v0.9/build_race.py. Руками не править. */\nwindow.RACE='+json.dumps(RACE,ensure_ascii=False,separators=(',',':'))+';\n')
import os; print('race2026.js', os.path.getsize(OUTP('race2026.js'))//1024,'КБ; планки',planks,'; игроков',len(rows),'; событий',len(events))
