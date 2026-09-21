#!/usr/bin/env python3
"""run_all.py · v1.0 · 2026-09-21 — весь конвейер «Гонки за золотую дюжину» одной командой.
Шаги: recal (прогноз 3000 сезонов) → scenarios3 (планки 1/2/3) → tickets → plan2 → build_race (race2026.js)
      → encrypt_race (vault/race.json, пароль из RACE_PASS) → build_series (data/series2026.js) → bump CACHE_VERSION в sw.js.
Окружение: GD_REPO (корень репо; по умолчанию — три уровня вверх от этого файла), GD_T (дата снимка, по умолчанию сегодня),
           GD_OUT (папка промежуточных json, по умолчанию $GD_REPO/.gd_out — не коммитится), RACE_PASS (обязателен).
Запуск:   RACE_PASS=… python3 data/research/model/run_all.py            (из корня репо, локально или в GitHub Actions)
Флаги:    --no-sw  не трогать sw.js;  --keep-plain  оставить открытый race2026.js в GD_OUT (по умолчанию удаляется).
"""
import os, sys, re, subprocess, time, shutil, datetime
HERE=os.path.dirname(os.path.abspath(__file__))
REPO=os.environ.get('GD_REPO') or os.path.abspath(os.path.join(HERE,'..','..','..'))
os.environ['GD_REPO']=REPO
T=os.environ.setdefault('GD_T', datetime.date.today().isoformat())
OUT=os.environ.setdefault('GD_OUT', os.path.join(REPO,'.gd_out'))
os.makedirs(OUT,exist_ok=True)
PASS=os.environ.get('RACE_PASS')
if not PASS: sys.exit('RACE_PASS не задан — без пароля vault/race.json не собрать')
if not os.path.exists(os.path.join(REPO,'calendar.html')): sys.exit(f'не похоже на корень репо: {REPO}')
print(f'== конвейер дюжины · T={T} · repo={REPO} · out={OUT}')
def step(name, *args):
    t0=time.time(); print(f'\n--- {name}'); sys.stdout.flush()
    r=subprocess.run([sys.executable,*args],cwd=HERE,env=os.environ)
    if r.returncode: sys.exit(f'!! шаг {name} упал ({r.returncode})')
    print(f'--- {name} ок, {time.time()-t0:.0f} с')
step('recal',      'recal.py')
step('scenarios3', 'scenarios3.py')
step('tickets',    'tickets.py')
step('plan2',      'plan2.py')
step('build_race', 'build_race.py')
plain=os.path.join(OUT,'race2026.js'); vault=os.path.join(REPO,'vault','race.json')
step('encrypt',    'encrypt_race.py', plain, vault, '--pass', PASS)
step('build_series','build_series.py')
shutil.copy(os.path.join(OUT,'series2026.js'), os.path.join(REPO,'data','series2026.js'))
if '--keep-plain' not in sys.argv: os.remove(plain)
if '--no-sw' not in sys.argv:
    sw=os.path.join(REPO,'sw.js'); s=open(sw,encoding='utf-8').read()
    m=re.search(r"const CACHE_VERSION = 'dovod-v(\d+)';",s)
    if m:
        v=int(m.group(1))+1; s=s.replace(m.group(0),f"const CACHE_VERSION = 'dovod-v{v}';"); open(sw,'w',encoding='utf-8').write(s); print(f'sw.js → dovod-v{v}')
print(f'\n== готово: {vault} ({os.path.getsize(vault)//1024} КБ), data/series2026.js ({os.path.getsize(os.path.join(REPO,"data","series2026.js"))//1024} КБ)')
