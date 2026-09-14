"""build_race.py · v1.0 · 2026-09-14 — собирает data/race2026.js для страницы «Гонка за золотую дюжину» из результатов модели.
Вход: tickets2026.json, plan2026.json, scenarios3.json, леджеры. Выход: window.RACE = {...}"""
import json, numpy as np, gd_data as g, gd_sim
from gd_sim import Season
T='2026-09-14'; Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
gd_sim.EVENT_WEIGHT={}; gd_sim.TARGET_TOP30_MEAN=None; gd_sim.RACE_BETA_SHIFT=0
se=Season(2026,T,cal_future=fut,verbose=False)
SHORT={'German Maf':'GMC','"Mafia Cha':'MCL','Poland Str':'PSP','White Mafi':'White Mafia','Arena Mold':'Arena Moldova','Васлуйская':'Васлуй','ЛЗГ Лига З':'ЛЗГ','Benelux Pl':'Benelux','Cyprus Maf':'Cyprus MS','Central Eu':'CEC'}
TK=json.load(open('tickets2026.json'))
for r in TK['rows']:
    for f in r['finals']: f['name']=SHORT.get(f['name'],f['name']); PL=json.load(open('plan2026.json')); SC=json.load(open('scenarios3.json'))
plan={r['uid']:r for r in PL['rows']}; tick={r['uid']:r for r in TK['rows']}
mid=g.standings(2026,T)
# планки
planks={'floor':115,'usual':round(SC['1 обычный ритм']['thr_med']),'usual_lo':round(SC['1 обычный ритм']['thr10']),'usual_hi':round(SC['1 обычный ритм']['thr90']),
        'active':round(SC['2 активно и стараются']['thr_med']),'beast':round(SC['3 как звери']['thr_med']),'work':[140,150]}
# турниры впереди
events=[]
for e in sorted(se.events,key=lambda e:e['date']):
    if e['type']=='contour':
        events.append({'id':e['id'],'date':e['date'],'name':e['name'],'stars':e['stars'],'kind':'final','grid_max':e['grid'][0],'grid_min':e['grid'][min(len(e['grid']),len(e['fin']))-1] if e['fin'] else e['base'],'n_fin':len(e['fin']),'fin':[g.NICK.get(u,'?') for u in e['fin'] if se.race.get(u,999)<=40],'short':SHORT.get(e['name'][:10],e['name'])})
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
    rec={'uid':u,'nick':g.NICK[u],'rank':i+1,'sigma':s,'ten':ten[:10],'tail':sum(ten[5:10]) if len(ten)>=10 else 0,'free':max(0,10-len(ten)),'country':g.COUNTRY.get(u)}
    if t:
        rec.update({'n12m':t['n12m'],'p10':round(t['p10'],2),'p5':round(t['p5'],2),'finals':t['finals'],
                    'need':{k:{'top5':v['top5'],'final':v['final'],'words':words(v['top5'],v['final']),'of5':min(5,v['top5']+v['final'])} for k,v in t['need'].items()}})
    if p:
        rec.update({'hist_median_pct':p['hist_median_pct'],'expected_k':p['expected_k'],'likely':p['likely_events'][:6],'table':p['table'],'one_result':p['one_result']})
    rows.append(rec)
hist={'note':'после ЧМ 2024 и 2025: доля прошедших в дюжину по Σ относительно 12-го места на тот момент',
      'bands':[{'band':'выше порога на 35%+','k':8,'n':8},{'band':'выше на 15–35%','k':2,'n':2},{'band':'около порога (−5…+15%)','k':8,'n':14},{'band':'ниже на 5–25%','k':2,'n':10},{'band':'ниже на 25–40%','k':4,'n':19}]}
RACE={'snapshot':T,'thr12_now':mid[11][0],'planks':planks,'events':events,'rows':rows,'hist':hist,
      'method':'Σ = 10 лучших турниров года, не более 2 серийных. Финал = 6–10 место на 4★ ≈ 12 баллов, топ-5 на 4★ ≈ 24. Частоты — за последние 12 месяцев, сглажены к среднему топ-30.'}
open('race2026.js','w',encoding='utf-8').write('/* race2026.js — данные страницы «Гонка за золотую дюжину». Генератор: _scripts_golden_dozen_v0.9/build_race.py. Руками не править. */\nwindow.RACE='+json.dumps(RACE,ensure_ascii=False,separators=(',',':'))+';\n')
import os; print('race2026.js', os.path.getsize('race2026.js')//1024,'КБ; планки',planks,'; игроков',len(rows),'; событий',len(events))
