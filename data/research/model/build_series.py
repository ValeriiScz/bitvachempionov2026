"""build_series.py · v1.1 · 2026-09-21 (T из gd_cfg, не сегодня) · v1.0 · 2026-09-15 — data/series2026.js для раздела «Серийники»: по каждому рейтинговому серийнику 2026 —
описание/правило прохода, финал, серии (сыграно/впереди), кто уже прошёл (с местом в гонке), ближайшие серии всех контуров."""
import json, datetime, collections, gd_data as g, gd_sim
from gd_sim import Season
from gd_cfg import T, out as OUTP
Season.FINALISTS_PLAY=True
fut=[t for t in g.CAL['tournaments'] if t['start']>T and not t.get('cancelled') and t['pts']]
gd_sim.EVENT_WEIGHT={}; gd_sim.TARGET_TOP30_MEAN=None; gd_sim.RACE_BETA_SHIFT=0
se=Season(2026,T,cal_future=fut,verbose=False)
race=se.race
META={
 664:{'short':'GMC Europa 2026','tag':'German Mafia Cup','rule':'в финал проходят 1-е и 2-е места каждой серии; замены — 3-и места по сумме допов','rule_src':'FACT: описание турнира','final':'14–15.11, Кёльн','final_size':'50–60 человек, 18 игр','prize':'от 2500–3000 €, взнос финала 100 €','planned':'25–30 серий','page':'gmc2026.html'},
 757:{'short':'MCL Europe 2026','tag':'Mafia Champions League','rule':'средний балл за серию (минимум 2 серии): Central Europe — 6 мест из 12 серий, Israel — 3 через полуфинал 3.10, Cyprus — 1','rule_src':'FACT: регламент в канале лиги','final':'21–22.11, Прага','final_size':'10 финалистов, 5 судей','prize':'2200 € (800/600/400/200/200)','planned':'12 + 5 + 3 серии','page':'mcl2026.html'},
 639:{'short':'Poland Strongest Player','tag':'PSP-26','rule':'12 финалистов из 6 серий — топ-2 каждой серии','rule_src':'ВЫВОД из описания (12 из 6 серий)','final':'17.10, Варшава (по описанию; в календаре 10.10)','final_size':'12 человек, 2 дня, 18 игр','prize':'2200 zł (1000/600/400 + 200 MVP)','planned':'6 серий'},
 645:{'short':'White Mafia Best Player','tag':'WMC Krakow','rule':'топ-2 каждой серии; заменяющие играют без рейтинговых баллов','rule_src':'FACT: регламент турнира','final':'7–8.11, Вроцлав','final_size':'12 человек, 18 игр','prize':'600 € (250/150/100 + 100 MVP)','planned':'6 серий, все до 5.10'},
 685:{'short':'Arena Moldova Cup','tag':'Decem / mafia.md','rule':'из каждой серии двое: 1-е место и MVP серии (если это один человек — 2-е место)','rule_src':'FACT: описание турнира','final':'28–29.11, Кишинёв','final_size':'взнос финала 100 €','prize':'—','planned':'9 серий'},
 740:{'short':'Benelux Plus 2026','tag':'Brussels / Sova','rule':'сумма двух лучших серий, минимум две сыгранные; топ-10 зачёта — в финал','rule_src':'FACT: регламент турнира','final':'19–20.12, Брюссель','final_size':'10 человек','prize':'1000 € (500/300/200)','planned':'10 серий, все до 20.11'},
 749:{'short':'ЛЗГ — Лига Западной Германии','tag':'MC Cologne','rule':'топ-2 каждой серии','rule_src':'ГИПОТЕЗА: описание пустое; в 2025 топ-2 серий = финалисты 7 из 7','final':'5.12, Кёльн','final_size':'10 человек','prize':'660 € (по mafgame)','planned':'7 серий'},
 670:{'short':'Васлуйская Битва 2026','tag':'mafia.md','rule':'топ-2 каждой серии','rule_src':'ГИПОТЕЗА: описание пустое; в 2025 — 1-е и 2-е места серий','final':'5.12, Кишинёв','final_size':'10 человек','prize':'—','planned':'7 серий'},
 579:{'short':'Cyprus Mafia Series 2026','tag':'Limassol','rule':'правило не опубликовано; в 2025 (Limassol Cup) топ-2 серий совпал с финалом лишь наполовину — вероятно, зачёт по сумме или среднему','rule_src':'ГИПОТЕЗА','final':'11.10, Лимассол','final_size':'10 человек','prize':'—','planned':'9 серий'},
}
GRID2=[30,27,25,22,20,18,16,14,12,10,8,6]; GRID4=[42,39,37,34,32,30,28,26,24,22,20,16,14,10,8]
out=[]; upcoming=[]
horizon=(datetime.date.fromisoformat(T)+datetime.timedelta(days=16)).isoformat()
for c in se.events:
    if c['type']!='contour': continue
    pid=c['id']; d=g.SER[pid]; m=META.get(pid,{})
    ser=sorted(d['series'],key=lambda s:s['start_date'])
    played=[s for s in ser if s['rows']]; ahead=[s for s in ser if not s['rows'] and s['start_date']>=T]; stale=[s for s in ser if not s['rows'] and s['start_date']<T]
    players=len({r[0] for s in played for r in s['rows']})
    qual=sorted([{'uid':u,'nick':g.NICK.get(u,'?'),'rank':race.get(u)} for u in c['fin']],key=lambda x:(x['rank'] or 999))
    nxt=[{'id':s['id'],'date':s['start_date'],'city':s['city'],'country':s['country'],'name':s['name'],'regs':len(s['regs']),'exp':s.get('expected') or 10} for s in ahead]
    for s in nxt:
        if s['date']<=horizon: upcoming.append(dict(s,contour=m.get('short',d['name']),pid=pid,stars=d['stars']))
    grid=GRID4 if d['stars']>=4 else GRID2
    out.append({'id':pid,'name':d['name'],'short':m.get('short',d['name']),'tag':m.get('tag',''),'stars':d['stars'],'city':g.TID[pid].get('city'),'country':g.TID[pid].get('country'),
                'final_date':d['start_date'],'final':m.get('final',''),'final_size':m.get('final_size',''),'prize':m.get('prize',''),'planned':m.get('planned',''),
                'rule':m.get('rule',''),'rule_src':m.get('rule_src',''),'page':m.get('page'),
                'series_total':len(ser),'series_played':len(played),'series_ahead':len(ahead),'series_stale':[{'date':x['start_date'],'city':x['city']} for x in stale],'players':players,
                'qualified':qual,'next':nxt,'points':{'max':grid[0],'min':grid[-1],'base':c['base']},
                'mafgame':f'https://mafgame.org/tournaments/{pid}/view'})
out.sort(key=lambda x:(-x['stars'],x['final_date']))
upcoming.sort(key=lambda s:s['date'])
S={'snapshot':T,'contours':out,'upcoming':upcoming,'horizon_days':16}
open(OUTP('series2026.js'),'w',encoding='utf-8').write('/* series2026.js — данные раздела «Серийники». Генератор: _scripts_golden_dozen_v0.9/build_series.py (снимки серий — робот fetch_series). Руками не править. */\nwindow.SERIES='+json.dumps(S,ensure_ascii=False,separators=(',',':'))+';\n')
import os; print(os.path.getsize(OUTP('series2026.js'))//1024,'КБ; контуров',len(out),'; ближайших серий',len(upcoming))
for c in out: print(f"  {c['short']:28s} {c['stars']}★ серий {c['series_played']}/{c['series_total']} впереди {c['series_ahead']} прошли {len(c['qualified'])} игроков {c['players']}")
for u in upcoming: print('   ',u['date'],u['contour'][:20],u['city'],'заявок',u['regs'])
