// MafgameStat · data/tournaments.js · v1.1 · 2026-06-12 · реестр турниров (источник правды для index.html и tournament.html)
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
      "note": "Турнир стартует 13 июня. Данные игр появятся здесь по ходу турнира.",
      "sections": [
        {"title": "Карточки игроков", "desc": "70 карточек: фото, ELO глобальный и за 12 мес, какой по счёту это турнир для игрока", "soon": true},
        {"title": "Статистика турнира", "desc": "Сводная таблица + ползунок «после игры N», победы красных/чёрных, разбивка по ролям R / S / B / D", "soon": true},
        {"title": "Интерактивная рассадка", "desc": "Столы по играм: сыгранные приглушены, следующая подсвечена. Клик по игроку — весь его маршрут", "soon": true},
        {"title": "Игры с результатами", "desc": "Раунд → все столы: роли, допы, победители. Фото игроков, яркое деление команд", "soon": true},
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
      "statusLabel": "Завершён",
      "organizer": "Mafia club «Champions League» Prague",
      "mafgame": "https://mafgame.org/tournaments/826/view",
      "note": "На сайте — live-срез первых 4 из 15 игр квалификации. Полные итоги — на mafgame.org.",
      "sections": [
        {"href": "standings.html?t=826", "title": "Сводная таблица", "desc": "Промежуточный рейтинг по 4 сыгранным играм: Σ, Σap, победы, K"},
        {"href": "results.html?t=826", "title": "Игры с результатами", "desc": "4 сыгранных стола × 3 — роли, доп баллы, цветной центр стола"},
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
