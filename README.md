# MafgameStat — репозиторий турнирного сайта (методология)

> Самодокументирующий README для GitHub. Полная внутренняя версия: `../МЕТОДОЛОГИЯ_new_ce634_v1.0.md`.
> Обновлять при существенных изменениях. Эталон «new»/мобильной версии — `ce634.html`.

## Что это
Статический сайт статистики мафия-турниров. Без сборки (no build): чистые HTML+CSS+JS. Прод — **Vercel** (`mafgamestat.vercel.app`). Каждый турнир имеет id (напр. 634 = Чемпионат Европы 2026).

Два вида страниц турнира:
- **Классика** — набор страниц (`tournament.html`, `participants.html`, `seating{id}.html`, `cards{id}.html`, `standings.html`, `results.html`, `roles.html`, `player.html`). Десктоп-ориентированы.
- **«new» / мобильная** — единый SPA `ce{id}.html` (эталон `ce634.html`). Мобайл-фёрст, esports-раскладка, всё в одном файле поверх ТЕХ ЖЕ данных.

## Структура репозитория (`site/`)
```
index.html            хаб турниров (список, статусы, постеры)
tournament.html       страница турнира (?t=id) — меню разделов классики
participants.html     состав + рейтинг markery (универсальная, ?t=id)
seating{id}.html      интерактивная рассадка (классика)
cards{id}.html        карточки игроков (классика)
standings.html        сводная (?t=id)  · roles.html (?t=id) · results.html · player.html
ce{id}.html           «new»/мобильная версия (эталон ce634.html)
data/
  tournaments.js      РЕЕСТР всех турниров (статусы, постеры, accent, разделы, порядок)
  live.js             LIVE-движок: тянет игры с mafgame через прокси /mafgame/*, парсит, защищает снимок
  streams.js          ссылки на трансляции
  tournament_{id}.json   мета турнира (in_progress, games_total, prize_eur, stars, accent, referees, format)
  participants_{id}.json ростер + рейтинг markery (nick,uid,real,av,status,markery_id,ms,r_tier,r_elo_cur,r_elo_2026,r_rank_eu_2026)
  avatars_{id}.json      {avatars:{nick:url}, judges:{"1":{name,tg,avatar},...}}
  elo_{id}.json          {players:{nick:{global,tournaments}}}
  skip_{id}.json         {nick: номер игры отдыха}
  games_{id}_current.json {games:[{title,stage,tables:[{table_num,judge,winner,seats:[{seat,name,role,marker,aps,wpts,ci,result}]}]}]}
  _snapshots/            снимки рейтинга markery по датам
assets/                 постеры (bonn{id}.jpg — широкий, bonn{id}_card.jpg — 16:9 для hero), фавикон
vercel.json             rewrite /mafgame/:path* -> https://mafgame.org/:path*  (прокси для live)
```

## Поток данных
1. Реестр `tournaments.js` (`window.TOURNAMENTS_DB.tournaments[]`) — что за турниры, статусы, постеры, accent, разделы.
2. По каждому турниру — JSON-файлы в `data/` (см. выше).
3. **Live:** если `tournament_{id}.json.in_progress===true`, `live.js` `loadGames(id)` при каждом открытии тянет `/mafgame/tournaments/{id}/game_results` (Vercel проксирует на mafgame.org), парсит Inertia-данные (`convertInertia`), сравнивает с сохранённым в `localStorage` снимком и **не затирает** хорошие данные пустыми (`snapScore`/`notRegression`). До старта / для завершённых — отдаёт локальный `games_{id}_current.json`.
4. Победитель стола — из официального поля `results` mafgame (`red_win`/`black_win`), не из очков.

Источники: **mafgame.org** (ростер uid, протоколы, рассадка, результаты — HTML Inertia), **markery.online** (ELO/тиры/места — ведём через Excel-базу, снимок в `_snapshots/`), **mafiastats.com** (REST, сверка).

## Формулы
- Σ (итог игрока) = **WPTS + доп(aps) + Ci** по сыгранным играм.
- доп(aps) может быть отрицательным (штраф). «доп+»=сумма плюсов, «доп−»=сумма минусов, «доп-всего»=aps+ci.
- Роли: Citizen(Мирный), Sheriff(Шериф) — красные; Mafia, Don — чёрные. К+Ш=красные, Ч+Д=чёрные.
- «убит 1-й ночью»: seat.marker==='first_killed'. Результат: result==='W'/'L'.

## «new»/ce634 — архитектура (детали в шапке `ce634.html`)
Загрузчик → объект `D` → `computeSeating()`+`computeStats()` → `NAV` (4 группы) строит sidebar(desktop)/tabbar(mobile) → `RENDER[section]()`+`afterRender()`.
- Мобильный режим: `@media(max-width:1024px)` (ловит и раскрытый Fold). Таб-бар снизу, всплывающее меню, тумблер Компактно/Подробно, залипший ник.
- `statFull` (Компактно/Подробно), `myPlayer`+`viewMode` (localStorage), демо-режим (`makeDemo` — полный случайный бракет для проверки статы до старта).

## Жизненный цикл турнира и статусы
Статус задаётся в `tournaments.js` (`status`) + флаг `in_progress` в `tournament_{id}.json`. Порядок на главной — поле `phase`.

1. **gathering (собирается)** — идёт регистрация, состав НЕ финализирован, рассадки нет. `status:"gathering"`, `phase:4`, `in_progress:false`. Показываем анонс/заявки.
2. **upcoming (скоро)** — **финальный состав и рассадка готовы** (квалификация посеяна), турнир ещё не начался. `status:"upcoming"`, `phase:3`. Доступны рассадка/карточки/участники; игр ещё нет. `in_progress:false` до дня старта.
3. **live (идёт)** — **дни турнира**. Состав считаем финальным и **тянем игры** с mafgame: `tournament_{id}.json.in_progress:true`, `status:"live"`, `phase:2`. `live.js` при каждом открытии подтягивает `game_results` через прокси.
   - ⚠️ **Тянуть только в дни турнира.** НЕ держать `in_progress:true` постоянно (лишняя нагрузка на mafgame + риск подтянуть кривое/пустое). Включаем на дни турнира, после — выключаем.
4. **finished (завершён → архив)** — после окончания. `in_progress:false`, `status:"finished"`, `phase:1`. Данные заморожены, турнир уходит в архив (главная сортирует по дате `start`).

## Как ЗАКРЫВАТЬ турнир (заморозка + сверка 1:1 с mafgame)
1. Снять с mafgame **официальную итоговую таблицу** (Result Table: Финал + Полуфинал + Квалификация + награды/MVP).
2. Вставить её **1-в-1** в `tournament_{id}.json` → `standings` (total/final/qualification), `awards`, чемпион/подиум. **Сверить с сайтом mafgame до цента** — итог и расшифровка обязаны биться.
3. Заморозить протоколы `games_{id}_current.json` (роли, очки, победители столов) как есть на конец турнира.
4. Переключить: `tournament_{id}.json.in_progress:false`; в `tournaments.js` `status:"finished"`, `phase:1`.
5. ⚠️ **Брать ОФИЦИАЛЬНУЮ таблицу mafgame, НЕ пересчитывать самим.** Урок (v10.1, Кёльн-702): на допы финала действует коэффициент ~1.3 — наш авторасчёт расходился с официалом. Для завершённых источник истины — таблица mafgame.
6. Задеплоить новую версию.

## Как добавить НОВЫЙ турнир (чек-лист)
1. Собрать `data/*_{newid}*` (participants/tournament/avatars/elo/skip/games_current) по схемам выше. Добавить запись в `tournaments.js`.
2. Копия `ce634.html` → `ce{newid}.html`, заменить `634`→`{newid}`, тексты (название/город/даты), START-дату, постер `assets/*_card.jpg` (16:9).
3. Поправить стадии в `stagesPanel()` и группировку селектора игр (День/стадии) под реальный формат. Число игр — из данных, не хардкод.
4. Кнопку-переключатель на классической `tournament.html?t={newid}` (условие по `t.id`).
5. QA: jsdom 0 ошибок (проверять КЛИКАМИ); демо-бракет; мобильный визуал — на телефоне через превью.
6. Zip → залить (см. Деплой).

## Деплой
```
cd site
zip -r ../Uploaded/mafgamestat_vN_upload.zip . \
  -x "_Архив/*" -x "data/_snapshots/*" -x "SPEC.md" -x "*.DS_Store" -x "*.bak" -x "* *"
```
→ содержимое залить в GitHub (`github.com/ValeriiScz/bitvachempionov2026`) → Vercel автодеплой. Zip кладёт содержимое `site/` в корень (без префикса). **Перед сборкой zip: поднять `CACHE_VERSION` в `sw.js`** (иначе у установивших PWA код обновится только со 2-го открытия).

## Грабли (важно)
- **«Сайт мелкий на телефоне, локальный HTML — ок»** = в Chrome включён режим **«Версия для ПК»** для домена (рендер в ~980px + ужатие). Это НЕ код — снять галочку в браузере. Проверять ПЕРВЫМ. (PWA-обёртка это лечит навсегда, см. ниже.)
- `.seatgrid`/сетки: `repeat(N,minmax(0,1fr))` + `min-width:0` — иначе min-content колонок вылезает.
- Sticky-колонки на подсвеченной строке — фон делать НЕПРОЗРАЧНЫМ, иначе цифры просвечивают при скролле.
- Не ломать защиту снимка в `live.js` (localStorage `snapScore`/`notRegression`) — она бережёт данные при глюках mafgame.
- Версионирование строго инкрементом; старое → `_Архив/`.

## QA — что можно и нельзя автоматически
- Можно: `node --check` / jsdom-прогон (проверять **кликами**, не только вызовом функций), баланс `{}` в CSS, десктоп-скриншот.
- Нельзя: отрендерить реальную мобильную ширину в CI/песочнице (headless-браузер недоступен). Мобильный визуал — на устройстве.

## Мобильное приложение (PWA) — реализовано (v12)
Сайт устанавливается как приложение: `manifest.json` (standalone, палитра Bonn) + `sw.js` (service worker) + иконки `assets/icons/` (эмблема mafgame внутри чемпионского кубка, золото на navy; any/maskable 192/512 + apple-touch-icon 180) + PWA-блок в `<head>` всех страниц (манифест, theme-color, iOS-меты, регистрация SW — только по http(s), локальный `file://` просмотр не падает) + **промо-плашка установки** на всех страницах: iPhone — инструкция Safari→«На экран “Домой”», Android — кнопка «Установить» (beforeinstallprompt) или инструкция про меню Chrome; не показывается внутри установленного приложения и 14 дней после «Позже» (localStorage `mgs_pwa_promo_hide_until`).

Стратегии кэша (`sw.js`):
- `/mafgame/*` — **только сеть** (кэш обходится): live всегда свежий, защита снимка в `live.js` не задета;
- `data/*.json` — network-first (офлайн — из кэша);
- оболочка (html/js/иконки/шрифты) — stale-while-revalidate: мгновенно из кэша + фоновое обновление (код не «залипает» даже без bump).

⚠️ **При каждом деплое поднять `CACHE_VERSION` в `sw.js`** (…-v12.1, …-v13) — на activate старые кэши удаляются. Установка: iPhone — Safari → Поделиться → «На экран "Домой"»; Android — Chrome → меню ⋮ → «Установить приложение». Полноэкранный standalone-запуск заодно навсегда лечит баг «Версии для ПК».

Нативное приложение (Swift/Kotlin) — избыточно: та же зависимость от mafgame, магазины, поддержка.
