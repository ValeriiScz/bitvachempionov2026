// MafgameStat · data/live.js · v1.3 · 2026-06-19 · турнир 667 закрыт и заморожен в JSON (data/games_667_current.json, 16 игр: 12 квалификации + 4 финала). Live-подтяжка с mafgame отключена. convertInertia667 оставлен как утилита (стадия 1 = Квалификация, стадия 2 = Финал) на случай будущих live-турниров.
window.normRole = function(r){
  if(r==null) return null;
  const map={'citizen':'Citizen','sheriff':'Sheriff','mafia':'Mafia','don':'Don',
             '1':'Citizen','2':'Sheriff','3':'Mafia','4':'Don','red':'Citizen','black':'Mafia'};
  return map[String(r).toLowerCase()]||null;
};
// Утилита: конвертация Inertia-протокола mafgame в формат games. Стадия 1 -> Квалификация, стадия 2 -> Финал (отдельной стадией).
window.convertInertia667 = function(g){
  if(!g||!g.seats) return null;
  const stages={}; // stage -> game -> table -> seats
  for(const k in g.seats){
    const p=k.split('-').map(Number);
    if(p.length!==4) continue;
    const [st,gm,tb,seat]=p, s=g.seats[k];
    if(st!==1&&st!==2) continue;
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
  const out=[];
  Object.keys(stages).map(Number).sort((a,b)=>a-b).forEach(st=>{
    const label=st===1?'Квалификация':'Финал';
    Object.keys(stages[st]).map(Number).sort((a,b)=>a-b).forEach(gm=>{
      const tables=[];
      Object.keys(stages[st][gm]).map(Number).sort((a,b)=>a-b).forEach(tb=>{
        const seats=stages[st][gm][tb].filter(Boolean);
        const hasRoles=seats.length===10&&seats.every(x=>x.role);
        let winner='unknown';
        if(hasRoles){
          const blackW=seats.some(x=>(x.role==='Mafia'||x.role==='Don')&&x.wpts>0);
          const redW=seats.some(x=>(x.role==='Citizen'||x.role==='Sheriff')&&x.wpts>0);
          winner=blackW?'black_win':(redW?'red_win':'unknown');
          if(winner!=='unknown') seats.forEach(x=>{
            const black=(x.role==='Mafia'||x.role==='Don');
            x.result=((winner==='black_win')===black)?'W':'L';
          });
        }
        tables.push({table_num:tb,winner,seats});
      });
      out.push({title:(st===1?'Game ':'Финал ')+gm,stage:label,tables});
    });
  });
  if(!out.length) return null;
  const playedCnt=out.filter(x=>x.tables.length&&x.tables.every(t=>t.winner!=='unknown')).length;
  return {tournament_id:667,tournament_name:'Four Seasons. Cyprus Open: Summer',
          games_played:playedCnt,games_total:out.length,games:out,live:true};
};
// Загрузка игр: все турниры читаются из локальных замороженных JSON (без live-зависимости от mafgame).
window.loadGames = async function(t){
  try{
    const r=await fetch('data/games_'+t+'_current.json',{cache:'no-store'});
    if(r.ok) return await r.json();
  }catch(e){console.warn('Нет локального файла игр для турнира '+t,e);}
  return null;
};
