"""gd_cfg · v1.0 · 2026-09-21 — общие настройки конвейера «золотой дюжины».
T   — дата снимка (GD_T, по умолчанию сегодня);
OUT — папка промежуточных json (GD_OUT, по умолчанию текущая). В публичный репозиторий эти json не коммитим."""
import os, datetime
T=os.environ.get('GD_T') or datetime.date.today().isoformat()
OUT=os.environ.get('GD_OUT') or '.'
os.makedirs(OUT,exist_ok=True)
def out(name): return os.path.join(OUT,name)
