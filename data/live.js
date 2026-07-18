/* ============================================================================
   live.js — LIVE-движок MafgameStat. Единая точка получения игр по турниру.
   API: window.loadGames(id) -> Promise<{tournament_id,games_played,games_total,games,live?}>
   Логика:
   1) Читает tournament_{id}.json.in_progress. Если true (турнир идёт):
      fetch('/mafgame/tournaments/{id}/game_results')  (Vercel rewrite -> mafgame.org),
      парсит Inertia-данные -> convertInertia() -> {games:[{title,stage,tables:[{table_num,judge,winner,seats}]}]}.
   2) ЗАЩИТА ДАННЫХ: сравнивает свежий парс с сохранённым в localStorage снимком
      (snapScore/notRegression) — НЕ затирает хорошие данные пустыми/обнулёнными/
      пропавшими (частый глюк mafgame при обновлении таблицы). live-фейл -> отдаёт снимок.
   3) Не in_progress (скоро/завершён): отдаёт локальный data/games_{id}_current.json (заморожен).
   Прочее: normRole (роли), convertInertia (парсер), applyAccent (тема), injectRefresh
   (плавающая кнопка «Обновить», #__refbtn), авто-reload раз в 10 мин.
   winner стола берётся из официального поля results mafgame (red_win/black_win), НЕ из очков.
   НЕ ломать защиту снимка — это ключевая гарантия «ничего не терять».
   ============================================================================ */
// MafgameStat · data/live.js · v1.9 · 2026-07-18 · фикс дня 1 ЧЕ: пока в снимке одна стадия, она звалась «Игры» и ce634 группировал её как «Финал» — для 634 стадия 1 всегда «Квалификация» · v1.8 · 2026-07-16 · ЧЕ-634: стадии Квалификация/Полуфинал/Финал (3 стадии) + ЗАЩИТА «держим последний топ-снимок» (localStorage): не затираем хорошие данные пустыми/обнулёнными/пропавшими (snapScore/notRegression); live-фейл → отдаём сохранённый снимок. · v1.7 · 2026-07-04 · кнопка «Обновить» перенесена в левый нижний угол (не налезает на «Наверх»);  · 2026-06-25 · пропуск пустых слотов/столов/игр (финал до посева не плодит «null»-игрока, ломавшего карточки); winner стола берётся из g.results (стадия-игра-стол → black/red); фикс парных турниров, где у победителей game_points=0 → раньше winner оставался unknown и таблицы не считались. v1.4 · 2026-06-19 · LIVE для идущих турниров (tournament_{t}.json in_progress:true): подтяжка game_results с mafgame через прокси /mafgame/* при каждом открытии + авто-reload 10 мин + плавающая кнопка «Обновить». Завершённые/скоро — из локальных JSON (заморожены). Generic-парсер: стадия 2 = Финал.
window.normRole = function(r){
  if(r==null) return null;
  const map={'citizen':'Citizen','sheriff':'Sheriff','mafia':'Mafia','don':'Don',
             '1':'Citizen','2':'Sheriff','3':'Mafia','4':'Don','red':'Citizen','black':'Mafia'};
  return map[String(r).toLowerCase()]||null;
};
window.convertInertia = function(g, t){
  if(!g||!g.seats) return null;
  const stages={};
  for(const k in g.seats){
    const p=k.split('-').map(Number);
    if(p.length!==4) continue;
    const [st,gm,tb,seat]=p, s=g.seats[k];
    if(!s.original_nickname) continue; // пропускаем незаполненные слоты (напр. финал до посева)
    const role=normRole(s.role);
    const bonus=(s.game_bonus||0)+(s.best_move_bonus||0);
    const minus=s.penalty||0;
    const ci=s.Ci||0;
    const wpts=s.game_points||0;
    (((stages[st]=stages[st]||{})[gm]=stages[st][gm]||{})[tb]=stages[st][gm][tb]||[])[seat-1]={
      seat,name:s.original_nickname,role,
      marker:s.killed_first?'first_killed':(bonus-minus>0?'beige':null),
      aps:+(bonus-minus).toFixed(4),wpts,ci:+ci.toFixed(4),
      sigma:+(wpts+bonus-minus+ci).toFixed(4),result:null};
  }
  const stKeys=Object.keys(stages).map(Number).sort((a,b)=>a-b);
  const multi=stKeys.length>1;
  const maxStage=stKeys[stKeys.length-1];
  const three=String(t)==='634'; // v1.9: ЧЕ — всегда 3 стадии, даже пока заполнена одна (иначе день 1 звался «Игры» → группировка кидала в «Финал»)
  const stageName=(st)=>{
    if(st===1) return (multi||three)?'Квалификация':'Игры';
    if(three||maxStage>=3) return st===2?'Полуфинал':(st===3?'Финал':'Стадия '+st); // 3 стадии: квал/полуфинал/финал (ЧЕ)
    return 'Финал'; // 2 стадии: квал/финал (766/702/667)
  };
  const out=[];
  stKeys.forEach(st=>{
    const label = stageName(st);
    Object.keys(stages[st]).map(Number).sort((a,b)=>a-b).forEach(gm=>{
      const tables=[];
      Object.keys(stages[st][gm]).map(Number).sort((a,b)=>a-b).forEach(tb=>{
        const seats=stages[st][gm][tb].filter(Boolean);
        if(!seats.length) return; // пустой стол не показываем
        const hasRoles=seats.length>=6&&seats.every(x=>x.role);
        let winner='unknown';
        const _rv=g.results&&g.results[st+'-'+gm+'-'+tb];
        if(_rv==='black'||_rv==='red'){ winner=_rv==='black'?'black_win':'red_win'; }
        else if(hasRoles){
          const blackW=seats.some(x=>(x.role==='Mafia'||x.role==='Don')&&x.wpts>0);
          const redW=seats.some(x=>(x.role==='Citizen'||x.role==='Sheriff')&&x.wpts>0);
          winner=blackW?'black_win':(redW?'red_win':'unknown');
        }
        if(winner!=='unknown'&&hasRoles) seats.forEach(x=>{const black=(x.role==='Mafia'||x.role==='Don');x.result=((winner==='black_win')===black)?'W':'L';});
        tables.push({table_num:tb,winner,seats});
      });
      if(tables.length) out.push({title:(st===1?'Game ':stageName(st)+' ')+gm,stage:label,tables}); // игру без столов пропускаем
    });
  });
  if(!out.length) return null;
  const played=out.filter(x=>x.tables.length&&x.tables.every(t=>t.winner!=='unknown')).length;
  return {tournament_id:+t,games_played:played,games_total:out.length,games:out,live:true};
};
function injectRefresh(){
  if(document.getElementById('__refbtn')) return;
  const add=()=>{
    if(document.getElementById('__refbtn')||!document.body) return;
    const b=document.createElement('button');
    b.id='__refbtn'; b.textContent='⟳ Обновить';
    b.title='Подтянуть свежие результаты с mafgame';
    b.style.cssText='position:fixed;left:16px;bottom:16px;z-index:9999;padding:11px 16px;border-radius:24px;border:1px solid #ffb84d;background:#1a1d2e;color:#ffb84d;font-weight:800;font-size:13px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.5);';
    b.onclick=()=>{b.textContent='Обновляю…';location.reload();};
    document.body.appendChild(b);
  };
  if(document.body) add(); else document.addEventListener('DOMContentLoaded',add);
}
window.applyAccent = async function(t){ try{const r=await fetch('data/tournament_'+t+'.json',{cache:'no-store'});if(r.ok){const j=await r.json();if(j&&j.accent)document.documentElement.style.setProperty('--accent',j.accent);}}catch(e){} };
// «Качество» снимка: чем больше доигранных игр и суммарной статистики — тем ценнее.
// Нужно, чтобы НЕ затирать хорошие данные пустыми/обнулёнными (правило: держим последний топ-снимок).
window.snapScore = function(conv){
  if(!conv||!conv.games) return {played:0,sum:0,games:0};
  let sum=0, seats=0;
  conv.games.forEach(g=>g.tables.forEach(tb=>tb.seats.forEach(s=>{ sum+=Math.abs(s.sigma||0)+Math.abs(s.wpts||0); if(s.role) seats++; })));
  return {played:conv.games_played||0, sum:+sum.toFixed(3), games:conv.games.length, seats};
};
// не регресс, если новый снимок не хуже сохранённого (не меньше доигранных игр и не «схлопнулась» статистика)
window.notRegression = function(fresh, saved){
  if(!saved) return true;
  const a=snapScore(fresh), b=snapScore(saved);
  if(a.played < b.played) return false;               // стало меньше доигранных игр → таблицу закрыли/подрезали
  if(b.sum>0 && a.sum < b.sum*0.5) return false;       // была статистика, а стала почти нулевая → обнуление допов
  if(a.games < b.games) return false;                  // пропали игры целиком
  return true;
};
window.loadGames = async function(t){
  let inprog=false;
  try{const tr=await fetch('data/tournament_'+t+'.json',{cache:'no-store'});if(tr.ok){const tj=await tr.json();inprog=!!tj.in_progress;}}catch(e){}
  const LSK='mgs_lastgood_'+t;
  let saved=null;
  try{ const raw=localStorage.getItem(LSK); if(raw) saved=JSON.parse(raw); }catch(e){}
  if(inprog){
    try{
      const r=await fetch('/mafgame/tournaments/'+t+'/game_results',{cache:'no-store'});
      if(r.ok){
        const html=await r.text();
        const m=html.match(/data-page="([^"]+)"/);
        if(m){
          const dp=JSON.parse(m[1].replace(/&quot;/g,'"').replace(/&amp;/g,'&').replace(/&#039;/g,"'"));
          const conv=convertInertia(dp.props&&dp.props.games, t);
          if(conv){
            injectRefresh(); if(!window._autoref){window._autoref=1;setTimeout(()=>location.reload(),600000);}
            // защита: принимаем свежий снимок только если он НЕ регресс относительно последнего хорошего
            if(notRegression(conv, saved)){
              try{ localStorage.setItem(LSK, JSON.stringify(conv)); }catch(e){}
              return conv;
            } else {
              console.warn('live '+t+': свежий снимок хуже сохранённого (таблицу закрыли/обнулили) — держим последние топ-данные');
              if(saved) return saved;
              return conv; // сохранённого нет — отдаём что есть
            }
          }
        }
      }
      // live не отдал данных — падаем на последний хороший снимок, если он есть
      if(saved) { injectRefresh(); return saved; }
    }catch(e){ console.warn('live '+t+' недоступен, беру сохранённый/локальный',e); if(saved){ injectRefresh(); return saved; } }
  }
  try{
    const r2=await fetch('data/games_'+t+'_current.json'+(inprog?'?cb='+Date.now():''),{cache:inprog?'no-store':'default'});
    if(r2.ok){
      const local=await r2.json();
      // если сохранённый снимок «богаче» замороженного локального — предпочитаем его
      if(saved && snapScore(saved).played > snapScore(local).played) return saved;
      return local;
    }
  }catch(e){console.warn('нет локального файла игр для '+t,e);}
  return saved||null;
};
