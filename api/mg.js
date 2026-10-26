/* DOVOD · api/mg.js · v1.0 · 2026-10-26
   Кэширующий прокси к mafgame.org (Vercel Edge Function).
   Зачем: страницы турнира во время игр опрашивают результаты каждые 15 с. Без кэша каждый зритель
   бил бы в mafgame отдельно; здесь CDN Vercel держит ответ 10 с — mafgame получает ≤1 запрос в 10 с
   на страницу, сколько бы людей ни смотрело.
   Вызов: /api/mg?p=tournaments/615/game_results   (только GET и только пути из белого списка — не открытый прокси)
   Кэш: game_results — 10 с (+20 с stale), остальное — 5 мин (+10 мин stale). Ошибки mafgame не кэшируем.
   Старый прямой rewrite /mafgame/* остаётся запасным путём (live.js откатывается на него сам). */
export const config = { runtime: 'edge' };
const OK = /^(tournaments(\/\d+(\/(view|game_results|participants|results))?)?|user\/\d+\/view)$/;
export default async function handler(req) {
  const u = new URL(req.url);
  const p = (u.searchParams.get('p') || '').replace(/^\/+|\/+$/g, '');
  if (req.method !== 'GET' || !OK.test(p)) return new Response('bad path', { status: 400 });
  const qs = new URLSearchParams(u.search); qs.delete('p'); qs.delete('cb');
  const q = qs.toString();
  const live = /game_results$/.test(p);
  let r;
  try {
    r = await fetch('https://mafgame.org/' + p + (q ? '?' + q : ''), {
      headers: { 'user-agent': 'DOVOD-site (+https://dovod-mafia.com)', 'accept': 'text/html,application/xhtml+xml' }
    });
  } catch (e) {
    return new Response('upstream error', { status: 502, headers: { 'cache-control': 'no-store' } });
  }
  const body = await r.text();
  const cdn = r.ok ? (live ? 'public, s-maxage=10, stale-while-revalidate=20' : 'public, s-maxage=300, stale-while-revalidate=600') : 'no-store';
  return new Response(body, {
    status: r.status,
    headers: {
      'content-type': r.headers.get('content-type') || 'text/html; charset=utf-8',
      'cache-control': 'public, max-age=0, must-revalidate',
      'cdn-cache-control': cdn,
      'vercel-cdn-cache-control': cdn,
      'x-dovod-proxy': 'mg1'
    }
  });
}
