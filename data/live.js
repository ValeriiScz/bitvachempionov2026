// MafgameStat · data/live.js · v1.4 · 2026-06-19 · LIVE для идущих турниров (tournament_{t}.json in_progress:true): подтяжка game_results с mafgame через прокси /mafgame/* при каждом открытии + авто-reload 10 мин + плавающая кнопка «Обновить». Завершённые/скоро — из локальных JSON (заморожены). Generic-парсер: стадия 2 = Финал.
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
  const out=[];
  stKeys.forEach(st=>{
    const label = st===2 ? 'Финал' : (multi ? 'Квалификация' : 'Игры');
    Object.keys(stages[st]).map(Number).sort((a,b)=>a-b).forEach(gm=>{
      const tables=[];
      Object.keys(stages[st][gm]).map(Number).sort((a,b)=>a-b).forEach(tb=>{
        const seats=stages[st][gm][tb].filter(Boolean);
        const hasRoles=seats.length>=6&&seats.every(x=>x.role);
        let winner='unknown';
        if(hasRoles){
          const blackW=seats.some(x=>(x.role==='Mafia'||x.role==='Don')&&x.wpts>0);
          const redW=seats.some(x=>(x.role==='Citizen'||x.role==='Sheriff')&&x.wpts>0);
          winner=blackW?'black_win':(redW?'red_win':'unknown');
          if(winner!=='unknown') seats.forEach(x=>{const black=(x.role==='Mafia'||x.role==='Don');x.result=((winner==='black_win')===black)?'W':'L';});
        }
        tables.push({table_num:tb,winner,seats});
      });
      out.push({title:(st===2?'Финал ':'Game ')+gm,stage:label,tables});
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
    b.style.cssText='position:fixed;right:16px;bottom:16px;z-index:9999;padding:11px 16px;border-radius:24px;border:1px solid #ffb84d;background:#1a1d2e;color:#ffb84d;font-weight:800;font-size:13px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.5);';
    b.onclick=()=>{b.textContent='Обновляю…';location.reload();};
    document.body.appendChild(b);
  };
  if(document.body) add(); else document.addEventListener('DOMContentLoaded',add);
}
window.applyAccent = async function(t){ try{const r=await fetch('data/tournament_'+t+'.json',{cache:'no-store'});if(r.ok){const j=await r.json();if(j&&j.accent)document.documentElement.style.setProperty('--accent',j.accent);}}catch(e){} };
window.loadGames = async function(t){
  let inprog=false;
  try{const tr=await fetch('data/tournament_'+t+'.json',{cache:'no-store'});if(tr.ok){const tj=await tr.json();inprog=!!tj.in_progress;}}catch(e){}
  if(inprog){
    try{
      const r=await fetch('/mafgame/tournaments/'+t+'/game_results',{cache:'no-store'});
      if(r.ok){
        const html=await r.text();
        const m=html.match(/data-page="([^"]+)"/);
        if(m){
          const dp=JSON.parse(m[1].replace(/&quot;/g,'"').replace(/&amp;/g,'&').replace(/&#039;/g,"'"));
          const conv=convertInertia(dp.props&&dp.props.games, t);
          if(conv){ injectRefresh(); if(!window._autoref){window._autoref=1;setTimeout(()=>location.reload(),600000);} return conv; }
        }
      }
    }catch(e){console.warn('live '+t+' недоступен, беру локальный файл',e);}
  }
  try{
    const r2=await fetch('data/games_'+t+'_current.json'+(inprog?'?cb='+Date.now():''),{cache:inprog?'no-store':'default'});
    if(r2.ok) return await r2.json();
  }catch(e){console.warn('нет локального файла игр для '+t,e);}
  return null;
};
