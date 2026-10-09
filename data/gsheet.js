/* DOVOD · data/gsheet.js · v1.0 · 2026-10-09
   Назначение: живые правки сайта из Google-таблицы «DOVOD · правки сайта (эфиры, игроки)» —
   без выкладки и без мака. Таблицу можно править с телефона, страницы перечитывают её сами.
   Оглавление: 1) ID таблицы · 2) чтение вкладки (gviz CSV) · 3) парсер CSV · 4) ссылка YouTube → id
               5) DOVOD_SHEET.streams(tid) · 6) DOVOD_SHEET.players(tid)
   Правило: таблица — слой ПРАВОК поверх данных сайта. Пустая ячейка = берём своё. Таблица недоступна = сайт работает как раньше.
   ⚠ Вкладка «Эфиры» хранит день/стол одной ТЕКСТОВОЙ колонкой «эфир» («день 1 · стол 2», «финал») — gviz выбрасывает
     значения меньшинства в колонках смешанного типа (числа + текст), поэтому числа и «финал» в одной колонке держать нельзя. */
(function(){
  const ID='1jLeVTGSVDefR-NEUgoG1ParZaYDVIH84ziKkmGN_GgU';
  const cache={};
  function url(tab){return 'https://docs.google.com/spreadsheets/d/'+ID+'/gviz/tq?tqx=out:csv&headers=1&sheet='+encodeURIComponent(tab)+'&cb='+Date.now();}
  function parseCSV(t){const rows=[];let row=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];
      if(q){if(c==='"'){if(t[i+1]==='"'){f+='"';i++;}else q=false;}else f+=c;}
      else if(c==='"')q=true;else if(c===','){row.push(f);f='';}else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;row.push(f);rows.push(row);row=[];f='';}else f+=c;}
    if(f!==''||row.length){row.push(f);rows.push(row);}
    if(!rows.length)return [];const h=rows[0].map(x=>x.trim().toLowerCase());
    return rows.slice(1).filter(r=>r.some(x=>String(x).trim()!=='')).map(r=>{const o={};h.forEach((k,i)=>o[k]=(r[i]==null?'':String(r[i]).trim()));return o;});}
  async function tab(name,timeoutMs){
    const ctl=window.AbortController?new AbortController():null;const tm=setTimeout(()=>{try{ctl&&ctl.abort();}catch(e){}},timeoutMs||3000);
    try{const r=await fetch(url(name),{cache:'no-store',signal:ctl?ctl.signal:undefined});clearTimeout(tm);if(!r.ok)return null;
      const t=await r.text();if(/^\s*</.test(t))return null; /* пришла HTML-страница входа = таблица закрыта */
      return (cache[name]=parseCSV(t));}catch(e){clearTimeout(tm);return cache[name]||null;}}
  function ytId(s){s=String(s||'').trim();if(!s)return null;
    let m=s.match(/(?:v=|youtu\.be\/|\/live\/|\/embed\/|\/shorts\/)([A-Za-z0-9_-]{11})/);if(m)return m[1];
    m=s.match(/\/channel\/(UC[A-Za-z0-9_-]{20,})/);if(m)return 'live:'+m[1];
    if(/^[A-Za-z0-9_-]{11}$/.test(s))return s;
    if(/^https?:\/\//.test(s))return 'url:'+s; /* @канал и прочее — встроить нельзя, покажем кнопку «на YouTube» */
    return null;}
  async function streams(tid){const rows=await tab('Эфиры');if(!rows)return null;const out={days:{},n:0};
    rows.filter(r=>String(r['турнир']).replace(/\.0+$/,'')===String(tid)).forEach(r=>{const id=ytId(r['ссылка']);if(!id)return;const e=(r['эфир']||'').toLowerCase();
      if(/финал/.test(e)){out.final=id;out.n++;return;}
      const d=(e.match(/день\s*(\d)/)||[])[1],t=(e.match(/стол\s*(\d)/)||[])[1];if(!d||!t)return;(out.days[d]=out.days[d]||{})[t]=id;out.n++;});
    return out;}
  async function players(tid){const rows=await tab('Игроки');if(!rows)return null;const out={};
    rows.filter(r=>{const t=String(r['турнир']).replace(/\.0+$/,'');return !t||t==='*'||t===String(tid);}).forEach(r=>{const n=r['ник'];if(!n)return;
      const elo=parseFloat(String(r['elo']).replace(',','.'));const mid=parseInt(r['markery_id'],10);
      out[n]={elo:isFinite(elo)?Math.round(elo):null,markery_id:isFinite(mid)?mid:null,note:r['примечание']||''};});
    return out;}
  /* применить правки к массиву игроков participants_*.json (мутирует) */
  function tierOf(e){if(e==null)return null;const T=[[1600,'L'],[1300,'S'],[1190,'A'],[1075,'B'],[994,'C'],[937,'D'],[880,'E']];for(const [th,t] of T)if(e>=th)return t;return 'F';}
  function applyPlayers(list,ov){if(!ov||!list)return 0;let n=0;list.forEach(p=>{const o=ov[p.nick];if(!o)return;
      if(o.elo!=null&&o.elo!==p.r_elo_cur){p.r_elo_cur=o.elo;n++;}
      const start=/новичок|стартов/i.test(o.note||'');p.elo_start=start||undefined;p.r_tier=(p.r_elo_cur!=null&&!start)?tierOf(p.r_elo_cur):null;
      if(o.markery_id!=null)p.markery_id=o.markery_id;});return n;}
  window.DOVOD_SHEET={id:ID,tab,streams,players,applyPlayers,ytId,tierOf};
})();
