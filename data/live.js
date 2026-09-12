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
// MafgameStat · data/live.js · v2.2 · 2026-09-10 · окно live по датам: tournament_{id}.json live_from/live_to (Прага) включают подтяжку с mafgame автоматически в дни турнира (ЧМ-710: 12–13.09), без ручного in_progress; window.__forceLocal — отладочный выключатель · v2.1 · 2026-08-23 · коэффициент финала (tournament_{id}.json final_coef, напр. 1.3): в протоколах mafgame сырые баллы, в офиц. таблицу баллы финальных игр входят с коэффициентом — live-таблица финала занижала Σ (урок 694; уточнение урока 702: коэффициент действует на ВСЕ баллы финала — WPTS/допы/штрафы/ЛХ/Ci) · v2.0 · 2026-08-22 · CEC-694 (финал серийника, Прага): стадия 1 всегда «Квалификация», стадия 2 — «Финал»; стадии 3+ (пустые заглушки 15 серий в данных mafgame) игнорируются · v1.9 · 2026-07-18 · фикс дня 1 ЧЕ: пока в снимке одна стадия, она звалась «Игры» и ce634 группировал её как «Финал» — для 634 стадия 1 всегда «Квалификация» · v1.8 · 2026-07-16 · ЧЕ-634: стадии Квалификация/Полуфинал/Финал (3 стадии) + ЗАЩИТА «держим последний топ-снимок» (localStorage): не затираем хорошие данные пустыми/обнулёнными/пропавшими (snapScore/notRegression); live-фейл → отдаём сохранённый снимок. · v1.7 · 2026-07-04 · кнопка «Обновить» перенесена в левый нижний угол (не налезает на «Наверх»);  · 2026-06-25 · пропуск пустых слотов/столов/игр (финал до посева не плодит «null»-игрока, ломавшего карточки); winner стола берётся из g.results (стадия-игра-стол → black/red); фикс парных турниров, где у победителей game_points=0 → раньше winner оставался unknown и таблицы не считались. v1.4 · 2026-06-19 · LIVE для идущих турниров (tournament_{t}.json in_progress:true): подтяжка game_results с mafgame через прокси /mafgame/* при каждом открытии + авто-reload 10 мин + плавающая кнопка «Обновить». Завершённые/скоро — из локальных JSON (заморожены). Generic-парсер: стадия 2 = Финал.
window.normRole = function(r){
  if(r==null) return null;
  const map={'citizen':'Citizen','sheriff':'Sheriff','mafia':'Mafia','don':'Don',
             '1':'Citizen','2':'Sheriff','3':'Mafia','4':'Don','red':'Citizen','black':'Mafia'};
  return map[String(r).toLowerCase()]||null;
};
window.convertInertia = function(g, t, fc){
  if(!g||!g.seats) return null;
  /* v2.4 (12.09.2026): балл за победу.
     Официальная сетка mafgame даёт за победу 0.75 — проверено на 634/694/702/766:
     в seats.game_points ровно два значения, 0 и 0.75, и сумма по игроку совпадает
     с официальной таблицей (total_score = 0.75×победы + допы + ЛХ − штрафы + Ci,
     финальные игры ×final_coef; сверено на дне 3 ЧЕ-634 — 10 строк из 10 до цента).
     НО платформа проставляет game_points только при пересчёте результатов: на идущем ЧМ
     у всех 550 мест ноль, хотя победители столов уже известны. Поэтому: если победа стола
     известна, а баллы за победу на столе не проставлены — начисляем 0.75 сами.
     Как только mafgame проставит свои — берём их (условие «все нули» перестанет выполняться). */
  const WIN_PTS = 0.75;
  /* v2.5 (12.09.2026): бонус первому убитому за запись чёрных — 0.25 за двоих, 0.4 за троих.
     `best_move` = сколько чёрных записал игрок, убитый первой ночью; проверено на ЧЕ-634:
     пересчитанный бонус совпал с `best_move_bonus` платформы у всех 44 игроков.
     Платформа, как и баллы за победу, проставляет его только при пересчёте турнира,
     поэтому на живом турнире считаем сами — по тому же условию «стол ещё не посчитан». */
  const BM_BONUS = m => (m >= 3 ? 0.4 : (m === 2 ? 0.25 : 0));
  let winSelf = false;
  fc=+fc||1; // коэффициент финала: офиц. таблица mafgame умножает баллы финальных игр (напр. x1.3)
  const stages={};
  for(const k in g.seats){
    const p=k.split('-').map(Number);
    if(p.length!==4) continue;
    const [st,gm,tb,seat]=p, s=g.seats[k];
    if(!s.original_nickname) continue; // пропускаем незаполненные слоты (напр. финал до посева)
    if(String(t)==='694'&&st>2) continue; // 694: стадии 3-17 — заглушки серий, в финале их быть не должно
    const role=normRole(s.role);
    const bonus=(s.game_bonus||0)+(s.best_move_bonus||0);
    const minus=s.penalty||0;
    const ci=s.Ci||0;
    const wpts=s.game_points||0;
    (((stages[st]=stages[st]||{})[gm]=stages[st][gm]||{})[tb]=stages[st][gm][tb]||[])[seat-1]={
      seat,name:s.original_nickname,role,
      marker:s.killed_first?'first_killed':(bonus-minus>0?'beige':null),
      aps:+(bonus-minus).toFixed(4),wpts,ci:+ci.toFixed(4),kf:+s.killed_first||0,bm:+s.best_move||0,bmb:+s.best_move_bonus||0,
      sigma:+(wpts+bonus-minus+ci).toFixed(4),result:null};
  }
  const stKeys=Object.keys(stages).map(Number).sort((a,b)=>a-b);
  const multi=stKeys.length>1;
  const maxStage=stKeys[stKeys.length-1];
  const three=String(t)==='634'; // v1.9: ЧЕ — всегда 3 стадии, даже пока заполнена одна (иначе день 1 звался «Игры» → группировка кидала в «Финал»)
  const two=String(t)==='694';   // v2.0: CEC-694 — всегда 2 стадии (1=Квалификация, 2=Финал), даже пока заполнена одна
  const wc=String(t)==='710';    // v2.3 (12.09.2026): ЧМ-2026 — всегда 3 стадии. Пока заполнена только первая, стадия 1 звалась «Игры»,
                                 // и всё, что фильтрует по 'Квалификация' (сила столов, рассадка, плашки, судьи), схлопывалось в ноль.
  const stageName=(st)=>{
    if(st===1) return (multi||three||two||wc)?'Квалификация':'Игры';
    if(two) return st===2?'Финал':'Стадия '+st;
    if(three||wc||maxStage>=3) return st===2?'Полуфинал':(st===3?'Финал':'Стадия '+st); // 3 стадии: квал/полуфинал/финал (ЧЕ)
    return 'Финал'; // 2 стадии: квал/финал (766/702/667)
  };
  const out=[];
  stKeys.forEach(st=>{
    const label = stageName(st);
    const k=(label==='Финал'&&fc!==1)?fc:1; // финал — с офиц. коэффициентом
    Object.keys(stages[st]).map(Number).sort((a,b)=>a-b).forEach(gm=>{
      const tables=[];
      Object.keys(stages[st][gm]).map(Number).sort((a,b)=>a-b).forEach(tb=>{
        const seats=stages[st][gm][tb].filter(Boolean).map(x=>k===1?x:{...x,aps:+(x.aps*k).toFixed(4),wpts:+(x.wpts*k).toFixed(4),ci:+(x.ci*k).toFixed(4),sigma:+(x.sigma*k).toFixed(4)});
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
        let selfTable = false; // этот стол платформа ещё не считала — баллы за победу и бонус записи ставим сами
        if(winner!=='unknown'&&hasRoles){
          seats.forEach(x=>{const black=(x.role==='Mafia'||x.role==='Don');x.result=((winner==='black_win')===black)?'W':'L';});
          if(seats.every(x=>!x.wpts)){
            selfTable = true; winSelf = true;
            seats.forEach(x=>{ if(x.result==='W'){ x.wpts=+(WIN_PTS*k).toFixed(4); } });
          }
        }
        if(selfTable&&seats.every(x=>!x.bmb)){ // платформа ещё не считала стол — начисляем бонус за запись сами
          seats.forEach(x=>{ if(x.kf){ const b=BM_BONUS(x.bm); if(b){ x.bmb=+(b*k).toFixed(4); x.aps=+(x.aps+x.bmb).toFixed(4); } } });
        }
        seats.forEach(x=>{ x.sigma=+(x.wpts+x.aps+x.ci).toFixed(4); });
        tables.push({table_num:tb,winner,seats,comment:(g.game_comments&&g.game_comments[st+'-'+gm+'-'+tb])||null});
      });
      if(tables.length) out.push({title:(st===1?'Game ':stageName(st)+' ')+gm,stage:label,tables}); // игру без столов пропускаем
    });
  });
  if(!out.length) return null;
  const played=out.filter(x=>x.tables.length&&x.tables.every(t=>t.winner!=='unknown')).length;
  if(winSelf) window.__winSelf = true;
  return {tournament_id:+t,games_played:played,games_total:out.length,games:out,live:true,win_self:winSelf};
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
  let inprog=false, fcoef=1;
  try{const tr=await fetch('data/tournament_'+t+'.json',{cache:'no-store'});if(tr.ok){const tj=await tr.json();inprog=!!tj.in_progress;fcoef=+tj.final_coef||1;
    /* v2.2: окно live по датам (live_from/live_to, Прага) — включается само в дни турнира, не держим in_progress заранее */
    if(!inprog&&tj.live_from&&!tj.closed){const now=Date.now(),a=new Date(tj.live_from+'T00:00:00+02:00').getTime(),b=new Date((tj.live_to||tj.live_from)+'T23:59:59+02:00').getTime();if(now>=a&&now<=b)inprog=true;}
    if(inprog&&window.__forceLocal)inprog=false;}}catch(e){}
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
          const conv=convertInertia(dp.props&&dp.props.games, t, fcoef);
          if(conv){
            injectRefresh(); if(!window._autoref){window._autoref=1;setTimeout(()=>location.reload(),120000);/* v2.3: было 10 мин — на ЧМ игроки ждали результат слишком долго */}
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
