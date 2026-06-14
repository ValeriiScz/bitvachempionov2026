// MafgameStat · data/live.js · v1.2 · 2026-06-14 · live-загрузка результатов с mafgame через Netlify-прокси /mafgame/*
// Замены игроков поддерживаются автоматически: берём фактический original_nickname из протокола игры.
window.normRole = function(r){
  if(r==null) return null;
  const map={'citizen':'Citizen','sheriff':'Sheriff','mafia':'Mafia','don':'Don',
             '1':'Citizen','2':'Sheriff','3':'Mafia','4':'Don','red':'Citizen','black':'Mafia'};
  return map[String(r).toLowerCase()]||null;
};
window.convertInertia667 = function(g){
  if(!g||!g.seats) return null;
  const games={};
  for(const k in g.seats){
    const p=k.split('-').map(Number);
    if(p.length!==4||p[0]!==1) continue; // 1 = квалификация; финал добавим отдельной стадией
    const [,gm,tb,seat]=p, s=g.seats[k];
    const role=normRole(s.role);
    const bonus=(s.game_bonus||0)+(s.best_move_bonus||0);
    const minus=s.penalty||0;
    const ci=s.Ci||0;            // компенсация (Ci) — есть в протоколе, входит в офиц. Σ
    const wpts=s.game_points||0;
    ((games[gm]=games[gm]||{})[tb]=games[gm][tb]||[])[seat-1]={
      seat,name:s.original_nickname,role,
      marker:s.killed_first?'first_killed':(bonus>0?'beige':null),
      aps:+(bonus-minus).toFixed(4),wpts,ci:+ci.toFixed(4),
      sigma:+(wpts+bonus-minus+ci).toFixed(4),result:null};
  }
  const out=[];
  Object.keys(games).map(Number).sort((a,b)=>a-b).forEach(gm=>{
    const tables=[];
    Object.keys(games[gm]).map(Number).sort((a,b)=>a-b).forEach(tb=>{
      const seats=games[gm][tb].filter(Boolean);
      const hasRoles=seats.length===10&&seats.every(x=>x.role);
      const officialWinner=g.results&&g.results['1-'+gm+'-'+tb];
      let winner=officialWinner==='black'?'black_win':(officialWinner==='red'?'red_win':'unknown');
      if(hasRoles){
        if(winner==='unknown'){
          const blackW=seats.some(x=>(x.role==='Mafia'||x.role==='Don')&&x.wpts>0);
          const redW=seats.some(x=>(x.role==='Citizen'||x.role==='Sheriff')&&x.wpts>0);
          winner=blackW?'black_win':(redW?'red_win':'unknown');
        }
        if(winner!=='unknown') seats.forEach(x=>{
          const black=(x.role==='Mafia'||x.role==='Don');
          x.result=((winner==='black_win')===black)?'W':'L';
          if(x.result==='W'&&!x.wpts) x.wpts=0.75;
          x.sigma=+(x.wpts+x.aps+x.ci).toFixed(4);
        });
      }
      tables.push({table_num:tb,winner,seats});
    });
    out.push({title:'Game '+gm,stage:'Квалификация',tables});
  });
  const playedCnt=out.filter(x=>x.tables.length&&x.tables.some(t=>t.winner!=='unknown')).length;
  if(!out.length) return null;
  return {tournament_id:667,tournament_name:'Four Seasons. Cyprus Open: Summer',
          games_played:playedCnt,games_total:out.length,games:out,live:true};
};
window.loadGames = async function(t){
  if(String(t)==='667'){
    try{
      const r=await fetch('/mafgame/tournaments/667/game_results',{cache:'no-store'});
      if(r.ok){
        const html=await r.text();
        const m=html.match(/data-page="([^"]+)"/);
        if(m){
          const dp=JSON.parse(m[1].replace(/&quot;/g,'"').replace(/&amp;/g,'&').replace(/&#039;/g,"'"));
          const conv=convertInertia667(dp.props&&dp.props.games);
          if(conv){
            // автообновление live-страницы каждые 10 минут
            if(!window._autoref){window._autoref=1;setTimeout(()=>location.reload(),600000);}
            return conv;
          }
        }
      }
    }catch(e){console.warn('live 667 недоступен, беру локальный файл',e);}
  }
  try{
    const r2=await fetch('data/games_'+t+'_current.json');
    if(r2.ok) return await r2.json();
  }catch(e){}
  return null;
};
