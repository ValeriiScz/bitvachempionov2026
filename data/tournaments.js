// MafgameStat · data/tournaments.js · v1.2 · 2026-06-12 · реестр турниров (источник правды для index.html и tournament.html)
window.TOURNAMENTS_DB = {
  "tournaments": [
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
      "status": "upcoming",
      "statusLabel": "Старт 13 июня",
      "organizer": "Mafia Club Cyprus · Aragil",
      "mafgame": "https://mafgame.org/tournaments/667/view",
      "note": "12 игр квалификации (7 столов × 10) + финал 4 игры. Результаты игр появятся по ходу турнира.",
      "sections": [
        {"href": "seating667.html", "title": "Интерактивная рассадка", "desc": "12 игр × 7 столов: клик по игроку — весь его маршрут по турниру"},
        {"href": "cards667.html", "title": "Карточки игроков", "desc": "70 карточек: фото, клуб, столы, слоты, соперники"},
        {"title": "Статистика турнира", "desc": "Сводная таблица + срез «после игры N», победы красных/чёрных, разбивка по ролям R / S / B / D", "soon": true},
        {"title": "Игры с результатами", "desc": "Раунд → все 7 столов: роли, допы, победители, фото, стримы", "soon": true},
        {"title": "Статистика игрока", "desc": "Место после каждой игры, стата по 4 ролям, сравнение с топ-10, 11–20 и средним по турниру", "soon": true}
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
