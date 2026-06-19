// MafgameStat · data/tournaments.js · v1.7 · 2026-06-19 · +693 (парный, рассадка готова) +766 (скоро); 667 +«Совместные посадки»; матрица маркеров для новых турниров
window.TOURNAMENTS_DB = {
  "tournaments": [
    {
      "id": "766",
      "name": "Four Seasons: Poland Mafia Open 2026",
      "dates": "27–28 июня 2026",
      "city": "Польша",
      "country": "Польша",
      "players": 40,
      "days": 2,
      "stars": 4,
      "status": "upcoming",
      "statusLabel": "Скоро · 27–28 июня",
      "organizer": "Four Seasons",
      "mafgame": "https://mafgame.org/tournaments/766/view",
      "note": "12 игр квалификации + финал 4 игры. Данные появятся ближе к старту.",
      "sections": [
        {"title": "Сводная таблица", "desc": "Итоговая / Финал / Квалификация — после старта", "soon": true},
        {"title": "Игры с результатами", "desc": "Раунды и столы — после старта", "soon": true},
        {"title": "Статистика игрока", "desc": "Появится после старта", "soon": true}
      ]
    },
    {
      "id": "693",
      "name": "MafiaCl Protocol 4 2026",
      "dates": "20–21 июня 2026",
      "city": "Прага",
      "country": "Чехия",
      "players": 20,
      "days": 2,
      "stars": 2,
      "status": "upcoming",
      "statusLabel": "Скоро · парный · 20–21 июня",
      "organizer": "Mafia club «Champions League» Prague · судьи Trinity, Yokai",
      "mafgame": "https://mafgame.org/tournaments/693/view",
      "note": "Парный турнир: 10 команд по 2 игрока, 15 игр (2 стола), без финала. Рассадка уже готова; результаты — после старта. Судьи: стол I — Trinity, стол II — Yokai.",
      "sections": [
        {"href": "results.html?t=693", "title": "Рассадка по играм", "desc": "15 игр × 2 стола: кто за каким столом (готова до старта)"},
        {"href": "markers.html?t=693", "title": "Совместные посадки", "desc": "Матрица: кто с кем сколько раз за одним столом"},
        {"href": "standings.html?t=693", "title": "Команды", "desc": "10 команд по 2 игрока; результаты — после старта"},
        {"title": "Статистика игрока", "desc": "Появится после старта", "soon": true}
      ]
    },
    {
      "id": "667",
      "name": "Four Seasons. Cyprus Open: Summer",
      "theme": "cyprus",
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
      "statusLabel": "Завершён · 16 игр (12 квал + 4 финала)",
      "organizer": "Mafia Club Cyprus · Aragil",
      "mafgame": "https://mafgame.org/tournaments/667/view",
      "note": "Завершён. 12 игр квалификации (7 столов) + финал 4 игры. Официальная итоговая таблица, финал и квалификация — раздельно. Чемпион — Tommy.",
      "sections": [
        {"href": "seating667.html", "title": "Интерактивная рассадка", "desc": "12 игр × 7 столов: клик по игроку — весь его маршрут по турниру"},
        {"href": "cards667.html", "title": "Карточки игроков", "desc": "70 карточек: фото, клуб, столы, слоты, соперники"},
        {"href": "standings.html?t=667", "title": "Статистика турнира", "desc": "Три таблицы: Итоговая (официальная) / Финал / Квалификация. Σ, роли R/S/B/D, блок «Сверка»"},
        {"href": "results.html?t=667", "title": "Игры с результатами", "desc": "Раунд → все 7 столов: роли, допы, победители, фото, стримы"},
        {"href": "player.html?t=667", "title": "Статистика игрока", "desc": "Итоговое место, разбивка игр квалификация/финал раздельно, стата по 4 ролям, динамика мест"},
        {"href": "roles.html?t=667", "title": "Статистика по ролям", "desc": "Σ по ролям: мирный, шериф, мафия, дон; фильтр стадии (все / квалификация / финал)"},
        {"href": "markers.html?t=667", "title": "Совместные посадки", "desc": "Матрица: кто с кем сколько раз сидел за одним столом за турнир"}
      ]
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
      "statusLabel": "Завершён · 15 игр",
      "organizer": "Mafia club «Champions League» Prague",
      "mafgame": "https://mafgame.org/tournaments/826/view",
      "note": "Полный турнир: официальная таблица, награды, все 15 игр с протоколами. Чемпион — Логика.",
      "sections": [
        {"href": "standings.html?t=826", "title": "Сводная таблица", "desc": "Официальный итог + динамика «после игры N»: Σ, R/S/B/D, награды"},
        {"href": "results.html?t=826", "title": "Игры с результатами", "desc": "Все 15 игр × 3 стола: роли, допы, фото, победители, стримы"},
        {"href": "seating.html", "title": "Рассадка по играм", "desc": "3 круглых стола в каждой из 15 игр, все столы и слоты игрока"},
        {"href": "cards.html", "title": "Карточки игроков", "desc": "30 карточек: столы, слоты, частота совместных игр"},
        {"href": "player.html?t=826", "title": "Все игроки", "desc": "Список 30 игроков, разбивка по сыгранным играм"}
      ]
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
      "statusLabel": "Завершён",
      "organizer": "Mafia club «Champions League» Prague",
      "mafgame": "https://mafgame.org/tournaments/622/view",
      "note": "Полный турнир: 3 стадии, итоговые таблицы и номинации.",
      "sections": [
        {"href": "standings.html?t=622", "title": "Сводная таблица", "desc": "33 игрока · 3 стадии · awards"},
        {"href": "results.html?t=622", "title": "Игры с результатами", "desc": "8 игр квалификации — роли, доп баллы, цветной центр стола"},
        {"href": "player.html?t=622", "title": "Карточки игроков", "desc": "Места по стадиям · номинации · разбивка по играм"}
      ]
    }
  ]
};
