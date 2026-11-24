"""finish.py · v1.2 · 2026-11-25 (forecast: прогнозные места по турнирам - старт «Конструктора») · v1.1 · 2026-11-25 (сетка 15 мест - для «Сыграй расклад» на странице) · v1.0 · 2026-11-23 - «Финишная прямая» гонки за Золотую Дюжину: кто прошёл математически, кто борется и что кому нужно.
Шаг конвейера после build_race: читает открытый race2026.js (GD_OUT), считает блок finish и дописывает его в window.RACE.finish.
Что считает:
  1) статус каждого игрока:
     in_math  - остаётся в дюжине при ЛЮБЫХ результатах оставшихся турниров, даже если все соперники запишутся везде (точный перебор, MILP);
     in_regs  - остаётся в дюжине при любых результатах, если новых заявок не будет (соперники играют только то, куда уже записаны, и свои финалы серий);
     alive    - исход зависит от результатов;  out_math - не догоняет, даже выиграв всё, что успевает сыграть.
     Допущения перебора: игрок сам больше ничего не набирает; один турнир на выходные (пт-вс); одно место - один игрок; в зачёте 10 лучших,
     серийных не больше двух; равенство баллов считаем риском (не «прошёл»); сетки баллов - по ожидаемому числу участников.
  2) шансы по модели (та же gd_sim, что и вся гонка) и проходной балл: медиана и коридор 10-90%.
  3) условные шансы по ближайшему крупному турниру: если игрок там в топ-3 / в финале (4-10) / вне финала / не едет.
  4) «что нужно»: какое место на каком турнире выводит на проходной (медиана) и на надёжный (90%) балл.
Нужен scipy (точный перебор). Без scipy статусы in_math/in_regs считаются только грубой оценкой сверху (осторожно: «прошёл» не завышается).
Запуск: из data/research/model, GD_T=... GD_OUT=... python3 finish.py"""
import json, datetime, itertools, collections, re, sys, numpy as np
import gd_data as g, gd_sim, gd_strength2, calendar_expert, players_expert
from gd_cfg import T, adj, out as OUTP
from gd_sim import Season
try:
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import lil_matrix
    HAVE_MILP = True
except Exception:
    HAVE_MILP = False
gd_sim.EVENT_WEIGHT = calendar_expert.W; gd_sim.TARGET_TOP30_MEAN = 4.0; gd_sim.TARGET_TOP20_MEAN = 5.5; gd_sim.PLAYER_TARGET = players_expert.TARGET
Season.FINALISTS_PLAY = True
S = 1500; KMAX = 15; TOPN = 40
fut = [t for t in g.CAL['tournaments'] if t['start'] > T and not t.get('cancelled') and t['pts']]
se = Season(2026, T, cal_future=fut, verbose=False)
mid = g.standings(2026, T); rank = {u: i + 1 for i, (s, u) in enumerate(mid)}; cur = {u: s for s, u in mid}
now12 = mid[11][0] if len(mid) > 11 else 0.0; now13 = mid[12][0] if len(mid) > 12 else 0.0

def wk(d):
    x = datetime.date.fromisoformat(d); return str(x - datetime.timedelta(days=(x.weekday() - 4) % 7))   # пятница этих выходных
def short(n):
    n = re.sub(r'^Four Seasons[:.]?\s*', '', n).strip()
    for a, b in (('Cyprus Open 26: Winter', 'Cyprus Open Winter'), ('Dutch Open 2026', 'Dutch Open'), ('Васлуйская Битва 2026. Реванш.', 'Васлуй (финал серии)'),
                 ('ЛЗГ Лига Западной Германии 2026', 'ЛЗГ (финал серии)'), ('Benelux Plus 2026', 'Benelux (финал серии)'), ('Arena Moldova Cup', 'Arena Moldova (финал серии)')):
        n = n.replace(a, b)
    return n
EV = []
for e in sorted(se.events, key=lambda e: e['date']):
    fin = e['type'] == 'contour'
    gf = [float(x) for x in (e['grid'] if fin else se.grid_pts(e['stars'], e['type'], e['N']))]
    if fin: gf = gf + [float(e['base'])]          # вне сетки финала - базовые баллы участника серии
    grid = gf[:KMAX]
    EV.append({'id': e['id'], 'date': e['date'], 'wk': wk(e['date']), 'name': e['name'], 'short': short(e['name']), 'stars': e['stars'], 'fin': fin, 'ser': 1 if fin else 0, 'grid': grid, 'gridfull': gf,
               'N': e.get('size') if fin else e['N'], 'regs': set(e['fin']) if fin else set(e['regs']), 'elig': (set(e['fin']) | set(e['cand'])) if fin else None})
WEEKS = sorted(set(e['wk'] for e in EV))
base = {u: list(se.base[u]) for u in se.pool}

def can(u, e, regs_only):
    if e['fin']: return u in (e['regs'] if regs_only else e['elig'])
    return (u in e['regs']) if regs_only else True
def best_case(u, regs_only=False):
    """максимум Σ: лучший вариант на каждые выходные (1-е место), серийных побед в выборе не больше двух"""
    opts = []
    for w in WEEKS:
        o = [None] + [e for e in EV if e['wk'] == w and can(u, e, regs_only)]
        opts.append(o)
    best = cur.get(u, 0.0)
    for combo in itertools.product(*opts):
        add = [(e['grid'][0], 1 if e['fin'] else 0) for e in combo if e]
        best = max(best, g.best10(base[u] + add))
    return float(best)
MAXA = {u: best_case(u) for s, u in mid[:120] if u in base}
MAXR = {u: best_case(u, True) for s, u in mid[:120] if u in base}

def ten_asc(u):
    reg = sorted([p for p, s in base[u] if not s], reverse=True); sr = sorted([p for p, s in base[u] if s], reverse=True)
    bst = max((sr[:k] + reg[:10 - k] for k in range(0, min(2, len(sr)) + 1)), key=sum)
    b = sorted(bst); return [0.0] * (10 - len(b)) + b

def worst_case(X, regs_only):
    """Может ли X выпасть из дюжины? Возвращает (n_above_max, scenario|None, exact). Клинч = n_above_max < 12."""
    sx = cur[X]; mx = MAXR if regs_only else MAXA
    riv = [u for u in mx if u != X and mx[u] >= sx]
    already = [u for u in riv if cur[u] >= sx]
    if len(riv) < 12: return len(riv), None, True          # грубая оценка сверху уже доказывает
    if not HAVE_MILP: return len(riv), None, False
    M = len(WEEKS); var = []
    for pi, u in enumerate(riv):
        if cur[u] >= sx: continue
        for ti, e in enumerate(EV):
            if not can(u, e, regs_only): continue
            for k, v in enumerate(e['grid']):
                if v > 0: var.append((pi, ti, k, v))
    nv = len(var); NP = len(riv); offc = nv; offw = nv + NP * (M + 1); N = offw + NP
    rows = []; lo = []; hi = []
    slot = collections.defaultdict(list); pw = collections.defaultdict(list); pc = collections.defaultdict(list); pf = collections.defaultdict(list)
    for i, (pi, ti, k, v) in enumerate(var):
        slot[(ti, k)].append(i); pw[(pi, EV[ti]['wk'])].append(i); pc[pi].append(i)
        if EV[ti]['fin']: pf[pi].append(i)
    for idx in list(slot.values()) + list(pw.values()):
        rows.append({i: 1 for i in idx}); lo.append(0); hi.append(1)
    for pi, idx in pf.items():
        rows.append({i: 1 for i in idx}); lo.append(0); hi.append(2)
    BIG = 500
    for pi, u in enumerate(riv):
        ta = ten_asc(u); Sm = [sum(ta[:m]) for m in range(M + 1)]
        rows.append({offc + pi * (M + 1) + m: 1 for m in range(M + 1)}); lo.append(1); hi.append(1)
        r = {i: 1 for i in pc[pi]}; r.update({offc + pi * (M + 1) + m: -m for m in range(M + 1)}); rows.append(r); lo.append(0); hi.append(0)
        r = {i: var[i][3] for i in pc[pi]}; r.update({offc + pi * (M + 1) + m: -Sm[m] for m in range(M + 1)}); r[offw + pi] = -BIG
        rows.append(r); lo.append(sx - cur[u] - BIG); hi.append(np.inf)
    rows.append({offw + pi: 1 for pi in range(NP)}); lo.append(12); hi.append(np.inf)
    A = lil_matrix((len(rows), N))
    for ri, r in enumerate(rows):
        for ci, val in r.items(): A[ri, ci] = val
    c = np.zeros(N); c[:nv] = 1.0                                  # самый «дешёвый» сценарий: минимум нужных результатов
    res = milp(c, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=np.ones(N), bounds=Bounds(0, 1), options={'time_limit': 25})
    if res.x is None:
        return (11, None, True) if res.status == 2 else (len(riv), None, False)     # 2 = недопустимо: 12 обойти не могут
    x = res.x; plan = collections.defaultdict(list)
    for i, (pi, ti, k, v) in enumerate(var):
        if x[i] > 0.5: plan[riv[pi]].append({'ev': EV[ti]['short'], 'date': EV[ti]['date'], 'place': k + 1, 'pts': v})
    above = [riv[pi] for pi in range(NP) if x[offw + pi] > 0.5]
    scen = [{'nick': g.NICK.get(u, '?'), 'now': cur[u], 'res': sorted(plan.get(u, []), key=lambda r: r['date'])} for u in sorted(above, key=lambda u: -cur[u])]
    return len(above), scen, True

# ---- модель: шансы, проходной, условные шансы по ближайшему крупному турниру
reg_ev = [e for e in EV if not e['fin']]
key = None
if reg_ev:
    d0 = min(e['date'] for e in reg_ev if e['stars'] >= 3) if any(e['stars'] >= 3 for e in reg_ev) else reg_ev[0]['date']
    key = max((e for e in reg_ev if e['date'] == d0), key=lambda e: e['stars'])
r = se.run(S=S, seed=7, frailty=None, track=key['id'] if key else None)
pool = r['pool']; idx = {u: i for i, u in enumerate(pool)}; sums = r['sums']
order = np.argsort(-sums, axis=1); in12 = np.zeros_like(sums, dtype=bool)
for s in range(S): in12[s, order[s, :12]] = True
thr = adj(r['thr'], now12)
q = lambda p: float(np.percentile(thr, p))
plank = {'q10': round(q(10)), 'q25': round(q(25)), 'q50': round(q(50)), 'q75': round(q(75)), 'q90': round(q(90))}
def cond(u):
    if not key or u not in idx: return None
    i = idx[u]; rk = r['trkr'][:, i]; pl = r['trk'][:, i] >= 0; out = {}
    for name, m in (('top3', pl & (rk <= 3)), ('fin', pl & (rk >= 4) & (rk <= 10)), ('out', pl & (rk > 10)), ('skip', ~pl)):
        n = int(m.sum()); out[name] = [round(float(in12[m, i].mean()), 3), n] if n >= 25 else None
    out['go'] = round(float(pl.mean()), 2)
    return out
def need(u, target):
    """какое место (самое низкое) выводит на target. one: по каждому доступному турниру отдельно (обычные - все, финалы серий - свои);
    multi: одинаковое место сразу на двух/трёх турнирах, куда игрок уже записан. Значения: число = место и выше; 'any' = хватит участия; None = не хватит."""
    if cur.get(u, 0) >= target: return {'done': True}
    def ok(add): return g.best10(base[u] + add) >= target
    def low(combo):
        if not ok([(e['gridfull'][0], e['ser']) for e in combo]): return None
        n = max(len(e['gridfull']) for e in combo); k = 1
        for j in range(1, n):
            if ok([(e['gridfull'][min(j, len(e['gridfull']) - 1)], e['ser']) for e in combo]): k = j + 1
            else: break
        return 'any' if k >= n else k
    one = {str(e['id']): low([e]) for e in EV if can(u, e, False) and (not e['fin'] or can(u, e, True))}
    av = [e for e in EV if can(u, e, True)]; byw = collections.defaultdict(list); multi = {}
    for e in av: byw[e['wk']].append(e)
    for n in (2, 3):
        best = None
        for ws in itertools.combinations(sorted(byw), n):
            for combo in itertools.product(*[byw[w] for w in ws]):
                if sum(e['ser'] for e in combo) > 2: continue
                k = low(combo)
                if k is None: continue
                kv = 999 if k == 'any' else k
                if best is None or kv > best[0]: best = (kv, k, [e['id'] for e in combo])
        multi[str(n)] = {'place': best[1], 'ev': best[2]} if best else None
    return {'done': False, 'one': one, 'multi': multi}

rows = []
for s0, u in mid[:TOPN]:
    if u not in base: continue
    above_now = sum(1 for s1, v in mid if v != u and s1 > MAXA.get(u, s0))
    st = 'alive'; wc = None; wcr = None
    if above_now >= 12: st = 'out_math'
    elif rank[u] <= 16:
        nR, scR, exR = worst_case(u, True)
        if nR < 12:
            nA, scA, exA = worst_case(u, False)
            st = 'in_math' if nA < 12 else 'in_regs'; wc = scA
        else: wcr = scR
    i = idx.get(u)
    row = {'uid': u, 'nick': g.NICK.get(u, '?'), 'rank': rank[u], 'sigma': s0, 'st': st, 'max': MAXA.get(u), 'max_regs': MAXR.get(u),
           'p12': round(float(in12[:, i].mean()), 3) if i is not None else 0.0,
           'exp': round(float(np.median(sums[:, i]))) if i is not None else s0, 'p10': round(float(np.percentile(sums[:, i], 10))) if i is not None else s0,
           'p90': round(float(np.percentile(sums[:, i], 90))) if i is not None else s0,
           'evs': [e['id'] for e in EV if can(u, e, True)], 'cond': cond(u)}
    if st in ('alive', 'in_regs'):
        row['need'] = {'q50': need(u, plank['q50']), 'q90': need(u, plank['q90'])}
        sc = wcr if st == 'alive' else wc
        if sc and rank[u] <= 12:
            row['risk'] = [x for x in sc if x['res']][:14]; row['risk_regs'] = (st == 'alive')      # risk_regs: сценарий укладывается в уже поданные заявки
            row['risk_n'] = sum(len(x['res']) for x in sc)
    rows.append(row)

# ---- прогнозный расклад для «Конструктора»: самый типичный розыгрыш модели (каждый игрок ближе всего к своей медиане).
#      Один и тот же seed даёт один и тот же мир при любом track, поэтому места по каждому обычному турниру берём из одного розыгрыша;
#      финалы серий - место, соответствующее средним баллам игрока в финале (модель не ведёт места финалов по розыгрышам).
cont = [u for s1, u in mid[:TOPN] if u in idx]; FC = {}; SF = 800; taken = set()
regs_ev = [e for e in se.events if e['type'] != 'contour' and any(e['p'].get(u, 0) >= 0.3 for u in cont)]
runs = {e['id']: se.run(S=SF, seed=11, frailty=None, track=e['id']) for e in regs_ev}
if runs:
    r0 = next(iter(runs.values())); top = [idx[u] for s1, u in mid[:20] if u in idx]
    dist = np.abs(r0['sums'][:, top] - np.median(r0['sums'][:, top], axis=0)).sum(axis=1) + 3 * np.abs(r0['thr'] - np.median(r0['thr']))
    sb = int(np.argmin(dist))
    for e in regs_ev:
        rr = runs[e['id']]; lst = [[u, int(rr['trkr'][sb, idx[u]])] for u in cont if rr['trk'][sb, idx[u]] >= 0]
        for u, pl in lst: taken.add((u, wk(e['date'])))
        if lst: FC[str(e['id'])] = sorted(lst, key=lambda x: x[1])
    for e in se.events:
        if e['type'] != 'contour' or e['id'] not in r0['ser_play']: continue
        gr = [float(x) for x in e['grid']]; lst = []; used = set()
        for u in sorted([u for u in cont if u in e['fin'] and r0['ser_play'][e['id']][idx[u]] >= 0.5 and (u, wk(e['date'])) not in taken],
                        key=lambda u: -r0['ser_by'][e['id']][idx[u]] / max(r0['ser_play'][e['id']][idx[u]], 1e-9)):
            avg = r0['ser_by'][e['id']][idx[u]] / max(r0['ser_play'][e['id']][idx[u]], 1e-9)
            pl = min(range(len(gr)), key=lambda k: abs(gr[k] - avg)) + 1
            while pl in used: pl += 1
            used.add(pl); lst.append([u, pl]); taken.add((u, wk(e['date'])))
        if lst: FC[str(e['id'])] = lst

F = {'v': '1.2', 'T': T, 'now12': now12, 'now13': now13, 'plank': plank, 'S': S, 'exact': HAVE_MILP,
     'key': {'id': key['id'], 'short': key['short'], 'date': key['date'], 'stars': key['stars']} if key else None,
     'weeks': WEEKS,
     'events': [{'id': e['id'], 'date': e['date'], 'wk': e['wk'], 'name': e['name'], 'short': e['short'], 'stars': e['stars'], 'fin': e['fin'], 'N': e['N'], 'grid': e['grid'][:15], 'tail': e['gridfull'][-1],
                 'regs': [g.NICK.get(u, '?') for s1, u in mid[:TOPN] if u in e['regs']]} for e in EV],
     'forecast': FC, 'rows': rows}
json.dump(F, open(OUTP('finish.json'), 'w'), ensure_ascii=False)
# дописать в открытый race2026.js (если он уже собран build_race)
try:
    p = OUTP('race2026.js'); s = open(p, encoding='utf-8').read(); a = s.index('{', s.index('window.RACE')); b = s.rindex('}')
    R = json.loads(s[a:b + 1]); R['finish'] = F
    open(p, 'w', encoding='utf-8').write(s[:a] + json.dumps(R, ensure_ascii=False, separators=(',', ':')) + s[b + 1:])
    print('finish → race2026.js')
except FileNotFoundError:
    print('race2026.js не найден - finish.json сохранён отдельно')
cnt = collections.Counter(x['st'] for x in rows)
print('finish:', dict(cnt), 'проходной', plank, 'ключевой турнир', key and key['short'], 'точный перебор' if HAVE_MILP else 'БЕЗ scipy - грубая оценка')
for x in rows[:20]: print(f"  {x['rank']:>2} {x['nick']:<12} Σ{x['sigma']:>5} {x['st']:<8} p12={x['p12']:.2f} max={x['max']} max_regs={x['max_regs']}")
