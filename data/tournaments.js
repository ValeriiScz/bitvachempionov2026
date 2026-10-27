// MafgameStat | tournaments.js | v4.2 | 2026-10-27 | 687: страница t687 + смотровая watch687 (4 стола)
// MafgameStat | tournaments.js | v4.1 | 2026-10-26 | архив: top3, mvp из data/tournament_*.json; 710 ср. ELO 1132 (54/55, снимок elo_710); 615/687 ELO markery 26.10
// MafgameStat | tournaments.js | v3.3 | 2026-10-13 | 673 -> finished (чемпион Tripok 13.33, Bard 12.275, TOPS 11.0; финал 4 игры); +710 ЧМ-2026 в архив (page wc2026-tournament.html); архив ведёт на t.page
// MafgameStat | tournaments.js | v3.2 | 2026-10-09 | +673 Чемпионат Молдовы (theme dovod, t673/watch673, live 10–11.10) + 692 Four Seasons Central Cup и 687 Mediterranean GP (собираются, участники + ELO)
// MafgameStat | tournaments.js | v3.1 | 2026-08-23 | 694 -> finished: чемпион Lюц 13.065 (Магнат 12.98, aptah 12.17); официальные таблицы вставлены, финал с коэффициентом x1.3
// MafgameStat | tournaments.js | v3.0 | 2026-08-22 | +694 Central Euro Cup (Прага, финал серийника, live 22-23.08): 12 квал x 3 стола + финал 5, постер prague694, accent #c9a227, ce694; 634 -> finished (чемпион Европы YeS 15.205, RAMZES 15.195, разрыв 0.01)
// MafgameStat | tournaments.js | v2.9 | 2026-07-16 | ЧЕ-634 -> upcoming(Скоро) премиум: постер Бонна, золотой accent, приз 3000€/5★, разлочены seating634/cards634/standings/results/roles/player; судьи столов
// MafgameStat | tournaments.js | v2.8 | 2026-07-15 | ЧЕ-634: свежий состав 44 подтв. + пересчитанный markery (eloAvg 1057/43); statusLabel и note обновлены
// MafgameStat | tournaments.js | v2.7 | 2026-07-04 | +start-даты для сортировки архива по дате; 702 live+закат; 766 finished (чемпион Lюц)
// MafgameStat | tournaments.js | v2.6 | 2026-07-03 | 766->finished (16/16, чемпион Lюц, store убран) + 702->upcoming(Скоро): рассадка 12x4, cards/seating702, live-подтяжка, постер cologne702, eloAvg 997/37
// MafgameStat · data/tournaments.js · v2.4 · 2026-06-21 · 693 live: разлочена карточка «Статистика игрока» (player.html?t=693)
// MafgameStat · data/tournaments.js · v2.3 · 2026-06-20 · 4 статуса (live/soon/gathering/finished) + поле phase для порядка главной (2→3→4→1);
//   +702 Кубок Кёльна, +634 Чемпионат Европы (оба «собирается»); счётчик ожид. ELO (markery) на плашках; участники+двойной рейтинг; accent per-турнир.
// MafgameStat | tournaments.js | v2.5 | 2026-06-25 | 766->upcoming(Скоро)+разлок seating/cards/stat+live(in_progress)+store; fix player.html?t=693
// MafgameStat | tournaments.js | v3.4 | 2026-10-15 | 692 Central Cup -> upcoming (Скоро): страница t692 + смотровая watch692, рассадка 15.10, 33 игрока, ELO markery 15.10 (Ø 1086), live 17–18.10
// MafgameStat | tournaments.js | v3.5 | 2026-10-15 | 710 ЧМ-2026 в архиве ведёт на хаб wc2026.html (страница турнира · режим зрителя · карточки) — плитка ЧМ убрана с главной
// MafgameStat | tournaments.js | v3.6 | 2026-10-16 | 692: studio:true — студия аналитики (для зрителей) в смотровой watch692.html#studio
// MafgameStat | tournaments.js | v3.7 | 2026-10-18 | 692 Central Cup -> finished (чемпион Korolevich 13.59, aptah 13.32, TOPS 12.74, DOVOD 12.64)
// MafgameStat | tournaments.js | v3.8 | 2026-10-26 | +645 White Mafia Best Player — финал серийника (Вроцлав 7–8.11, постер, t645, состав предварительный) + 643 Wroclaw Mafia Open (собирается, участники + ELO)
// MafgameStat | tournaments.js | v3.9 | 2026-10-26 | 645 -> страница на движке DOVOD (t645 v2.0, один стол) + watch645; 645/643 theme dovod с акцентом White Mafia (accent/accent2/artPaper — новые поля для tournaments.html v4.0)
// MafgameStat | tournaments.js | v4.0 | 2026-10-26 | +615 Four Seasons: Black Circle (Брюссель 7–8.11, 4★): t615 + watch615 на движке DOVOD (формат 12+4 — гипотеза), участники 30 + 1
window.TOURNAMENTS_DB = {
  "tournaments": [
  {
    "id": "615",
    "theme": "dovod",
    "page": "t615.html",
    "watch": "watch615.html",
    "name": "Four Seasons: Black Circle 2026",
    "posterTitle": "Four Seasons|Black Circle",
    "dates": "7–8 ноября 2026",
    "city": "Брюссель",
    "country": "Бельгия",
    "players": 30,
    "days": 2,
    "stars": 4,
    "status": "upcoming",
    "phase": 3,
    "statusLabel": "Состав полный · 30 + 1 заявка (Korolevich)",
    "eloAvg": 1143,
    "eloN": 30,
    "eloTotal": 30,
    "organizer": "AtomNøir · орг Рыба-мÓя",
    "format": "12 квал × 3 стола → финал топ-10 (ожидаемо, регламента ещё нет)",
    "mafgame": "https://mafgame.org/tournaments/615/view",
    "note": "Формат и время старта на mafgame не указаны — страница собрана по формату прошлых Four Seasons на 30 игроков.",
    "sections": [
      {
        "href": "t615.html",
        "title": "Страница турнира",
        "desc": "Обзор · Моё · Игроки · Столы · Результаты"
      },
      {
        "href": "watch615.html",
        "title": "▶ Смотровая · эфиры",
        "desc": "три стола в одном окне, следить за игроком"
      },
      {
        "href": "participants.html?t=615",
        "title": "Участники и рейтинг",
        "desc": "30 игроков + ELO markery у всех (снимок 26.10)"
      }
    ],
    "start": "2026-11-07"
  },
  {
    "id": "645",
    "theme": "dovod",
    "art": "assets/wroclaw645_card.jpg",
    "artRatio": "16 / 9",
    "page": "t645.html",
    "name": "White Mafia Best Player 2026 — финал",
    "dates": "7–8 ноября 2026",
    "city": "Вроцлав",
    "country": "Польша",
    "players": 12,
    "days": 2,
    "stars": 2,
    "prize": "600€",
    "status": "upcoming",
    "phase": 3,
    "statusLabel": "Финал серийника · 12 финалистов (состав предварительный) · 18 игр, один стол",
    "eloAvg": 1079,
    "eloN": 7,
    "eloTotal": 12,
    "organizer": "White Mafia Club Wroclaw · орг и главный судья Кирпич",
    "mafgame": "https://mafgame.org/tournaments/645/view",
    "note": "Состав предварительный: топ-2 каждой из 6 отборочных серий по протоколам mafgame. Официально утвердит организатор; замены — 3-е место той же серии, затем 3-и места по сумме доп. баллов.",
    "sections": [
      {
        "href": "t645.html",
        "title": "Страница финала",
        "desc": "обзор, отбор и резерв, рассадка, таблица, игры, роли"
      },
      {
        "href": "watch645.html",
        "title": "▶ Смотровая · эфир",
        "desc": "стол крупно, live-таблица, следить за игроком"
      },
      {
        "href": "participants.html?t=645",
        "title": "Финалисты и рейтинг",
        "desc": "ELO markery и место в рейтинге mafgame 2026"
      }
    ],
    "start": "2026-11-07",
    "watch": "watch645.html",
    "accent": "#ece7dd",
    "accent2": "#f4f1ea",
    "artPaper": "#efeeec",
    "posterTitle": "White Mafia|Best Player"
  },
  {
    "id": "643",
    "name": "Wroclaw Mafia Open 2026",
    "dates": "21–22 ноября 2026",
    "city": "Вроцлав",
    "country": "Польша",
    "players": 30,
    "days": 2,
    "stars": 3,
    "prize": "",
    "status": "gathering",
    "phase": 3,
    "statusLabel": "Собирается · 12 в списке + 1 заявка",
    "eloAvg": 1082,
    "eloN": 9,
    "eloTotal": 13,
    "organizer": "White Mafia Club Wroclaw · орг Кирпич",
    "mafgame": "https://mafgame.org/tournaments/643/view",
    "note": "Ожидается 30 участников, взнос 110 €. В списке — записанные и заявки (снимок 26.10). Страница турнира откроется после рассадки.",
    "sections": [
      {
        "href": "participants.html?t=643",
        "title": "Участники и рейтинг",
        "desc": "записанные и заявки + ELO markery (снимок 26.10)"
      },
      {
        "soon": true,
        "title": "Страница турнира",
        "desc": "рассадка, сила столов, live-результаты"
      }
    ],
    "start": "2026-11-21",
    "accent": "#ece7dd",
    "accent2": "#f4f1ea",
    "posterTitle": "Wroclaw|Mafia Open",
    "theme": "dovod"
  },
  {
    "id": "673",
    "theme": "dovod",
    "page": "t673.html",
    "watch": "watch673.html",
    "name": "Чемпионат Молдовы 2026",
    "posterTitle": "Чемпионат|Молдовы",
    "dates": "10–11 октября 2026",
    "city": "Кишинёв",
    "country": "Молдова",
    "players": 30,
    "days": 2,
    "stars": 3,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 16 игр (12 квал + 4 финала) · чемпион Tripok",
    "eloAvg": 1020,
    "eloN": 29,
    "eloTotal": 30,
    "organizer": "mafia.md · орг Весная, Г-жа Кот · главный судья YeS",
    "format": "12 игр квалификации × 3 стола → финал 4 игры (топ-10, ×1.3)",
    "mafgame": "https://mafgame.org/tournaments/673/view",
    "note": "Чемпион Молдовы — Tripok (13.33), 2-е Bard (12.275), 3-е TOPS (11.0). Протоколы 16 игр заморожены и сверены с официальной таблицей mafgame.",
    "sections": [
      {
        "href": "t673.html",
        "title": "Страница турнира",
        "desc": "Итоги, таблица, протоколы 16 игр, сила столов и рассадка"
      },
      {
        "href": "watch673.html",
        "title": "▶ Смотровая · все эфиры",
        "desc": "Записи трансляций трёх столов и финала"
      },
      {
        "href": "participants.html?t=673",
        "title": "Участники и рейтинг",
        "desc": "30 игроков + ELO markery (снимок 09.10)"
      }
    ],
    "start": "2026-10-10",
    "prize": "700€",
    "champion": "Tripok",
    "top3": [
      "Tripok",
      "Bard",
      "TOPS"
    ],
    "mvp": "Tripok"
  },
  {
    "id": "692",
    "theme": "dovod",
    "page": "t692.html",
    "watch": "watch692.html",
    "studio": true,
    "name": "Four Seasons: Central Cup 2026",
    "posterTitle": "Four Seasons|Central Cup",
    "dates": "17–18 октября 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 33,
    "days": 2,
    "stars": 4,
    "prize": "750€",
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 17 игр (11 квал + 2 полуфинала + 4 финала) · чемпион Korolevich",
    "liveFrom": "2026-10-17",
    "liveTo": "2026-10-18",
    "eloAvg": 1086,
    "eloN": 33,
    "eloTotal": 33,
    "organizer": "Mafia club «Champions League» Prague · судьи YeS (главный), Гармония, Trinity",
    "format": "11 игр квалификации × 3 стола (у каждого 10) → полуфинал 2 игры (топ-30) → финал 4 игры (топ-10, ×1.3)",
    "mafgame": "https://mafgame.org/tournaments/692/view",
    "note": "Чемпион — Korolevich (13.59), 2-е aptah (13.32), 3-е TOPS (12.74), 4-е DOVOD (12.64). Протоколы 17 игр заморожены и сверены с официальной таблицей mafgame.",
    "champion": "Korolevich",
    "sections": [
      {
        "href": "t692.html",
        "title": "Страница турнира",
        "desc": "Обзор · Моё · Игроки · Столы · Результаты — рассадка, сила столов, live-таблица"
      },
      {
        "href": "watch692.html",
        "title": "▶ Смотровая · все эфиры",
        "desc": "Три стола в одном окне, «следить за игроком»"
      },
      {
        "href": "participants.html?t=692",
        "title": "Участники и рейтинг",
        "desc": "33 игрока + ELO markery (снимок 15.10)"
      }
    ],
    "start": "2026-10-17",
    "top3": [
      "Korolevich",
      "aptah",
      "TOPS"
    ],
    "mvp": "Korolevich"
  },
  {
    "id": "687",
    "theme": "dovod",
    "name": "Mediterranean Grand-Prix 2026",
    "posterTitle": "Mediterranean|Grand-Prix",
    "dates": "31 октября – 1 ноября 2026",
    "city": "Лимасол",
    "country": "Кипр",
    "players": 46,
    "days": 2,
    "stars": 5,
    "prize": "3000€",
    "status": "gathering",
    "phase": 3,
    "statusLabel": "Собирается · 36 подтв. + 1 заявка",
    "eloAvg": 1124,
    "eloN": 34,
    "eloTotal": 46,
    "organizer": "Mafia Club Cyprus",
    "mafgame": "https://mafgame.org/tournaments/687/view",
    "note": "Регламент: на 40 игроков — 12 отборочных туров и 4 финальные игры; на 44 — 11 туров, 2 полуфинала и финал. Рассадка — жеребьёвкой накануне.",
    "sections": [
      {
        "href": "t687.html",
        "title": "Страница турнира",
        "desc": "рассадка, сила столов, live-результаты"
      },
      {
        "href": "watch687.html",
        "title": "Смотровая · эфиры",
        "desc": "4 стола в одном окне, режим экономии"
      },
      {
        "href": "participants.html?t=687",
        "title": "Участники и рейтинг",
        "desc": "подтверждённые и заявки + ELO markery (снимок 26.10)"
      }
    ],
    "start": "2026-10-31",
    "page": "t687.html",
    "watch": "watch687.html",
    "liveFrom": "2026-10-31",
    "liveTo": "2026-11-01",
    "format": "12 квал × 4 стола → финал топ-10"
  },
  {
    "id": "710",
    "page": "wc2026.html",
    "name": "Mafia World Championship 2026",
    "dates": "12–13 сентября 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 55,
    "days": 2,
    "stars": 5,
    "status": "finished",
    "statusLabel": "Завершён · 17 игр (11 квал + 2 полуфинала + 4 финала) · чемпион Призрак",
    "start": "2026-09-12",
    "top3": [
      "Призрак",
      "RAMZES",
      "Сью"
    ],
    "mvp": "RAMZES",
    "eloAvg": 1132,
    "eloN": 54,
    "eloTotal": 55
  },
  {
    "id": "694",
    "theme": "poster",
    "art": "assets/prague694_card.jpg",
    "artRatio": "16 / 9",
    "posterScript": "Praha",
    "posterTitle": "CENTRAL EURO CUP",
    "posterSub": "AUG 22–23 · PRAGUE",
    "accent": "#c9a227",
    "name": "Central Euro Cup 2026",
    "dates": "22–23 августа 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 30,
    "days": 2,
    "stars": 3,
    "prize": "2000€",
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 17 игр · чемпион Lюц",
    "eloAvg": 1088,
    "eloN": 28,
    "eloTotal": 30,
    "organizer": "Mafia club «Champions League» Prague · орг YeS · судьи Кирпич, Trinity, Broniak",
    "mafgame": "https://mafgame.org/tournaments/694/view",
    "note": "Завершён 23.08.2026. Чемпион — Lюц (Σ 13.065); 2-е Магнат (12.98), 3-е aptah (12.17). Финал серийного турнира: 12 игр квалификации (3 стола, играли все 30) + финал 5 игр (топ-10). Официальные таблицы (Итоговая / Финал / Квалификация) и протоколы всех 17 игр — по ссылкам ниже. Данные mafgame, сверено 1:1 (финал — с офиц. коэффициентом ×1.3).",
    "sections": [
      {
        "href": "ce694.html",
        "title": "✦ Мобильная версия · beta",
        "desc": "Всё в одном: Обзор · Моё · Игроки · Результаты — открывайте с телефона"
      },
      {
        "href": "participants.html?t=694",
        "title": "Участники и рейтинг",
        "desc": "30 игроков + ELO markery (свежий снимок 22.08), средний рейтинг состава"
      },
      {
        "href": "seating694.html",
        "title": "Интерактивная рассадка",
        "desc": "Квалификация 12 игр × 3 стола: клик по игроку — весь его маршрут"
      },
      {
        "href": "cards694.html",
        "title": "Карточки игроков",
        "desc": "30 карточек: фото, ранг/ELO, столы, места за столом, соперники, маршрут"
      },
      {
        "href": "markers.html?t=694",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз за одним столом"
      },
      {
        "href": "results.html?t=694",
        "title": "Игры с результатами",
        "desc": "Все 17 игр: роли, допы, победители"
      },
      {
        "href": "standings.html?t=694",
        "title": "Сводная таблица",
        "desc": "Официальный итог + стадии Квалификация/Финал"
      },
      {
        "href": "roles.html?t=694",
        "title": "Статистика по ролям",
        "desc": "Σ по ролям: мирный, шериф, мафия, дон"
      },
      {
        "href": "player.html?t=694",
        "title": "Статистика игрока",
        "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
      }
    ],
    "start": "2026-08-22",
    "top3": [
      "Lюц",
      "Магнат",
      "aptah"
    ],
    "mvp": "Lюц"
  },
  {
    "id": "693",
    "theme": "protocol",
    "accent": "#ff5e5e",
    "name": "MafiaCl Protocol 4 2026",
    "dates": "20–21 июня 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 20,
    "days": 2,
    "stars": 2,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · парный · 15 игр (20–21 июня)",
    "organizer": "Mafia club «Champions League» Prague · судьи Trinity, Yokai",
    "mafgame": "https://mafgame.org/tournaments/693/view",
    "note": "Парный турнир: 10 команд по 2 игрока, 15 игр (2 стола), без финала. Завершён. Зачёт по командам и игрокам — на сводной. Судьи: стол I — Trinity, стол II — Yokai.",
    "sections": [
      {
        "href": "seating693.html",
        "title": "Интерактивная рассадка",
        "desc": "15 игр × 2 стола: клик по игроку — весь его маршрут; судьи Trinity/Yokai с фото"
      },
      {
        "href": "cards693.html",
        "title": "Карточки игроков",
        "desc": "20 карточек: фото, клуб, столы, слоты, соперники, маршрут"
      },
      {
        "href": "teams693.html",
        "title": "Карточки команд",
        "desc": "10 команд по 2: составы и фото"
      },
      {
        "href": "markers.html?t=693",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз за одним столом"
      },
      {
        "href": "results.html?t=693",
        "title": "Игры с результатами",
        "desc": "Все 15 игр × 2 стола: роли, допы, победители"
      },
      {
        "href": "standings.html?t=693",
        "title": "Команды и сводная",
        "desc": "Зачёт по командам и по игрокам (переключатель), Σ и роли"
      },
      {
        "href": "player.html?t=693",
        "title": "Статистика игрока",
        "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
      }
    ],
    "start": "2026-06-20",
    "top3": [
      "ХоровоDovoDоведы (DOVOD + Гармония)"
    ],
    "paired": true,
    "mvp": "DOVOD"
  },
  {
    "id": "766",
    "theme": "poster",
    "art": "assets/FourSeasonsPolandMafiaOpen2026_27.06.2026.jpg",
    "posterScript": "Poland",
    "posterTitle": "POLAND MAFIA OPEN",
    "posterSub": "JUNE 27–28 · POLAND",
    "accent": "#e0b341",
    "name": "Four Seasons: Poland Mafia Open 2026",
    "dates": "27–28 июня 2026",
    "city": "Вроцлав",
    "country": "Польша",
    "players": 40,
    "days": 2,
    "stars": 4,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 16 игр (12 квал + 4 финала)",
    "eloAvg": 1009,
    "eloN": 30,
    "eloTotal": 40,
    "organizer": "Four Seasons",
    "mafgame": "https://mafgame.org/tournaments/766/view",
    "note": "Завершён. 12 игр квалификации (4 стола) + финал 4 игры. Чемпион — Lюц. Официальная сводная, роли и статистика игрока — по ссылкам ниже.",
    "sections": [
      {
        "href": "standings.html?t=766",
        "title": "Сводная таблица",
        "desc": "Итог: Σ, роли, квалификация и финал"
      },
      {
        "href": "results.html?t=766",
        "title": "Игры с результатами",
        "desc": "Все 16 игр: роли, допы, победители"
      },
      {
        "href": "player.html?t=766",
        "title": "Статистика игрока",
        "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
      },
      {
        "href": "roles.html?t=766",
        "title": "Статистика по ролям",
        "desc": "Σ по ролям: мирный, шериф, мафия, дон"
      },
      {
        "href": "seating766.html",
        "title": "Интерактивная рассадка",
        "desc": "12 игр × 4 стола: маршрут каждого игрока"
      },
      {
        "href": "cards766.html",
        "title": "Карточки игроков",
        "desc": "40 карточек: фото, ELO (markery), столы, слоты, соперники"
      },
      {
        "href": "participants.html?t=766",
        "title": "Участники и рейтинг",
        "desc": "Ростер + ELO (markery / mafiastats)"
      },
      {
        "href": "markers.html?t=766",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз за одним столом"
      }
    ],
    "start": "2026-06-27",
    "top3": [
      "Lюц",
      "aptah",
      "SANYURIK"
    ],
    "mvp": "Lюц"
  },
  {
    "id": "702",
    "accent": "#e0592a",
    "name": "Кубок Кёльна 2026",
    "dates": "4–5 июля 2026",
    "city": "Кёльн",
    "country": "Германия",
    "players": 40,
    "days": 2,
    "stars": 3,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 16 игр (12 квал + 4 финала) · чемпион ParadoXx",
    "eloAvg": 997,
    "eloN": 37,
    "eloTotal": 40,
    "organizer": "Mafgame · судьи KEX, Рыба-мÓя, Кура, Кано (столы I–IV)",
    "mafgame": "https://mafgame.org/tournaments/702/view",
    "note": "Завершён. 12 игр квалификации (4 стола) + финал 4 игры (10 финалистов). Чемпион — ParadoXx. Официальная итоговая таблица (Итоговая / Финал / Квалификация), награды и рейтинг — по ссылкам ниже. Данные mafgame, сверено 1:1.",
    "sections": [
      {
        "href": "participants.html?t=702",
        "title": "Участники и рейтинг",
        "desc": "Заявки mafgame + ELO (markery / mafiastats), ожидаемый средний рейтинг состава"
      },
      {
        "href": "seating702.html",
        "title": "Интерактивная рассадка",
        "desc": "12 игр × 4 стола: клик по игроку — весь его маршрут по турниру"
      },
      {
        "href": "cards702.html",
        "title": "Карточки игроков",
        "desc": "40 карточек: фото, ELO (markery), столы, слоты, соперники. Сортировка по рангу/ELO"
      },
      {
        "href": "markers.html?t=702",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз за одним столом"
      },
      {
        "href": "results.html?t=702",
        "title": "Игры с результатами",
        "desc": "Раунды и столы; до старта — рассадка, результаты появятся вживую"
      },
      {
        "href": "standings.html?t=702",
        "title": "Сводная таблица",
        "desc": "Σ, роли, динамика — появится после первой игры"
      },
      {
        "href": "roles.html?t=702",
        "title": "Статистика по ролям",
        "desc": "Σ по ролям: мирный, шериф, мафия, дон — после старта"
      },
      {
        "href": "player.html?t=702",
        "title": "Статистика игрока",
        "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
      }
    ],
    "theme": "poster",
    "art": "assets/cologne702.jpg",
    "posterScript": "Köln",
    "posterTitle": "КУБОК КЁЛЬНА",
    "posterSub": "JULY 4–5 · COLOGNE",
    "start": "2026-07-04",
    "top3": [
      "ParadoXx",
      "ShakAl",
      "RAMZES"
    ],
    "mvp": "ParadoXx"
  },
  {
    "id": "634",
    "theme": "poster",
    "art": "assets/bonn634_card.jpg",
    "artRatio": "16 / 9",
    "posterScript": "Bonn",
    "posterTitle": "ЧЕМПИОНАТ ЕВРОПЫ",
    "posterSub": "18–19 JULY · BONN · GERMANY",
    "accent": "#d4af37",
    "name": "Чемпионат Европы 2026",
    "dates": "18–19 июля 2026",
    "city": "Бонн",
    "country": "Германия",
    "players": 44,
    "days": 2,
    "stars": 5,
    "prize": "3000€",
    "flagship": true,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 18 игр · чемпион Европы — YeS",
    "eloAvg": 1057,
    "eloN": 43,
    "eloTotal": 44,
    "organizer": "Mafgame · World Alliance League",
    "mafgame": "https://mafgame.org/tournaments/634/view",
    "note": "★★★★★ Завершён 19.07.2026. Чемпион Европы — YeS (Σ 15.205); серебро RAMZES (15.195, разрыв 0.01 — фотофиниш), бронза Саботаж. 44 игрока, Бонн, приз 3000€. Официальные таблицы (Итоговая / Финал / Полуфинал / Квалификация) и протоколы всех 18 игр — по ссылкам ниже. Данные mafgame, заморожены.",
    "sections": [
      {
        "href": "participants.html?t=634",
        "title": "Участники и рейтинг",
        "desc": "44 игрока + ELO markery (тек / 2026 / Европа-2026), ожидаемый средний рейтинг состава"
      },
      {
        "href": "seating634.html",
        "title": "Интерактивная рассадка",
        "desc": "Квалификация 11 игр × 4 стола: клик по игроку — весь его маршрут; судьи по столам"
      },
      {
        "href": "cards634.html",
        "title": "Карточки игроков",
        "desc": "44 карточки: фото, ранг/ELO, столы, места за столом, соперники, маршрут; кто какую игру отдыхает"
      },
      {
        "href": "markers.html?t=634",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз за одним столом"
      },
      {
        "href": "results.html?t=634",
        "title": "Игры с результатами",
        "desc": "Все 18 игр: роли, допы, победители"
      },
      {
        "href": "standings.html?t=634",
        "title": "Сводная таблица",
        "desc": "Официальный итог + стадии Квалификация/Полуфинал/Финал"
      },
      {
        "href": "roles.html?t=634",
        "title": "Статистика по ролям",
        "desc": "Σ по ролям: мирный, шериф, мафия, дон"
      },
      {
        "href": "player.html?t=634",
        "title": "Статистика игрока",
        "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
      }
    ],
    "start": "2026-07-18",
    "top3": [
      "YeS",
      "RAMZES",
      "Саботаж"
    ],
    "mvp": "KEX"
  },
  {
    "id": "667",
    "name": "Four Seasons. Cyprus Open: Summer",
    "theme": "cyprus",
    "art": "assets/cyprus667.jpg",
    "accent": "#46c2ee",
    "posterScript": "Summer",
    "posterTitle": "CYPRUS OPEN 2026",
    "posterSub": "JUNE 13–14 · LIMASSOL",
    "dates": "13–14 июня 2026",
    "city": "Лимассол",
    "country": "Кипр",
    "players": 70,
    "days": 2,
    "stars": 4,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 16 игр (12 квал + 4 финала)",
    "organizer": "Mafia Club Cyprus · Aragil",
    "mafgame": "https://mafgame.org/tournaments/667/view",
    "note": "Завершён. 12 игр квалификации (7 столов) + финал 4 игры. Официальная итоговая таблица, финал и квалификация — раздельно. Чемпион — Tommy.",
    "sections": [
      {
        "href": "seating667.html",
        "title": "Интерактивная рассадка",
        "desc": "12 игр × 7 столов: клик по игроку — весь его маршрут по турниру"
      },
      {
        "href": "cards667.html",
        "title": "Карточки игроков",
        "desc": "70 карточек: фото, клуб, столы, слоты, соперники"
      },
      {
        "href": "standings.html?t=667",
        "title": "Статистика турнира",
        "desc": "Три таблицы: Итоговая (официальная) / Финал / Квалификация. Σ, роли R/S/B/D, блок «Сверка»"
      },
      {
        "href": "results.html?t=667",
        "title": "Игры с результатами",
        "desc": "Раунд → все 7 столов: роли, допы, победители, фото, стримы"
      },
      {
        "href": "player.html?t=667",
        "title": "Статистика игрока",
        "desc": "Итоговое место, разбивка игр квалификация/финал раздельно, стата по 4 ролям, динамика мест"
      },
      {
        "href": "roles.html?t=667",
        "title": "Статистика по ролям",
        "desc": "Σ по ролям: мирный, шериф, мафия, дон; фильтр стадии (все / квалификация / финал)"
      },
      {
        "href": "markers.html?t=667",
        "title": "Совместные посадки",
        "desc": "Матрица: кто с кем сколько раз сидел за одним столом за турнир"
      }
    ],
    "start": "2026-06-13",
    "top3": [
      "Tommy",
      "doc",
      "Золушка"
    ],
    "mvp": "Tommy"
  },
  {
    "id": "826",
    "name": "Битва Чемпионов 2026",
    "dates": "23–24 мая 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 30,
    "days": 2,
    "stars": 4,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён · 15 игр",
    "organizer": "Mafia club «Champions League» Prague",
    "mafgame": "https://mafgame.org/tournaments/826/view",
    "note": "Полный турнир: официальная таблица, награды, все 15 игр с протоколами. Чемпион — Логика.",
    "sections": [
      {
        "href": "standings.html?t=826",
        "title": "Сводная таблица",
        "desc": "Официальный итог + динамика «после игры N»: Σ, R/S/B/D, награды"
      },
      {
        "href": "results.html?t=826",
        "title": "Игры с результатами",
        "desc": "Все 15 игр × 3 стола: роли, допы, фото, победители, стримы"
      },
      {
        "href": "seating.html",
        "title": "Рассадка по играм",
        "desc": "3 круглых стола в каждой из 15 игр, все столы и слоты игрока"
      },
      {
        "href": "cards.html",
        "title": "Карточки игроков",
        "desc": "30 карточек: столы, слоты, частота совместных игр"
      },
      {
        "href": "player.html?t=826",
        "title": "Все игроки",
        "desc": "Список 30 игроков, разбивка по сыгранным играм"
      }
    ],
    "start": "2026-05-23",
    "top3": [
      "Логика",
      "Сью",
      "Season's"
    ],
    "mvp": "Логика"
  },
  {
    "id": "622",
    "name": "MafiaCL Championship",
    "dates": "14 марта 2026",
    "city": "Прага",
    "country": "Чехия",
    "players": 33,
    "days": 1,
    "stars": 3,
    "status": "finished",
    "phase": 1,
    "statusLabel": "Завершён",
    "organizer": "Mafia club «Champions League» Prague",
    "mafgame": "https://mafgame.org/tournaments/622/view",
    "note": "Полный турнир: 3 стадии, итоговые таблицы и номинации.",
    "sections": [
      {
        "href": "standings.html?t=622",
        "title": "Сводная таблица",
        "desc": "33 игрока · 3 стадии · awards"
      },
      {
        "href": "results.html?t=622",
        "title": "Игры с результатами",
        "desc": "8 игр квалификации — роли, доп баллы, цветной центр стола"
      },
      {
        "href": "player.html?t=622",
        "title": "Карточки игроков",
        "desc": "Места по стадиям · номинации · разбивка по играм"
      }
    ],
    "start": "2026-03-14",
    "top3": [
      "Landing",
      "f5",
      "Виталий"
    ],
    "mvp": "Landing"
  }
]
};
