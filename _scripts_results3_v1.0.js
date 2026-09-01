/* results3 · v1.0 · 2026-09-01
   Назначение: собрать data/results3.js — топ-3 призёров прошедших турниров для карточек календаря.
   Запуск: node _scripts_results3_v1.0.js   (из корня репозитория сайта)

   Оглавление
     1  источники данных
     2  сборка
     3  запись файла

   Источники (что есть на сегодня):
     - data/mcl2026.js        → MCL.series[].top = [[ник, балл], ...]  → 12 этапов MCL
     - data/tournament_<id>.json → .winners = [ник, ник, ник]          → 8 разобранных турниров
   Чего нет: результаты остальных ~173 прошедших турниров. Их надо один раз выгрузить
   с mafgame через Chrome Валерия и дописать сюда четвёртым источником.

   Формат на выходе:
     window.RES3  = { <id турнира>: [ник1, ник2, ник3] }
     window.RES3T = { <id>: 1 }  — где призёры это команды, а не игроки
*/
'use strict';
const fs = require('fs');

/* 1 · источники */
const MANUAL_TOURNAMENTS = [622, 634, 667, 693, 694, 702, 766, 826];
const TEAM_TOURNAMENTS   = [693];

/* 2 · сборка */
const R = {}, T = {};
global.window = {};
eval(fs.readFileSync('data/mcl2026.js', 'utf8').replace(/window\./g, 'global.'));
(global.MCL.series || []).forEach(s => {
  if (s.top && s.top.length) R[s.id] = s.top.slice(0, 3).map(x => x[0]);
});
for (const id of MANUAL_TOURNAMENTS) {
  const j = JSON.parse(fs.readFileSync('data/tournament_' + id + '.json', 'utf8'));
  if (j.winners && j.winners.length) R[id] = j.winners.slice(0, 3);
}
TEAM_TOURNAMENTS.forEach(id => { if (R[id]) T[id] = 1; });

/* 3 · запись */
const head = '/* results3.js — призёры прошедших турниров (топ-3).\n' +
  '   Источники: data/mcl2026.js (этапы MCL) и data/tournament_<id>.json (разобранные турниры).\n' +
  '   Генератор: _scripts_results3_v1.0.js. Турниров с данными: ' + Object.keys(R).length + '.\n' +
  '   Остальные прошедшие ждут выгрузки результатов с mafgame. */\n';
fs.writeFileSync('data/results3.js', head + 'window.RES3=' + JSON.stringify(R) + ';\nwindow.RES3T=' + JSON.stringify(T) + ';\n');
console.log('турниров с призёрами:', Object.keys(R).length);
