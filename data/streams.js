// MafgameStat · data/streams.js · v1.7 · 2026-09-10 · ЧМ-710: +комментаторская дня 2 (HsyqZA_6V0k, от Валерия) · v1.6 · 2026-09-10 · ЧМ-710: вписаны 12 ID из плейлиста Mafia World Championship 2026 (день 1 столы 1–5 + комментаторская, день 2 столы 1–5, финал); комментаторской на день 2 в плейлисте пока нет — страницы падают на день 1 · v1.5 · 2026-09-10 · +заготовка 710 (ЧМ-2026, Прага): 5 столов, главный эфир комментатора — commentary[day], gamesDay1=8 — ГИПОТЕЗА, уточнить по расписанию; ссылки впишем когда орги опубликуют · v1.4 · 2026-08-22 · +заготовка 694 (Central Euro Cup, Прага): 3 стола, gamesDay1 уточнить по факту (пока 6); ссылки вписать когда появятся трансляции — кнопки на сайте включатся сами · v1.3 · 2026-07-18 · ссылки ЧЕ-634 вписаны (плейлист @mafgameorg, титулы сверены oEmbed): день 1 столы 1-4, день 2 столы 1-4, финал · v1.2 · 2026-07-17 · +заготовка 634 (ЧЕ): день1 = игры 1-9, день2 = 10-11 + полуфинал; final — отдельный стрим финала. Ссылки вписать в день турнира — кнопки на сайте появятся сами. · v1.1 · 2026-06-14 · трансляции YouTube @mafgameorg: турнир → день → стол → videoId
// правило: игра N → день 1 если N <= gamesDay1, иначе день 2
window.STREAMS_DB = {
  "channel": "https://www.youtube.com/@mafgameorg",
  "710": {
    "gamesDay1": 8,
    "days": {
      "1": {"1":"7k5M0oEGXZs","2":"txIps74ftbU","3":"ooHNwmzalO4","4":"5xzUo7FvDM4","5":"W3q32nFgV7k"},
      "2": {"1":"UZrv4iyCxUo","2":"0ibZYJhGwuQ","3":"-qg3JY8B63E","4":"1VE4a-Cp5QA","5":"GvhGLPQc5s0"}
    },
    "commentary": {"1":"vu-6aK_tdN4","2":"HsyqZA_6V0k"},
    "final": "cgl-EsSu5Pk",
    "playlist": "https://www.youtube.com/playlist?list=PLXdDgdvp5aJs"
  },
  "694": {
    "gamesDay1": 6,
    "days": {
      "1": {},
      "2": {}
    }
  },
  "634": {
    "gamesDay1": 9,
    "days": {
      "1": {"1":"mJLwDJ2z4Xs","2":"e5YdLN0HO28","3":"JJcE1Jmt8Jw","4":"sNYDxPQUuMQ"},
      "2": {"1":"SZgXjykMG80","2":"ruQbp0jYZfA","3":"YFu-hx5Deps","4":"1m4DoxJLTUo"}
    },
    "final": "-Erzky4iGgk"
  },
  "667": {
    "gamesDay1": 7,
    "days": {
      "1": {"1":"ATlCCOquogQ","2":"yM0jGib3-gU","3":"ZZGk8Et7I9M","4":"Fp_AwLLnsUQ","5":"fVr2d32qNgA","6":"FeRd5JWGnPs","7":"Vbb4YtOO9zg"},
      "2": {"1":"fEDRvWSF584","2":"aCtLtIeLxNg","3":"TyGQsYkCBLE","4":"OxIE2K80VD8","5":"m--ze8D4wxI","6":"62w0gU799lI","7":"LC5xCihkgD8"}
    },
    "commentary": {"1":"etcrBoqaPYM","2":"vND46wjEZIA"},
    "final": "5vYHSNgP-mM"
  },
  "826": {
    "gamesDay1": 8,
    "days": {
      "1": {"1":"RnH2wJjOtMg","2":"4P8KorUGPTI","3":"UvmSIF4FFv8"},
      "2": {"1":"nO0ezdxl94E","2":"8_C4rOaTA_M","3":"nUskeCf4in8"}
    }
  }
};
window.streamFor = function(tid, gameNum, tableNum) {
  const s = window.STREAMS_DB[String(tid)];
  if (!s || !s.days) return null;
  const day = gameNum <= (s.gamesDay1 || 8) ? "1" : "2";
  const id = (s.days[day] || {})[String(tableNum)];
  return id ? "https://www.youtube.com/watch?v=" + id : null;
};
