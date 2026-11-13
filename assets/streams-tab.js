/* DOVOD · assets/streams-tab.js · v1.0 · 2026-11-13
   Вкладка «Трансляции» на странице турнира (t*.html): эфир прямо во вкладке, а не голые кнопки.
   · сверху — встроенный плеер YouTube: в дни турнира — текущая игра (день по дате, финал — эфир финала),
     после турнира — записи; переключатель «День · Стол / Финал / Студия»;
   · под плеером — большая кнопка «Смотровая — все столы сразу» и маленькая «открыть в YouTube»;
   · ссылок нет — честная заглушка 16:9 «эфир появится здесь» с отсчётом до старта.
   Источник ссылок тот же, что у смотровой: window.STREAMS_DB[id] (data/streams.js, data/streams_{id}.json, Google-таблица).
   Подключение: <script src="assets/streams-tab.js?v=1"></script> до основного скрипта; в streams() страницы —
   ${window.DVST?DVST.html(CFG,D):streamsPanel()}. Состояние выбора — в памяти страницы. */
(function(){
  var R=['','I','II','III','IV','V','VI'];
  var sel=null, ctx=null, timer=null;
  var css='.dvst{margin-bottom:14px}.dvst .pl{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#05060a;border:1px solid rgba(255,255,255,.12)}'+
    '.dvst .pl iframe{position:absolute;inset:0;width:100%;height:100%;border:0}'+
    '.dvst .ph{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;padding:18px;'+
    'background:radial-gradient(500px 260px at 50% 0%,rgba(245,255,53,.08),transparent 70%),repeating-linear-gradient(135deg,rgba(255,255,255,.025) 0 12px,transparent 12px 24px)}'+
    '.dvst .ph .pi{width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:rgba(245,255,53,.12);color:#f5ff35;font-size:24px;border:1px solid rgba(245,255,53,.35)}'+
    '.dvst .ph b{font:800 16px/1.25 Inter,system-ui,sans-serif;color:#eef3fb}.dvst .ph small{font:500 12.5px/1.45 Inter,system-ui,sans-serif;color:#a4adbd;max-width:420px}'+
    '.dvst .cd{font:800 22px/1 "JetBrains Mono",monospace;color:#f5ff35;letter-spacing:.04em}'+
    '.dvst .now{display:flex;align-items:center;gap:8px;margin:10px 0 0;font:700 12.5px/1.3 Inter,system-ui,sans-serif;color:#cfd5df}.dvst .now .lv{display:inline-flex;align-items:center;gap:5px;padding:3px 8px;border-radius:999px;background:rgba(219,81,78,.16);color:#ff8a86;font:800 10.5px/1 "JetBrains Mono",monospace;letter-spacing:.08em}'+
    '.dvst .now .lv i{width:7px;height:7px;border-radius:50%;background:#db514e;animation:dvstp 1.4s infinite}@keyframes dvstp{50%{opacity:.3}}'+
    '.dvst .grp{margin-top:12px}.dvst .gl{font:800 10px/1 "JetBrains Mono",monospace;letter-spacing:.14em;text-transform:uppercase;color:#79808f;margin:0 0 6px}'+
    '.dvst .chips{display:flex;flex-wrap:wrap;gap:6px}.dvst .ch{min-height:40px;padding:0 14px;border-radius:10px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.04);color:#cfd5df;font:700 13px/1 Inter,system-ui,sans-serif;cursor:pointer}'+
    '.dvst .ch.on{background:#f5ff35;color:#05060a;border-color:transparent}.dvst .ch.st{border-color:rgba(193,75,189,.55);color:#e7a6e3}.dvst .ch.st.on{background:#c14bbd;color:#fff}'+
    '.dvst .acts{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:14px}'+
    '.dvst .big{flex:1 1 260px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;min-height:52px;padding:8px 18px;text-align:center;border-radius:12px;background:#f5ff35;color:#05060a;font:800 14.5px/1.1 Inter,system-ui,sans-serif;text-decoration:none;box-shadow:0 8px 26px rgba(245,255,53,.16)}'+
    '.dvst .big small{font-weight:700;opacity:.7;font-size:11.5px}.dvst .yt{font:700 12.5px/1 Inter,system-ui,sans-serif;color:#a4adbd;text-decoration:none;padding:10px 4px}.dvst .yt:hover{color:#fff}';
  var stl=document.createElement('style');stl.textContent=css;document.head.appendChild(stl);
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function today(){var n=new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Prague'}));return n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0');}
  function emb(id){var b=/^live:/.test(id)?'https://www.youtube.com/embed/live_stream?channel='+encodeURIComponent(id.slice(5))+'&':'https://www.youtube.com/embed/'+encodeURIComponent(id)+'?';
    return b+'autoplay=1&mute=1&playsinline=1&rel=0&modestbranding=1';}
  function wurl(id){return window.ytWatchURL?window.ytWatchURL(id):'https://www.youtube.com/watch?v='+id;}
  /* все доступные эфиры турнира списком */
  function items(st,CFG){var out=[];if(!st)return out;
    Object.keys(st.days||{}).sort().forEach(function(d){var tb=st.days[d]||{};Object.keys(tb).sort(function(a,b){return a-b;}).forEach(function(t){if(tb[t])out.push({k:'d'+d+'t'+t,g:'День '+d,lab:'Стол '+(R[+t]||t),id:tb[t],day:d,t:+t});});});
    if(st.final)out.push({k:'fin',g:'Финал',lab:'Финальный стол',id:st.final,fin:1});
    Object.keys(st.studio||{}).sort().forEach(function(d){if(st.studio[d])out.push({k:'s'+d,g:'Студия аналитики',lab:'🎙 День '+d,id:st.studio[d],st:1});});
    return out;}
  /* что показывать по умолчанию: идёт турнир — текущий день/финал, стол моего игрока или I; иначе — первое */
  function auto(list,st,CFG,D){if(!list.length)return null;
    var games=(D&&(D.realGames||D.games))||[];var cur=games.findIndex(function(g){return g.tables.some(function(t){return t.winner==='unknown';});});
    var g=cur>=0?games[cur]:null;
    if(g&&g.stage==='Финал'){var f=list.find(function(x){return x.fin;});if(f)return f.k;}
    var dd=st.dayDates||{},t=today(),day=null;Object.keys(dd).forEach(function(k){if(t>=dd[k])day=k;});
    var my=null;try{my=localStorage.getItem(CFG.ls+'my');}catch(e){}
    var myT=null;if(g&&my){var tb=g.tables.find(function(x){return x.seats.some(function(s){return s&&s.name===my;});});if(tb)myT=tb.table_num;}
    if(day){var a=list.find(function(x){return x.day===day&&x.t===(myT||1);})||list.find(function(x){return x.day===day;});if(a)return a.k;}
    return list[0].k;}
  function startISO(D){return (D&&D.tour&&D.tour.start_iso)||null;}
  function cdText(iso){if(!iso)return '';var s=Math.floor((new Date(iso)-Date.now())/1000);if(s<=0)return '';var d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return (d?d+' д ':'')+String(h).padStart(2,'0')+':'+String(m).padStart(2,'0');}
  function render(){var el=document.getElementById('dvstBox');if(!el||!ctx)return;el.outerHTML=html(ctx.CFG,ctx.D);}
  function html(CFG,D){
    ctx={CFG:CFG,D:D};
    var st=window.STREAMS_DB&&window.STREAMS_DB[CFG.id];var list=items(st,CFG);
    if(!sel||!list.some(function(x){return x.k===sel;}))sel=auto(list,st||{},CFG,D);
    var it=list.find(function(x){return x.k===sel;});
    var games=(D&&(D.realGames||D.games))||[];var played=games.filter(function(g){return g.tables.length&&g.tables.every(function(t){return t.winner!=='unknown';});}).length;
    var live=!!window.__liveOn;var iso=startISO(D);var cd=cdText(iso);
    var player;
    if(it){player='<div class="pl"><iframe src="'+emb(it.id)+'" title="Эфир" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen loading="lazy"></iframe></div>';}
    else{player='<div class="pl"><div class="ph"><div class="pi">▶</div><b>Эфир появится здесь</b>'+(cd?'<div class="cd" id="dvstCd">'+cd+'</div><small>до старта · ссылки на трансляции организаторы публикуют перед началом — подставим сразу</small>':'<small>ссылок на трансляции пока нет — как только организаторы опубликуют, эфир включится прямо здесь. Рассадка, таблица и «следить за игроком» уже работают в смотровой.</small>')+'</div></div>';}
    var now='';if(it){now='<div class="now">'+(live&&!it.st?'<span class="lv"><i></i>LIVE</span>':'')+'<span>'+esc(it.g)+' · '+esc(it.lab)+(played?' · сыграно игр: '+played:'')+'</span></div>';}
    var groups={},order=[];list.forEach(function(x){if(!groups[x.g]){groups[x.g]=[];order.push(x.g);}groups[x.g].push(x);});
    var chips=order.map(function(g){return '<div class="grp"><div class="gl">'+esc(g)+'</div><div class="chips">'+groups[g].map(function(x){return '<button type="button" class="ch'+(x.st?' st':'')+(x.k===sel?' on':'')+'" onclick="DVST.pick(\''+x.k+'\')">'+esc(x.lab)+'</button>';}).join('')+'</div></div>';}).join('');
    var acts='<div class="acts"><a class="big" href="'+esc(CFG.watch||('watch'+CFG.id+'.html'))+'">▶ Смотровая — все столы сразу <small>следить за игроком</small></a>'+(it?'<a class="yt" href="'+esc(wurl(it.id))+'" target="_blank" rel="noopener">открыть в YouTube ↗</a>':'')+'</div>';
    if(timer)clearInterval(timer);if(!it&&cd)timer=setInterval(function(){var c=document.getElementById('dvstCd');if(!c){clearInterval(timer);return;}c.textContent=cdText(iso)||'скоро';},30000);
    return '<div class="panel dvst" id="dvstBox">'+player+now+acts+chips+'</div>';
  }
  window.DVST={html:html,pick:function(k){sel=k;render();}};
})();
