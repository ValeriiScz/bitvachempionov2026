/* DOVOD · assets/watch-ui.js · v2.0 · 2026-11-13 · смотровая: два разных интерфейса — телефон и компьютер (дизайн-ревью)
   Работает с любой смотровой watchNNN.html по общим id (#stage, #tabs, #modes, #qnav, #seatP, #followP, #topP, #fsel) и
   глобальным S / D / tableOf / seatOf страницы. Ничего в логике страниц не меняет — только раскладка и удобство.
   ТЕЛЕФОН: эфир наверху; столы → режимы → ссылки под эфиром; мини-плеер в углу при прокрутке; телефон боком —
            эфир на весь экран; «Слежу за …» — плашка над эфиром; выбор игрока — поиск с аватарами; кнопки ≥40 px.
   КОМПЬЮТЕР (≥1100 px): трансляционный экран — шапка в одну строку, большой эфир, столы карточками, 10 мест одной строкой,
            справа поиск игрока и таблица на всю высоту; режим «Кино» (T); горячие клавиши 1–6, ← →, M, A/O, T, F, ?. */
(function(){
  if(window.__dvWatch)return;window.__dvWatch=1;
  var PH=window.matchMedia('(max-width:820px)'),PC=window.matchMedia('(min-width:1100px)');
  function $(s,r){return (r||document).querySelector(s);} function $$(s,r){return [].slice.call((r||document).querySelectorAll(s));}
  function g(name){try{return eval(name);}catch(e){return undefined;}}   // глобальные const страницы (S, D, …)
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var ROM=['','I','II','III','IV','V','VI'];
  var css=document.createElement('style');
  css.textContent=
  /* общее: плашка «слежу» и поиск игрока */
  '.dvw-fb{display:flex;align-items:center;gap:10px;margin:0 14px 8px;padding:8px 10px;border-radius:12px;border:1px solid rgba(245,255,53,.45);background:rgba(245,255,53,.07);font:600 13px/1.25 Inter,system-ui,sans-serif;color:#eef3fb}'+
  '.dvw-fb img{width:30px;height:30px;border-radius:50%;object-fit:cover;flex:none}.dvw-fb b{color:#f5ff35}.dvw-fb .s{flex:1;min-width:0}.dvw-fb small{display:block;color:#aab2c0;font-size:12px}'+
  '.dvw-fb button{flex:none;min-height:36px;padding:0 12px;border-radius:9px;border:1px solid rgba(245,255,53,.6);background:none;color:#f5ff35;font:800 12.5px Inter,sans-serif;cursor:pointer}'+
  '.dvw-fb .x{border-color:rgba(255,255,255,.2);color:#aab2c0;padding:0 10px}'+
  '.dvw-q{position:relative;margin-top:2px}.dvw-q input{width:100%;box-sizing:border-box;min-height:44px;padding:0 14px;border-radius:10px;border:1px solid rgba(255,255,255,.16);background:#0b0d14;color:#eef3fb;font:600 15px Inter,system-ui,sans-serif;outline:none}'+
  '.dvw-q input:focus{border-color:#26e0ff}'+
  '.dvw-ql{position:absolute;left:0;right:0;top:calc(100% + 4px);z-index:60;max-height:320px;overflow:auto;background:#0f1320;border:1px solid rgba(255,255,255,.14);border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.6);padding:4px}'+
  '.dvw-ql button{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;padding:4px 10px;border:0;border-radius:8px;background:none;color:#eef3fb;font:600 14px Inter,sans-serif;text-align:left;cursor:pointer}'+
  '.dvw-ql button:hover,.dvw-ql button.on{background:rgba(38,224,255,.12)}.dvw-ql img{width:28px;height:28px;border-radius:50%;object-fit:cover}.dvw-ql small{margin-left:auto;color:#9aa3b2;font-size:12px}'+
  '.dvw-hid{position:absolute!important;opacity:0!important;pointer-events:none!important;height:0!important;width:0!important}'+
  /* телефон */
  '@media(max-width:820px){'+
    '.dv-crumb{display:none!important}.hd{padding-top:8px!important}.stagebox{position:static!important}'+
    '.gnav button{width:44px!important;height:40px!important;font-size:18px!important}.tabs button{min-height:44px}'+
    '.qnav a{padding:10px 12px!important;font-size:13px!important}.modes button{min-height:40px}#golive,.snd{min-height:36px;padding-left:12px;padding-right:12px}'+
    '.dvw-ph{position:relative}'+
    '.dvw-pip{position:fixed!important;top:calc(8px + env(safe-area-inset-top,0px));right:8px;width:52vw!important;max-width:320px;z-index:9500;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.65);outline:1px solid rgba(255,255,255,.18);background:#000}'+
    '.dvw-pip .snd,.dvw-pip .lab{display:none!important}'+
    '.dvw-x{position:fixed;z-index:9502;top:calc(12px + env(safe-area-inset-top,0px));right:12px;width:30px;height:30px;border-radius:50%;border:0;background:rgba(0,0,0,.72);color:#fff;font:700 17px/30px Inter,sans-serif;text-align:center}'+
  '}'+
  /* телефон боком — эфир на весь экран (режим «один стол») */
  '@media(orientation:landscape) and (max-height:520px){body.dvw-one #stage{position:fixed!important;inset:0;z-index:9800;background:#000;width:100vw!important;max-width:none!important;border-radius:0!important}'+
    'body.dvw-one #stage .pl{padding-top:0!important;height:100vh!important;--hd:0px}body.dvw-one #stage .pl .lab{top:6px}body.dvw-one .dvw-x{display:none}}'+
  /* компьютер — трансляционный экран */
  '@media(min-width:1100px){'+
    '.wrap{max-width:none!important;width:100%;padding:0 22px 30px!important;box-sizing:border-box}'+
    '.dvw-top{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:10px 0 12px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:14px}'+
    '.dvw-top .hd{padding:0!important;flex:0 1 auto;min-width:0}.dvw-top .hd h1{white-space:nowrap}.dvw-top .status{padding:0!important;margin:0!important}'+
    '.dvw-top .qnav{padding:0!important;margin-left:auto;overflow:visible}.dvw-top .modes{padding:0!important}'+
    '.dvw-top .modes button,.dvw-top .qnav a{min-height:38px}'+
    '.body{grid-template-columns:minmax(0,1fr) 400px!important;gap:20px!important}'+
    '.body .side{position:sticky!important;top:12px;max-height:calc(100vh - 24px);overflow:auto;scrollbar-width:thin}'+
    '#stage .pl{border-radius:14px}'+
    '.tabs{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;padding:10px 0 0!important}.tabs .tcap{grid-column:1/-1}'+
    '.tabs button{min-height:58px;font-size:14px}'+
    '.dv-crumb{display:none!important}'+
    '.body .side #seatP .panel{margin-top:0}'+
    'body.dvw-theater .body .side{display:block!important;position:static!important;max-height:none}body.dvw-theater .body .side>*:not(#seatP){display:none}'+
    'body.dvw-theater #seatP .seats{grid-template-columns:repeat(10,minmax(0,1fr))!important}'+
    '#topP table.top td{padding-top:7px;padding-bottom:7px}'+
    '.rotate{display:none!important}'+
    '.dvw-keys{display:flex;gap:6px;align-items:center;color:#9aa3b2;font:600 12px Inter,sans-serif}.dvw-keys kbd{display:inline-block;min-width:20px;padding:2px 6px;border-radius:6px;border:1px solid rgba(255,255,255,.2);background:#0b0d14;color:#eef3fb;font:700 11px/1.4 "JetBrains Mono",monospace;text-align:center}'+
    '.dvw-btn{min-height:38px;padding:0 14px;border-radius:999px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.03);color:#eef3fb;font:700 13px Inter,sans-serif;cursor:pointer}.dvw-btn.on{border-color:#f5ff35;color:#f5ff35}'+
    'body.dvw-theater .body{grid-template-columns:minmax(0,1fr)!important}'+
    'body.dvw-theater #stage{max-width:calc((100vh - 150px) * 16 / 9);margin:0 auto}'+
    '.dvw-help{position:fixed;inset:0;z-index:9900;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center}'+
    '.dvw-help>div{background:#0f1320;border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:20px 24px;min-width:340px;color:#eef3fb;font:500 14px/1.9 Inter,sans-serif}'+
    '.dvw-help h4{margin:0 0 8px;font:800 16px Inter,sans-serif}.dvw-help kbd{display:inline-block;min-width:26px;margin-right:10px;padding:1px 7px;border-radius:6px;border:1px solid rgba(255,255,255,.25);font:700 12px/1.6 "JetBrains Mono",monospace;text-align:center}'+
  '}';
  document.head.appendChild(css);

  /* ── поиск игрока вместо выпадающего списка ── */
  function avatarSrc(n){try{var h=g('avatar')(n);var m=/src="([^"]+)"/.exec(h);return m?m[1]:'';}catch(e){return '';}}
  function enhanceFollow(){
    var sel=$('#fsel');if(!sel||sel.__dvw)return;sel.__dvw=1;
    var names=$$('option',sel).map(function(o){return o.value||o.textContent;}).filter(function(v,i){return i>0&&v;});
    var cur=sel.value;sel.classList.add('dvw-hid');
    var box=document.createElement('div');box.className='dvw-q';
    box.innerHTML='<input type="search" inputmode="search" autocomplete="off" placeholder="'+(cur?'Слежу: '+esc(cur)+' — найти другого':'Найти игрока по нику…')+'" aria-label="Найти игрока"><div class="dvw-ql" hidden></div>';
    sel.parentNode.insertBefore(box,sel);
    var inp=box.firstChild,list=box.lastChild,act=0;
    function pick(n){sel.value=n;sel.dispatchEvent(new Event('change',{bubbles:true}));list.hidden=true;inp.blur();}
    function show(){var q=inp.value.trim().toLowerCase();var L=names.filter(function(n){return !q||n.toLowerCase().indexOf(q)>=0;}).slice(0,40);
      var tOf=g('tableOf'),Dd=g('D');
      list.innerHTML=L.map(function(n,i){var t='';try{var tt=tOf(n,Dd.cur);t=tt?'стол '+ROM[tt]:'';}catch(e){}
        var a=avatarSrc(n);return '<button type="button" data-n="'+esc(n)+'"'+(i===act?' class="on"':'')+'>'+(a?'<img src="'+esc(a)+'" alt="" loading="lazy" onerror="this.remove()">':'')+esc(n)+'<small>'+t+'</small></button>';}).join('')||'<div style="padding:10px;color:#9aa3b2">Никого не нашли</div>';
      list.hidden=false;}
    inp.addEventListener('focus',function(){act=0;show();});inp.addEventListener('input',function(){act=0;show();});
    inp.addEventListener('keydown',function(e){var bs=$$('button',list);if(e.key==='ArrowDown'){act=Math.min(bs.length-1,act+1);show();e.preventDefault();}
      else if(e.key==='ArrowUp'){act=Math.max(0,act-1);show();e.preventDefault();}else if(e.key==='Enter'&&bs[act]){pick(bs[act].dataset.n);}else if(e.key==='Escape'){list.hidden=true;inp.blur();}});
    list.addEventListener('mousedown',function(e){var b=e.target.closest('button');if(b){e.preventDefault();pick(b.dataset.n);}});
    document.addEventListener('click',function(e){if(!box.contains(e.target))list.hidden=true;});
  }
  /* ── плашка «Слежу за …» ── */
  var fb=null;
  function followBar(){
    var S=g('S'),Dd=g('D');if(!S||!Dd)return;
    var host=$('.dvw-ph')||$('#stagebox')||$('#stage');if(!host)return;
    if(!S.follow){if(fb){fb.remove();fb=null;}return;}
    var t=null,seat=null;try{t=g('tableOf')(S.follow,Dd.cur);}catch(e){}
    try{var so=g('seatOf')(S.follow,Dd.cur);seat=so&&(so.n||so.seat||so.place||so.i);}catch(e){}
    var watching=t&&S.mode==='one'&&(S.table===t);
    var html='<img src="'+esc(avatarSrc(S.follow))+'" alt="" onerror="this.remove()"><div class="s">Слежу: <b>'+esc(S.follow)+'</b><small>'+
      (t?'сейчас — стол '+ROM[t]+(seat?' · место '+seat:''):'в этой игре не играет')+'</small></div>'+
      (t&&!watching?'<button type="button" class="go">К столу</button>':'')+'<button type="button" class="x" aria-label="Перестать следить">×</button>';
    if(!fb){fb=document.createElement('div');fb.className='dvw-fb';host.parentNode.insertBefore(fb,host);
      fb.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
        if(b.classList.contains('x')){var sel=$('#fsel');if(sel){sel.value='';sel.dispatchEvent(new Event('change',{bubbles:true}));}else{var c=$('#fclr');if(c)c.click();}}
        else{var go=$('#fgo');if(go)go.click();}});}
    if(fb.__h!==html){fb.innerHTML=html;fb.__h=html;}
  }
  /* ── телефон ── */
  function phone(){
    var stage=$('#stage'),box=$('#stagebox')||(stage&&stage.parentNode),tabs=$('#tabs'),modes=$('#modes'),qnav=$('#qnav'),rot=$('#rotate');
    var par=(rot||tabs||box);par=par&&par.parentNode;
    var cand=[box,tabs,rot].filter(function(e){return e&&e.parentNode===par;});
    var after=cand.sort(function(a,b){return a.compareDocumentPosition(b)&4?-1:1;}).pop();
    if(after){if(qnav)par.insertBefore(qnav,after.nextSibling);if(modes)par.insertBefore(modes,after.nextSibling);}
    if(!stage||!('IntersectionObserver' in window))return;
    var ph=document.createElement('div');ph.className='dvw-ph';stage.parentNode.insertBefore(ph,stage);ph.appendChild(stage);
    var closed=false,x=null;
    function on(){if(closed||!stage.querySelector('iframe'))return;ph.style.height=ph.offsetHeight+'px';stage.classList.add('dvw-pip');
      if(!x){x=document.createElement('button');x.className='dvw-x';x.textContent='×';x.setAttribute('aria-label','Скрыть мини-плеер');
        x.onclick=function(e){e.stopPropagation();closed=true;off();};document.body.appendChild(x);}}
    function off(){stage.classList.remove('dvw-pip');ph.style.height='';if(x){x.remove();x=null;}}
    new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){off();closed=false;}else if(e.boundingClientRect.top<0)on();});},{threshold:0}).observe(ph);
    stage.addEventListener('click',function(e){if(stage.classList.contains('dvw-pip')){e.preventDefault();e.stopPropagation();window.scrollTo({top:0,behavior:'smooth'});}},true);
  }
  /* ── компьютер ── */
  function desktop(){
    var wrap=$('.wrap'),hd=$('.hd');if(!wrap||!hd)return;
    var top=document.createElement('div');top.className='dvw-top';wrap.insertBefore(top,hd);
    [hd,$('#status'),$('#modes'),$('#qnav')].forEach(function(e){if(e)top.appendChild(e);});
    // справа — «за столом», слежка и таблица; слева — эфир и столы (всё на одном экране)
    var side=$('.body .side'),seat=$('#seatP');if(side&&seat)side.insertBefore(seat,side.firstChild);
    var th=document.createElement('button');th.className='dvw-btn';th.type='button';th.innerHTML='🎬 Кино <span style="opacity:.6">T</span>';th.title='Эфир на всю ширину, без боковой колонки';
    th.onclick=function(){document.body.classList.toggle('dvw-theater');th.classList.toggle('on');try{localStorage.setItem('dvw_th',document.body.classList.contains('dvw-theater')?'1':'');}catch(e){}};
    var keys=document.createElement('span');keys.className='dvw-keys';keys.innerHTML='<kbd>1</kbd>–<kbd>'+(($$('#tabs button[data-t]').length)||4)+'</kbd> столы · <kbd>←</kbd><kbd>→</kbd> игры · <kbd>M</kbd> звук · <kbd>?</kbd>';
    top.appendChild(th);top.appendChild(keys);
    try{if(localStorage.getItem('dvw_th')){document.body.classList.add('dvw-theater');th.classList.add('on');}}catch(e){}
    document.addEventListener('keydown',function(e){
      if(e.target.closest('input,select,textarea')||e.metaKey||e.ctrlKey||e.altKey)return;var k=e.key;
      if(/^[1-6]$/.test(k)){var b=$('#tabs button[data-t="'+k+'"]');if(b){b.click();e.preventDefault();}}
      else if(k==='ArrowLeft'){var p=$('#gp');if(p&&!p.disabled){p.click();e.preventDefault();}}
      else if(k==='ArrowRight'){var n=$('#gn');if(n&&!n.disabled){n.click();e.preventDefault();}}
      else if(k==='m'||k==='M'||k==='ь'||k==='Ь'){var s=$('#stage .pl.main .snd')||$('#stage .snd');if(s)s.click();}
      else if(k==='a'||k==='A'||k==='ф'||k==='Ф'){var a=$('#modes [data-m="all"]');if(a&&a.style.display!=='none')a.click();}
      else if(k==='o'||k==='O'||k==='щ'||k==='Щ'){var o=$('#modes [data-m="one"]');if(o)o.click();}
      else if(k==='t'||k==='T'||k==='е'||k==='Е'){th.click();}
      else if(k==='f'||k==='F'||k==='а'||k==='А'){var i=$('.dvw-q input');if(i){i.focus();e.preventDefault();}}
      else if(k==='?'||k===','){help();}
      else if(k==='Escape'){var h=$('.dvw-help');if(h)h.remove();}
    });
  }
  function help(){if($('.dvw-help'))return;var d=document.createElement('div');d.className='dvw-help';
    d.innerHTML='<div><h4>Горячие клавиши</h4><kbd>1–6</kbd>стол<br><kbd>←</kbd><kbd>→</kbd>предыдущая / следующая игра<br><kbd>M</kbd>звук главного эфира<br><kbd>A</kbd>все столы · <kbd>O</kbd>один стол<br><kbd>T</kbd>режим «Кино»<br><kbd>F</kbd>найти игрока<br><kbd>Esc</kbd>закрыть</div>';
    d.onclick=function(){d.remove();};document.body.appendChild(d);}
  /* ── запуск ── */
  function tick(){enhanceFollow();followBar();var S=g('S');if(S)document.body.classList.toggle('dvw-one',S.mode==='one');}
  function init(){
    if(PH.matches)phone();
    if(PC.matches)desktop();
    tick();setInterval(tick,1500);
    var fp=$('#followP');if(fp&&'MutationObserver' in window)new MutationObserver(function(){enhanceFollow();followBar();}).observe(fp,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
