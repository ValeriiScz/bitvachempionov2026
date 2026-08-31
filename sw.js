/* ============================================================================
   MafgameStat · sw.js (Service Worker для PWA) · v1.14 · 2026-08-27 (кэш v19.3: ФИКС — медиа и Range-запросы мимо воркера (из-за 206 не открывался ролик-анонс); v19.2: календарь с городами в клетках и карточками серий, кнопка «наверх»; v19.1: карточки победителей 9 серий из канала, финал золотым в календаре; MCL разрезан на 4 страницы — mcl2026/mcl-standings/mcl-series/mcl-lab + data/mcl2026.js в прекэше; видео не кэшируем)
   Назначение: офлайн-кэш ОБОЛОЧКИ сайта (html/js/иконки) + установка как
   приложение. Данные турниров НЕ замораживаются кэшем.

   Стратегии:
   1) /mafgame/*  → ТОЛЬКО сеть (bypass, никакого кэша). Live-данные всегда
      свежие; при офлайне fetch падает → live.js сам отдаёт снимок из
      localStorage (snapScore/notRegression). Защиту снимка НЕ трогаем.
   2) data/*.json → network-first: сеть, при фейле — кэш (офлайн-просмотр
      завершённых турниров), успешные ответы кладём в кэш данных.
   3) Оболочка (html/js/svg/png/jpg, google-fonts) → stale-while-revalidate:
      мгновенно из кэша + фоновое обновление. Даже если забыли поднять
      CACHE_VERSION при деплое, новый код подтянется со 2-го открытия.

   ДЕПЛОЙ: поднять CACHE_VERSION (…-v11.24, -v11.25…) при каждом релизе —
   старые кэши удаляются на activate.
   ============================================================================ */
'use strict';

const CACHE_VERSION = 'mafgamestat-v20';
const SHELL_CACHE = CACHE_VERSION + '-shell';
const DATA_CACHE  = CACHE_VERSION + '-data';

/* Ядро оболочки — докачивается при установке (без постеров: они тяжёлые,
   докэшируются на лету при первом просмотре). */
const PRECACHE = [
  'index.html',
  'ce634.html',
  'ce694.html',
  'research2025.html',
  'mcl2026.html',
  'mcl-standings.html',
  'mcl-series.html',
  'mcl-lab.html',
  'data/mcl2026.js',
  'gmc2026.html',
  'calendar.html',
  'assets/mcl/logo-white.png',
  'assets/mcl/hero.jpg',
  'tournament.html',
  'participants.html',
  'data/tournaments.js',
  'data/live.js',
  'data/streams.js',
  'assets/favicon.svg',
  'assets/icons/icon-192.png',
  'assets/icons/icon-512.png',
  'manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(SHELL_CACHE)
      .then(c => c.addAll(PRECACHE))
      .catch(() => null) /* частичный фейл прекэша не блокирует установку */
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => !k.startsWith(CACHE_VERSION)).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return; /* не-GET не трогаем */
  const url = new URL(req.url);

  /* 0) МЕДИА И RANGE-ЗАПРОСЫ — мимо воркера.
     Видео браузер тянет кусками (Range → ответ 206 Partial Content), а 206
     нельзя положить в Cache API: cache.put бросает исключение, respondWith
     отдаёт ошибку и ролик не открывается вообще. Поэтому не трогаем. */
  if (req.headers.has('range') ||
      /\.(mp4|webm|m4v|mov|ogv|mp3|m4a|ogg|wav)$/i.test(url.pathname)) return;

  /* 1) live-прокси mafgame — только сеть, никакого кэша */
  if (url.pathname.startsWith('/mafgame/')) return;

  /* 2) данные турниров (*.json) — network-first с кэш-фолбэком */
  if (url.origin === location.origin && url.pathname.endsWith('.json') && url.pathname !== '/manifest.json') {
    e.respondWith(
      fetch(req).then(res => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(DATA_CACHE).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() => caches.match(req))
    );
    return;
  }

  /* 3) оболочка (same-origin + google fonts) — stale-while-revalidate */
  const isFonts = url.hostname.endsWith('gstatic.com') || url.hostname.endsWith('googleapis.com');
  if (url.origin !== location.origin && !isFonts) return; /* прочий кросс-домен не трогаем */

  e.respondWith(
    caches.open(SHELL_CACHE).then(cache =>
      cache.match(req).then(cached => {
        const fresh = fetch(req).then(res => {
          /* в кэш кладём только полные ответы (200) и opaque; put может бросить — гасим */
          if (res && (res.status === 200 || res.type === 'opaque')) {
            cache.put(req, res.clone()).catch(() => {});
          }
          return res;
        }).catch(() => cached); /* офлайн → отдаём кэш (или undefined) */
        return cached || fresh;
      })
    )
  );
});
