// MafgameStat · data/streams.js · v1.1 · 2026-06-14 · трансляции YouTube @mafgameorg: турнир → день → стол → videoId
// правило: игра N → день 1 если N <= gamesDay1, иначе день 2
window.STREAMS_DB = {
  "channel": "https://www.youtube.com/@mafgameorg",
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
