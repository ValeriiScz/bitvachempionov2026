/* DOVOD · assets/watch-my.js · v1.1 · 2026-11-14 (без дубля: старая панель «Следить за игроком» спрятана — её функции здесь: главный игрок, «эфир за главным в каждой новой игре») · v1.0 · 2026-11-14
   «★ Мои игроки» в смотровых (watch*.html): следить сразу за несколькими игроками (до 8) — как «Для зрителей» на ЧМ-2026.
   · сводка по каждому: место и Σ (▲▼ за последнюю сыгранную игру), сейчас — стол и место (кнопка «▶»), дальше — следующая игра,
     путь «игра:стол» на весь турнир, в сыгранных — роль и победа/поражение (роль в будущей игре заранее неизвестна никому);
   · «В этой игре»: выбранные игроки по столам, «играют вместе», если двое за одним столом;
   · подсветка ★ в плитках «За столом», в таблице (кто ниже топ-12 — строкой под таблицей) и на кнопках столов;
   · телефон: блок свёрнут в одну строку («★ Мои игроки · YeS — стол II …»), разворачивается по тапу, состояние помнится;
     компьютер: в правой колонке под «За столом».
   Работает поверх страницы: глобальные S, D, CFG, RL, tableOf; список хранится в localStorage dvw_fav_{id}.
   Главный (за кем переключается эфир) — существующее «Следить за игроком» (#fsel); «★ главный» назначает его. */
(function(){
  if(window.__dvMy)return;window.__dvMy=1;
  function g(n){try{return eval(n);}catch(e){return undefined;}}
  function $(s,r){return (r||document).querySelector(s);} function $$(s,r){return [].slice.call((r||document).querySelectorAll(s));}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var ROM=['','I','II','III','IV','V','VI'],MAX=8;
  var PH=window.matchMedia('(max-width:820px)');
  var CF=g('CFG')||{};var KEY='dvw_fav_'+(CF.id||location.pathname);
  var FAV=[];try{FAV=JSON.parse(localStorage.getItem(KEY)||'[]')||[];}catch(e){}
  var OPEN=false;try{OPEN=localStorage.getItem('dvw_my_open')==='1';}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(FAV));}catch(e){}}
  var css=document.createElement('style');css.textContent=
  '#followP{position:absolute!important;left:-9999px!important;width:1px!important;height:1px!important;overflow:hidden!important}'+
  '.dvm-auto{display:flex;align-items:center;gap:8px;margin:8px 0 2px;font:600 12.5px/1.3 Inter;color:#cfd5df;cursor:pointer}.dvm-auto input{width:18px;height:18px;accent-color:#f5ff35}'+
  '.dvm{margin:0 0 12px}.dvm .panel{margin:0}'+
  '.dvm-h{display:flex;align-items:center;gap:8px;cursor:default}.dvm-h h3{margin:0!important;flex:1;display:flex;align-items:center;gap:8px}'+
  '.dvm-h .cnt{font:800 11px/1 "JetBrains Mono",monospace;color:#9aa3b2}.dvm-tg{display:none;min-width:40px;min-height:36px;border-radius:9px;border:1px solid rgba(255,255,255,.16);background:none;color:#cfd5df;font:800 14px/1 Inter;cursor:pointer}'+
  '.dvm-q{position:relative;margin:10px 0 4px}.dvm-q input{width:100%;box-sizing:border-box;min-height:42px;padding:0 12px;border-radius:10px;border:1px solid rgba(255,255,255,.16);background:#0b0d14;color:#eef3fb;font:600 14px Inter,system-ui,sans-serif;outline:0}'+
  '.dvm-q input:focus{border-color:#f5ff35}.dvm-ql{position:absolute;left:0;right:0;top:calc(100% + 4px);z-index:70;max-height:300px;overflow:auto;background:#0f1320;border:1px solid rgba(255,255,255,.14);border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.6);padding:4px}'+
  '.dvm-ql button{display:flex;align-items:center;gap:10px;width:100%;min-height:42px;padding:4px 10px;border:0;border-radius:8px;background:none;color:#eef3fb;font:600 14px Inter,sans-serif;text-align:left;cursor:pointer}.dvm-ql button:hover{background:rgba(245,255,53,.1)}'+
  '.dvm-ql img{width:26px;height:26px;border-radius:50%;object-fit:cover}.dvm-ql small{margin-left:auto;color:#9aa3b2;font-size:12px}'+
  '.dvm-now{display:flex;flex-direction:column;gap:6px;margin:10px 0 6px}.dvm-nt{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);font:600 13px/1.3 Inter}'+
  '.dvm-nt b{font:800 12px/1 "JetBrains Mono",monospace;color:#f5ff35;min-width:58px}.dvm-nt .tg2{font:800 10.5px/1 Inter;color:#05060a;background:#f5ff35;border-radius:999px;padding:3px 7px}'+
  '.dvm-nt button,.dvm-r .go{margin-left:auto;min-height:34px;padding:0 12px;border-radius:9px;border:1px solid rgba(245,255,53,.6);background:none;color:#f5ff35;font:800 12px Inter;cursor:pointer}'+
  '.dvm-r{padding:10px 0;border-top:1px solid rgba(255,255,255,.07)}.dvm-r:first-of-type{border-top:0}'+
  '.dvm-r .dvm-tp{display:flex;align-items:center;gap:10px}.dvm-r img.av{width:36px;height:36px;border-radius:50%;object-fit:cover;flex:none;border:2px solid rgba(245,255,53,.6)}'+
  '.dvm-r .nm{flex:1;min-width:0}.dvm-r .nm b{font:800 14px/1.2 Inter;color:#eef3fb}.dvm-r .nm b.main::after{content:" · главный";font:700 10.5px Inter;color:#f5ff35}'+
  '.dvm-r .nm small{display:block;font:600 12px/1.35 Inter;color:#aab2c0}.dvm-r .dvm-pl{font:900 20px/1 Unbounded,Inter,sans-serif;color:#f5ff35;text-align:right}.dvm-r .dvm-pl small{display:block;font:700 10px/1.2 Inter;color:#9aa3b2}'+
  '.dvm-r .up{color:#7ce6a0}.dvm-r .dn{color:#ff8a86}'+
  '.dvm-r .acts{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}.dvm-r .acts button{min-height:32px;padding:0 10px;border-radius:8px;border:1px solid rgba(255,255,255,.14);background:none;color:#cfd5df;font:700 12px Inter;cursor:pointer}'+
  '.dvm-path{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}.dvm-path span{display:inline-flex;align-items:center;gap:3px;min-width:34px;justify-content:center;padding:4px 6px;border-radius:7px;border:1px solid rgba(255,255,255,.12);font:700 11px/1 "JetBrains Mono",monospace;color:#cfd5df}'+
  '.dvm-path span.cur{border-color:#f5ff35;color:#f5ff35;box-shadow:0 0 0 1px #f5ff35 inset}.dvm-path span.w{background:rgba(124,230,160,.12);border-color:rgba(124,230,160,.4)}.dvm-path span.l{background:rgba(255,138,134,.08);border-color:rgba(255,138,134,.3)}'+
  '.dvm-path span.fut{opacity:.55}.dvm-path i{font-style:normal;font-size:9.5px;opacity:.85}.dvm-path span.blk i{color:#ff8a86}.dvm-path span.red i{color:#9fd3ff}'+
  '.dvm-opp{margin-top:6px;font:600 12px/1.35 Inter;color:#aab2c0}'+
  '.dvm-mini{display:none;gap:6px;flex-wrap:wrap;margin-top:8px}.dvm-mini span{display:inline-flex;align-items:center;gap:5px;padding:5px 9px;border-radius:999px;background:rgba(245,255,53,.08);border:1px solid rgba(245,255,53,.3);font:700 12px/1 Inter;color:#eef3fb}.dvm-mini span b{color:#f5ff35}'+
  '.dvm-empty{font:500 12.5px/1.45 Inter;color:#9aa3b2;margin-top:6px}'+
  /* подсветка */
  '#seatP .st.dvw-fav{box-shadow:0 0 0 2px #f5ff35 inset;border-radius:10px}#seatP .st.dvw-fav .nk::before{content:"★ ";color:#f5ff35}'+
  '#topP tr.dvw-favr td{color:#f5ff35;background:rgba(245,255,53,.06)}#topP tr.dvw-favr td:nth-child(2)::before{content:"★ "}'+
  '#tabs button .dvm-b{display:inline-flex;align-items:center;justify-content:center;margin-left:6px;min-width:18px;height:18px;padding:0 5px;border-radius:999px;background:#f5ff35;color:#05060a;font:800 10.5px/1 Inter}'+
  /* телефон: свёрнуто — одна строка с чипами */
  '.dvm-r .acts .pth{display:none}'+
  '@media(max-width:820px){.dvm{margin:8px 14px}.dvm-tg{display:inline-flex;align-items:center;justify-content:center}.dvm.closed .dvm-body{display:none}.dvm.closed .dvm-mini{display:flex}.dvm-opp{display:none}.dvm-r:not(.open) .dvm-path{display:none}.dvm-path span{min-width:30px;padding:4px 5px}.dvm-r .acts .pth{display:inline-flex}.dvm-r .acts .mn{display:none}}';
  document.head.appendChild(css);

  function avatarSrc(n){var D=g('D')||{};var p=(D.P||{})[n];return (D.av&&D.av[n])||(p&&p.av)||'';}
  function names(){var D=g('D')||{};return (D.players||[]).map(function(p){return p.nick;}).filter(Boolean);}
  function tierOf(n){var D=g('D')||{};var p=(D.P||{})[n];return p&&p.r_ms_tier;}
  function isFin(gm,games){return !!gm&&gm.stage==='Финал'&&games.some(function(x){return x.stage!=='Финал';});}
  function done(t){return t.winner&&t.winner!=='unknown';}
  function agg(games,upto){var A={};games.forEach(function(gm,gi){if(upto!=null&&gi>upto)return;gm.tables.forEach(function(t){if(!done(t))return;t.seats.forEach(function(x){if(!x||!x.name)return;var a=A[x.name]=A[x.name]||{n:x.name,s:0,g:0,w:0};a.s+=x.sigma||0;a.g++;if(x.result==='W')a.w++;});});});
    return Object.values(A).sort(function(a,b){return b.s-a.s;});}
  function where(games,gi,n){var gm=games[gi];if(!gm)return null;for(var i=0;i<gm.tables.length;i++){var t=gm.tables[i];for(var j=0;j<t.seats.length;j++){var x=t.seats[j];if(x&&x.name===n)return {t:t.table_num,seat:x.seat||j+1,x:x,tb:t};}}return null;}
  var RLS={Citizen:'мир',Sheriff:'шер',Mafia:'маф',Don:'дон'};
  function goTable(t){var b=$('#tabs button[data-t="'+t+'"]');var S=g('S');if(S&&S.mode!=='one'){var o=$('#modes [data-m="one"]');if(o)o.click();}if(b)b.click();window.scrollTo({top:0,behavior:'smooth'});}
  function setMain(n){var sel=$('#fsel');if(sel){sel.value=n;sel.dispatchEvent(new Event('change',{bubbles:true}));}}

  var box=null,sig='';
  function mount(){
    if(box&&document.body.contains(box))return box;
    box=document.createElement('div');box.className='dvm'+(PH.matches&&!OPEN?' closed':'');
    var seat=$('#seatP'),fp=$('#followP');
    if(PH.matches){var q=$('#qnav')||$('#modes');if(q&&q.parentNode)q.parentNode.insertBefore(box,q.nextSibling);else if(fp)fp.parentNode.insertBefore(box,fp);}
    else{if(seat&&seat.parentNode)seat.parentNode.insertBefore(box,seat.nextSibling);else if(fp)fp.parentNode.insertBefore(box,fp);}
    if(!box.parentNode)return null;
    box.addEventListener('click',function(e){var b=e.target.closest('[data-a]');if(!b)return;var a=b.dataset.a,n=b.dataset.n;
      if(a==='tg'){OPEN=box.classList.contains('closed');box.classList.toggle('closed',!OPEN);try{localStorage.setItem('dvw_my_open',OPEN?'1':'');}catch(e){}return;}
      if(a==='rm'){FAV=FAV.filter(function(x){return x!==n;});save();var S3=g('S');if(S3&&S3.follow===n){setMain(FAV[0]||'');}sig='';render();return;}
      if(a==='main'){setMain(n);sig='';setTimeout(render,50);return;}
      if(a==='go'){goTable(+b.dataset.t);return;}
      if(a==='auto'){var fa=$('#fauto');var S2=g('S');if(fa){fa.checked=b.checked;fa.dispatchEvent(new Event('change',{bubbles:true}));}else if(S2){S2.auto=b.checked;}sig='';return;}
      if(a==='pth'){var r=b.closest('.dvm-r');if(r)r.classList.toggle('open');return;}});
    return box;
  }
  function searchUI(){var wrap=$('.dvm-q',box);if(!wrap)return;var inp=$('input',wrap),list=$('.dvm-ql',wrap);if(inp.__ok)return;inp.__ok=1;
    function show(){var q=inp.value.trim().toLowerCase();var D=g('D')||{};var L=names().filter(function(n){return FAV.indexOf(n)<0&&(!q||n.toLowerCase().indexOf(q)>=0);}).slice(0,30);
      list.innerHTML=L.map(function(n){var w=where(D.games||[],D.cur,n);var a=avatarSrc(n);return '<button type="button" data-n="'+esc(n)+'">'+(a?'<img src="'+esc(a)+'" alt="" loading="lazy" onerror="this.remove()">':'')+esc(n)+'<small>'+(w?'стол '+ROM[w.t]:'')+'</small></button>';}).join('')||'<div class="dvm-empty" style="padding:8px">никого не нашли</div>';list.hidden=false;}
    inp.addEventListener('focus',show);inp.addEventListener('input',show);
    list.addEventListener('mousedown',function(e){var b=e.target.closest('button[data-n]');if(!b)return;e.preventDefault();var n=b.dataset.n;if(FAV.indexOf(n)<0){FAV.push(n);if(FAV.length>MAX)FAV.shift();save();}inp.value='';list.hidden=true;inp.blur();sig='';render();});
    document.addEventListener('click',function(e){if(!wrap.contains(e.target))list.hidden=true;});}
  function render(){
    var D=g('D'),S=g('S');if(!D||!D.games||!mount())return;
    var games=D.games,cur=D.cur||0;var rows=agg(games);
    var lastDone=-1;games.forEach(function(gm,gi){if(gm.tables.length&&gm.tables.every(done))lastDone=gi;});
    var prev=lastDone>=0?agg(games,lastDone-1):[];
    var s2=[FAV.join(','),cur,rows.map(function(r){return r.n+r.s.toFixed(2);}).join(','),S&&S.follow,S&&S.auto,box.className,games.map(function(gm){return gm.tables.map(function(t){return t.winner;}).join('');}).join('|')].join('#');
    if(s2===sig){mark();return;}sig=s2;
    var keep=$('.dvm-q input',box);var qv=keep?keep.value:'';
    var gm=games[cur];var fin=isFin(gm,games);
    /* в этой игре — по столам */
    var byT={};FAV.forEach(function(n){var w=where(games,cur,n);if(w)(byT[w.t]=byT[w.t]||[]).push(n+' <small style="color:#9aa3b2">м.'+w.seat+'</small>');});
    var nowH=Object.keys(byT).sort(function(a,b){return a-b;}).map(function(t){return '<div class="dvm-nt"><b>'+(fin?'Финал':'Стол '+ROM[t])+'</b>'+byT[t].join(', ')+(byT[t].length>1?'<span class="tg2">играют вместе</span>':'')+'<button type="button" data-a="go" data-t="'+t+'">▶</button></div>';}).join('');
    var gl=fin?'финал':'игра '+(games.slice(0,cur+1).filter(function(x){return !isFin(x,games);}).length);
    var rowsH=FAV.map(function(n){
      var i=rows.findIndex(function(r){return r.n===n;}),r=rows[i],pi=prev.findIndex(function(r){return r.n===n;});
      var d=(i>=0&&pi>=0)?pi-i:0;var w=where(games,cur,n);
      var nx=null;for(var k=cur+1;k<games.length;k++){var ww=where(games,k,n);if(ww){nx={gi:k,w:ww};break;}}
      var opp='';if(w){var strong=w.tb.seats.filter(function(x){return x&&x.name!==n&&/^[LSA]$/.test(tierOf(x.name)||'');}).map(function(x){return esc(x.name)+' ('+tierOf(x.name)+')';});opp=strong.length?'за столом сильные: '+strong.join(', '):'за столом без игроков уровня A и выше';}
      var path=games.map(function(gm2,gi){var ww=where(games,gi,n);if(!ww)return '';var c=gi===cur?'cur':done(ww.tb)?(ww.x.result==='W'?'w':'l'):'fut';var rl=ww.x.role&&RLS[ww.x.role];var side=(ww.x.role==='Mafia'||ww.x.role==='Don')?' blk':ww.x.role?' red':'';
        return '<span class="'+c+side+'" title="игра '+(gi+1)+' · стол '+ROM[ww.t]+' · место '+ww.seat+(rl?' · '+rl:'')+(c==='w'?' · победа':c==='l'?' · поражение':'')+'">'+(gi+1)+':'+(isFin(gm2,games)?'Ф':ROM[ww.t])+(rl?'<i>'+rl+'</i>':'')+'</span>';}).join('');
      var main=S&&S.follow===n;
      var sub=(w?'сейчас ('+gl+'): '+(fin?'финальный стол':'стол '+ROM[w.t])+', место '+w.seat:'в этой игре отдыхает')+(nx?' · дальше: игра '+(nx.gi+1)+', '+(isFin(games[nx.gi],games)?'финал':'стол '+ROM[nx.w.t])+', место '+nx.w.seat:'');
      var a=avatarSrc(n);
      return '<div class="dvm-r"><div class="dvm-tp">'+(a?'<img class="av" src="'+esc(a)+'" alt="" onerror="this.remove()">':'')+'<div class="nm"><b class="'+(main?'main':'')+'">'+esc(n)+'</b><small>'+sub+'</small></div>'+
        '<div class="dvm-pl">'+(r?(i+1):'—')+'<small>'+(r?'из '+rows.length+' · Σ '+r.s.toFixed(2)+(d?' <span class="'+(d>0?'up':'dn')+'">'+(d>0?'▲'+d:'▼'+(-d))+'</span>':''):'ещё не играл')+'</small></div></div>'+
        (opp?'<div class="dvm-opp">'+opp+'</div>':'')+'<div class="dvm-path">'+path+'</div>'+
        '<div class="acts">'+(w?'<button type="button" class="go" data-a="go" data-t="'+w.t+'" style="margin-left:0">▶ смотреть его стол</button>':'')+(main?'':'<button type="button" class="mn" data-a="main" data-n="'+esc(n)+'">★ главный (эфир за ним)</button>')+'<button type="button" class="pth" data-a="pth">путь по играм ▾</button><button type="button" data-a="rm" data-n="'+esc(n)+'">убрать</button></div></div>';}).join('');
    var mini=FAV.map(function(n){var w=where(games,cur,n);var i=rows.findIndex(function(r){return r.n===n;});return '<span>'+esc(n)+' <b>'+(i>=0?'#'+(i+1):'')+'</b>'+(w?' · '+(fin?'Ф':ROM[w.t]):'')+'</span>';}).join('');
    box.innerHTML='<div class="panel"><div class="dvm-h"><h3>★ Мои игроки <span class="cnt">'+FAV.length+'/'+MAX+'</span></h3><button type="button" class="dvm-tg" data-a="tg" aria-label="Свернуть/развернуть">'+(box.classList.contains('closed')?'▾':'▴')+'</button></div>'+
      (FAV.length?'<div class="dvm-mini" data-a="tg">'+mini+'</div>':'')+
      '<div class="dvm-body"><div class="dvm-q"><input type="search" autocomplete="off" placeholder="'+(FAV.length?'добавить игрока…':'Найти игрока — следить за несколькими сразу')+'" aria-label="Добавить игрока"><div class="dvm-ql" hidden></div></div>'+
      (S&&S.follow&&FAV.indexOf(S.follow)>=0?'<label class="dvm-auto"><input type="checkbox" data-a="auto" '+(S.auto?'checked':'')+'> Эфир за главным ('+esc(S.follow)+') — сам переключается на его стол в каждой новой игре</label>':'')+(FAV.length?(nowH?'<div class="dvm-now">'+nowH+'</div>':'')+rowsH:'<div class="dvm-empty">Добавь одного или нескольких игроков — здесь будет, где каждый сидит сейчас и дальше, место в таблице, путь по столам и роли в сыгранных играх.</div>')+'</div></div>';
    if(!FAV.length&&PH.matches)box.classList.remove('closed');
    var ni=$('.dvm-q input',box);if(ni&&qv)ni.value=qv;searchUI();mark();
  }
  /* подсветка ★ на плитках, в таблице, на кнопках столов */
  function mark(){var D=g('D');if(!D)return;var set={};FAV.forEach(function(n){set[n]=1;});
    $$('#seatP .st[data-p]').forEach(function(e){e.classList.toggle('dvw-fav',!!set[e.dataset.p]);});
    var tbl=$('#topP table.top');if(tbl){$$('tr',tbl).forEach(function(tr){var td=tr.children[1];if(td&&!tr.classList.contains('gap'))tr.classList.toggle('dvw-favr',!!set[td.textContent.replace(/^★\s*/,'')]);});
      var rows=D.rows||[];var shown={};$$('tr',tbl).forEach(function(tr){var td=tr.children[1];if(td)shown[td.textContent]=1;});
      var extra=FAV.map(function(n){var i=rows.findIndex(function(r){return r.n===n;});return {n:n,i:i};}).filter(function(x){return x.i>=12&&!shown[x.n];}).sort(function(a,b){return a.i-b.i;});
      if(extra.length){var tb=tbl.tBodies[0]||tbl;if(!$('tr.gap',tbl))tb.insertAdjacentHTML('beforeend','<tr class="gap"><td colspan="3">···</td></tr>');
        extra.forEach(function(x){var r=rows[x.i];tb.insertAdjacentHTML('beforeend','<tr class="dvw-favr"><td class="n">'+(x.i+1)+'</td><td>'+esc(r.n)+'</td><td class="v">'+(r.s||0).toFixed(2)+'</td></tr>');});}}
    var cur=D.cur||0;$$('#tabs button[data-t]').forEach(function(b){var t=+b.dataset.t;var c=FAV.filter(function(n){var w=where(D.games||[],cur,n);return w&&w.t===t;}).length;var e=$('.dvm-b',b);
      if(c){if(!e){e=document.createElement('span');e.className='dvm-b';b.appendChild(e);}if(e.textContent!=='★'+c)e.textContent='★'+c;}else if(e)e.remove();});}
  function init(){
    /* первый раз: главный игрок страницы попадает в список */
    var S=g('S');if(!FAV.length&&S&&S.follow){FAV=[S.follow];save();}
    render();setInterval(render,2000);
    ['#seatP','#topP','#tabs'].forEach(function(s){var el=$(s);if(el&&'MutationObserver' in window)new MutationObserver(function(){if(!mark.__busy){mark.__busy=1;setTimeout(function(){mark();mark.__busy=0;},30);}}).observe(el,{childList:true,subtree:true});});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(init,600);});else setTimeout(init,600);
})();
