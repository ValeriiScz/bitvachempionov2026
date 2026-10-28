/* DOVOD · api/social.js · v1.0 · 2026-10-29
   Просмотры, реакции и комментарии к открытым статьям (Vercel Edge Function + Upstash Redis по REST).
   Регистрации нет: посетитель — случайный id в localStorage браузера (vid), комментарий — ник + текст.
   Хранилище: Redis из Vercel Marketplace (Upstash). Переменные окружения ставит сама интеграция:
   KV_REST_API_URL / KV_REST_API_TOKEN или UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN.
   Пока хранилище не подключено — отвечаем 503, и виджет на странице просто не показывается.

   GET  /api/social?a=<slug>&vid=<id>            → {views, reactions:{k:n}, mine:[k], comments:[{n,t,ts}]}
   POST /api/social  {a, vid, op:'view'}          → засчитать просмотр (уникальный посетитель, HyperLogLog)
   POST /api/social  {a, vid, op:'react', k, on}  → поставить / снять реакцию k
   POST /api/social  {a, vid, op:'comment', n, t, hp} → комментарий (hp — ловушка для ботов, должна быть пустой)

   Ключи Redis: s:<slug>:v (PF), s:<slug>:r:<k> (SET vid), s:<slug>:c (LIST JSON, новые сверху), rl:<ip> (антиспам).
   Удалить комментарий: в консоли Upstash — LREM s:<slug>:c 1 '<json строки>'. */
export const config = { runtime: 'edge' };

const SLUG = /^[a-z0-9-]{3,60}$/;
const VID = /^[A-Za-z0-9_-]{8,40}$/;
const REACT = ['fire', 'target', 'wow', 'hmm', 'lol'];
const MAX_COMMENTS = 300;

function env() {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const tok = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
  return url && tok ? { url, tok } : null;
}
async function redis(E, cmds) {
  const r = await fetch(E.url.replace(/\/$/, '') + '/pipeline', {
    method: 'POST',
    headers: { authorization: 'Bearer ' + E.tok, 'content-type': 'application/json' },
    body: JSON.stringify(cmds)
  });
  if (!r.ok) throw new Error('redis ' + r.status);
  return (await r.json()).map(x => x.result);
}
const J = (o, s = 200) => new Response(JSON.stringify(o), {
  status: s, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
});
const clean = (s, n) => String(s || '').replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, '').replace(/\s+\n/g, '\n').trim().slice(0, n);

async function state(E, a, vid) {
  const cmds = [['PFCOUNT', `s:${a}:v`], ['LRANGE', `s:${a}:c`, 0, 199]];
  for (const k of REACT) cmds.push(['SCARD', `s:${a}:r:${k}`]);
  if (vid) for (const k of REACT) cmds.push(['SISMEMBER', `s:${a}:r:${k}`, vid]);
  const res = await redis(E, cmds);
  const reactions = {}, mine = [];
  REACT.forEach((k, i) => { reactions[k] = res[2 + i] || 0; if (vid && res[2 + REACT.length + i]) mine.push(k); });
  const comments = (res[1] || []).map(x => { try { return JSON.parse(x); } catch (e) { return null; } }).filter(Boolean);
  return { views: res[0] || 0, reactions, mine, comments };
}

export default async function handler(req) {
  const E = env();
  if (!E) return J({ off: 1 }, 503);
  const u = new URL(req.url);
  try {
    if (req.method === 'GET') {
      const a = u.searchParams.get('a') || '', vid = u.searchParams.get('vid') || '';
      if (!SLUG.test(a)) return J({ err: 'a' }, 400);
      return J(await state(E, a, VID.test(vid) ? vid : ''));
    }
    if (req.method !== 'POST') return J({ err: 'method' }, 405);
    const b = await req.json().catch(() => ({}));
    const a = String(b.a || ''), vid = String(b.vid || '');
    if (!SLUG.test(a) || !VID.test(vid)) return J({ err: 'bad' }, 400);
    const ip = (req.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'x';

    if (b.op === 'view') {
      await redis(E, [['PFADD', `s:${a}:v`, vid]]);
      return J({ ok: 1 });
    }
    if (b.op === 'react') {
      if (!REACT.includes(b.k)) return J({ err: 'k' }, 400);
      await redis(E, [[b.on ? 'SADD' : 'SREM', `s:${a}:r:${b.k}`, vid]]);
      return J(await state(E, a, vid));
    }
    if (b.op === 'comment') {
      if (b.hp) return J({ ok: 1 });                       // бот заполнил скрытое поле — молча игнорируем
      const n = clean(b.n, 32), t = clean(b.t, 1000);
      if (n.length < 2 || t.length < 2) return J({ err: 'Напишите ник и текст' }, 400);
      if ((t.match(/https?:\/\//g) || []).length > 2) return J({ err: 'Слишком много ссылок' }, 400);
      const rl = await redis(E, [['SET', `rl:${ip}`, '1', 'NX', 'EX', 30]]);
      if (rl[0] !== 'OK') return J({ err: 'Чуть подождите — не чаще раза в 30 секунд' }, 429);
      const row = JSON.stringify({ n, t, ts: Date.now() });
      await redis(E, [['LPUSH', `s:${a}:c`, row], ['LTRIM', `s:${a}:c`, 0, MAX_COMMENTS - 1]]);
      return J(await state(E, a, vid));
    }
    return J({ err: 'op' }, 400);
  } catch (e) {
    return J({ err: 'store' }, 502);
  }
}
