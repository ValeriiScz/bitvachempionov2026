// api/lead.js · v1.0 · 20.10.2026 — приём заявок раздела «Шпионаж» (spy.html).
// POST {k:'demo'|'buy'|'more', p:'dossier'|…, player, nick, tg, note} → пишет строку в лог Vercel (видно в runtime logs)
// и, если заданы TG_BOT_TOKEN и TG_CHAT_ID, шлёт сообщение в Telegram. Без базы: хранилище Blob в проекте недоступно (403).
// Ответ: {ok:true, n:<номер заявки за этот запуск функции>}.
let seq = 0;
const PNAME = { dossier: 'Досье на игрока', series: 'Подготовка к серии', tourn: 'Подготовка к турниру', final: 'Финалы и ELO-гонка', agent: 'База + ИИ-агент', demo: 'Демо-досье', wait: 'Лист ожидания' };
module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  b = b || {};
  const clean = (s, n) => String(s == null ? '' : s).replace(/[\r\n\t]+/g, ' ').trim().slice(0, n);
  const lead = {
    t: new Date().toISOString(),
    k: clean(b.k, 10) || 'click',
    p: clean(b.p, 12) || '-',
    player: clean(b.player, 40),
    nick: clean(b.nick, 40),
    tg: clean(b.tg, 40),
    note: clean(b.note, 300),
    ua: clean(req.headers['user-agent'], 80),
    ip: clean((req.headers['x-forwarded-for'] || '').split(',')[0], 45),
    country: clean(req.headers['x-vercel-ip-country'], 4),
  };
  seq += 1;
  console.log('SPY_LEAD ' + JSON.stringify(lead));
  const tok = process.env.TG_BOT_TOKEN, chat = process.env.TG_CHAT_ID;
  let tgOk = false;
  if (tok && chat) {
    const kind = lead.k === 'demo' ? '🎁 ДЕМО-ДОСЬЕ' : lead.k === 'buy' ? '💰 ЗАПРОС' : lead.k === 'more' ? '👀 подробнее' : lead.k === 'wait' ? '⏳ лист ожидания' : '•';
    const text = [`${kind} · ${PNAME[lead.p] || lead.p}`, lead.player ? `на кого: ${lead.player}` : '', lead.nick ? `ник: ${lead.nick}` : '', lead.tg ? `tg: ${lead.tg}` : '', lead.note ? `— ${lead.note}` : '', `${lead.country || '??'} · ${lead.t.slice(0, 16).replace('T', ' ')}`].filter(Boolean).join('\n');
    try {
      const r = await fetch(`https://api.telegram.org/bot${tok}/sendMessage`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ chat_id: chat, text, disable_web_page_preview: true }) });
      tgOk = r.ok;
    } catch (e) { console.log('SPY_LEAD tg error ' + e.message); }
  }
  return res.status(200).json({ ok: true, n: seq, tg: tgOk });
};
