/* ============================================================================
   MafgameStat · sw.js (Service Worker для PWA) · v1.2 · 2026-07-17 (кэш v13)
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

const CACHE_VERSION = 'mafgamestat-v13.6';
const SHELL_CACHE = CACHE_VERSION + '-shell';
const DATA_CACHE  = CACHE_VERSION + '-data';

/* Ядро оболочки — докачивается при установке (без постеров: они тяжёлые,
   докэшируются на лету при первом просмотре). */
const PRECACHE = [
  'index.html',
  'ce634.html',
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
          if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
          return res;
        }).catch(() => cached); /* офлайн → отдаём кэш (или undefined) */
        return cached || fresh;
      })
    )
  );
});
