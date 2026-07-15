// MafgameStat | tournaments.js | v2.9 | 2026-07-16 | ЧЕ-634 -> upcoming(Скоро) премиум: постер Бонна, золотой accent, приз 3000€/5★, разлочены seating634/cards634/standings/results/roles/player; судьи столов
// MafgameStat | tournaments.js | v2.8 | 2026-07-15 | ЧЕ-634: свежий состав 44 подтв. + пересчитанный markery (eloAvg 1057/43); statusLabel и note обновлены
// MafgameStat | tournaments.js | v2.7 | 2026-07-04 | +start-даты для сортировки архива по дате; 702 live+закат; 766 finished (чемпион Lюц)
// MafgameStat | tournaments.js | v2.6 | 2026-07-03 | 766->finished (16/16, чемпион Lюц, store убран) + 702->upcoming(Скоро): рассадка 12x4, cards/seating702, live-подтяжка, постер cologne702, eloAvg 997/37
// MafgameStat · data/tournaments.js · v2.4 · 2026-06-21 · 693 live: разлочена карточка «Статистика игрока» (player.html?t=693)
// MafgameStat · data/tournaments.js · v2.3 · 2026-06-20 · 4 статуса (live/soon/gathering/finished) + поле phase для порядка главной (2→3→4→1);
//   +702 Кубок Кёльна, +634 Чемпионат Европы (оба «собирается»); счётчик ожид. ELO (markery) на плашках; участники+двойной рейтинг; accent per-турнир.
// MafgameStat | tournaments.js | v2.5 | 2026-06-25 | 766->upcoming(Скоро)+разлок seating/cards/stat+live(in_progress)+store; fix player.html?t=693
window.TOURNAMENTS_DB = {
  "tournaments": [
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
      "start": "2026-06-20"
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
      "start": "2026-06-27"
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
      "start": "2026-07-04"
    },
    {
      "id": "634",
      "theme": "poster",
      "art": "assets/bonn634.jpg",
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
      "status": "upcoming",
      "phase": 3,
      "statusLabel": "Скоро · старт 18 июля · 5★ · приз 3000€",
      "eloAvg": 1057,
      "eloN": 43,
      "eloTotal": 44,
      "organizer": "Mafgame · World Alliance League",
      "mafgame": "https://mafgame.org/tournaments/634/view",
      "note": "★★★★★ Титульный турнир сезона — победитель становится чемпионом Европы. Призовой фонд 3000€, Бонн (Германия), 44 игрока. Рассадка квалификации готова (11 игр × 4 стола, каждый играет 10). Полуфинал (топ-40, 2 игры) и финал (топ-10, 4 игры) сеются после квалификации. Судьи столов: I — Рыба-мÓя, II — Гармония, III — Тринити, IV — Кура. Статистика включится автоматически после первой игры — данные тянутся с mafgame вживую.",
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
          "desc": "До старта — рассадка; результаты появятся вживую после первой игры"
        },
        {
          "href": "standings.html?t=634",
          "title": "Сводная таблица",
          "desc": "Σ, роли, стадии Квалификация/Полуфинал/Финал — появится после первой игры"
        },
        {
          "href": "roles.html?t=634",
          "title": "Статистика по ролям",
          "desc": "Σ по ролям: мирный, шериф, мафия, дон — после старта"
        },
        {
          "href": "player.html?t=634",
          "title": "Статистика игрока",
          "desc": "Маршруты, роли, соперники и зачёт каждого игрока"
        }
      ],
      "start": "2026-07-18"
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
      "start": "2026-06-13"
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
      "start": "2026-05-23"
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
      "start": "2026-03-14"
    }
  ]
};
