/* DOVOD · assets/dv-ui.js · v1.0 · 2026-11-13
   Общий слой интерфейса для всех страниц (подключается из assets/share.js):
   1) нижнее меню на телефоне — одно на весь сайт (Сейчас · Турниры · Календарь · Серии · Ещё);
      не ставится там, где у страницы своё нижнее меню (.tabbar — страницы турниров), в смотровых и в режиме ?embed=1;
   2) читаемость: подписи мельче 11 px поднимаются до 11 px, серый текст с контрастом ниже 4.5:1 (WCAG AA)
      осветляется до 4.5:1 — оттенок сохраняется; работает и для того, что страница дорисовывает позже. */
(function(){
  if(window.__dvUI)return;window.__dvUI=1;
  var path=(location.pathname.split('/').pop()||'index.html').toLowerCase();
  var embed=/[?&]embed=1/.test(location.search);
  /* ── 1) нижнее меню ── */
  var SEC=[['now','Сейчас','/','M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'],
           ['tour','Турниры','/tournaments.html','M8 4h8v3a4 4 0 0 1-8 0zM5 5h3v2a3 3 0 0 1-3-2zm11 0h3a3 3 0 0 1-3 2zM10 13h4v3h-4zM7 19h10v2H7z'],
           ['cal','Календарь','/calendar.html','M4 6h16v14H4zM4 10h16M8 3v4M16 3v4'],
           ['ser','Серии','/series.html','M4 18V9M10 18V5M16 18v-7M22 18H2'],
           ['more','Ещё','#','M5 12h.01M12 12h.01M19 12h.01']];
  function active(){
    if(path==='index.html'||path==='')return 'now';
    if(/^(tournaments|tournament|participants|seating|cards|standings|results|roles|player|markers|ce6|teams|wc2026|logisticpro|t\d)/.test(path))return 'tour';
    if(/^(calendar|season)/.test(path))return 'cal';
    if(/^(series|mcl|gmc)/.test(path))return 'ser';
    return 'more';
  }
  var MORE=[['Гонка за дюжину','/race.html'],['Статьи','/articles.html'],['Лаборатория','/lab.html'],['MCL Europe','/mcl2026.html'],['German Mafia Cup','/gmc664.html'],['Сводка сезона','/season.html']];
  function nav(){
    if(embed||document.querySelector('.tabbar')||/^watch/.test(path))return;
    var css=document.createElement('style');
    css.textContent='@media(max-width:820px){body{padding-bottom:calc(64px + env(safe-area-inset-bottom,0px))!important}'+
      '.dvnav{position:fixed;left:0;right:0;bottom:0;z-index:9000;display:flex;background:rgba(8,10,16,.94);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-top:1px solid rgba(255,255,255,.1);padding:4px 4px calc(4px + env(safe-area-inset-bottom,0px))}'+
      '.dvnav a{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;min-height:52px;border-radius:12px;color:#9aa3b2;text-decoration:none;font:600 11px/1 Inter,system-ui,sans-serif;letter-spacing:0;text-transform:none}'+
      '.dvnav a svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}'+
      '.dvnav a.on{color:#f5ff35}.dvnav a.on svg{filter:drop-shadow(0 0 6px rgba(245,255,53,.45))}'+
      '.dvmore{position:fixed;left:8px;right:8px;bottom:calc(68px + env(safe-area-inset-bottom,0px));z-index:9001;background:#0f1320;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:6px;box-shadow:0 12px 34px rgba(0,0,0,.6)}'+
      '.dvmore a{display:flex;align-items:center;min-height:46px;padding:0 14px;border-radius:10px;color:#e9ecf3;text-decoration:none;font:600 15px/1 Inter,system-ui,sans-serif}.dvmore a:active{background:rgba(255,255,255,.06)}}'+
      '@media(min-width:821px){.dvnav,.dvmore{display:none!important}}';
    document.head.appendChild(css);
    var on=active(),n=document.createElement('nav');n.className='dvnav';n.setAttribute('aria-label','Разделы сайта');
    n.innerHTML=SEC.map(function(s){return '<a href="'+s[2]+'" data-k="'+s[0]+'"'+(s[0]===on?' class="on" aria-current="page"':'')+'><svg viewBox="0 0 24 24"><path d="'+s[3]+'"/></svg>'+s[1]+'</a>';}).join('');
    document.body.appendChild(n);
    var sheet=null;
    n.querySelector('[data-k="more"]').addEventListener('click',function(e){e.preventDefault();
      if(sheet){sheet.remove();sheet=null;return;}
      sheet=document.createElement('div');sheet.className='dvmore';sheet.innerHTML=MORE.map(function(m){return '<a href="'+m[1]+'">'+m[0]+'</a>';}).join('');
      document.body.appendChild(sheet);
      setTimeout(function(){document.addEventListener('click',function c(ev){if(sheet&&!sheet.contains(ev.target)&&!n.contains(ev.target)){sheet.remove();sheet=null;document.removeEventListener('click',c);}});},0);});
  }
  /* ── 1б) ощущение приложения: без синих вспышек и задержки тапа, отклик на нажатие, плавные переходы между страницами ── */
  (function(){var st=document.createElement('style');st.textContent=
    'html{-webkit-tap-highlight-color:transparent;-webkit-text-size-adjust:100%}'+
    'a,button,[onclick],summary,label{touch-action:manipulation}'+
    '@media(hover:none){a:active,button:active,[onclick]:active{opacity:.72;transition:opacity .06s}}'+
    '@view-transition{navigation:auto}::view-transition-old(root),::view-transition-new(root){animation-duration:.16s}'+
    ':focus-visible{outline:2px solid #26e0ff;outline-offset:2px}';
    document.head.appendChild(st);})();
  /* ── 2) читаемость ── */
  function rgb(s){var m=s&&s.match(/rgba?\(([^)]+)\)/);if(!m)return null;var p=m[1].split(/[ ,/]+/).filter(Boolean).map(parseFloat);return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
  function lum(c){function f(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4);}return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b);}
  function ratio(a,b){var x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
  var PAGE=null;
  function bgOf(el){
    while(el&&el.nodeType===1){var cs=getComputedStyle(el),c=rgb(cs.backgroundColor);
      if(cs.backgroundImage&&cs.backgroundImage!=='none'&&!(c&&c.a>.85))return null;   // картинка/градиент — не трогаем
      if(c&&c.a>.85)return c; el=el.parentElement;}
    return PAGE;
  }
  function fixEl(el){
    if(el.__dvfx||el.closest('svg,.dvnav,.dvmore,canvas,.poster,.pst,.vis,.dvpo'))return;el.__dvfx=1;
    var cs=getComputedStyle(el),fs=parseFloat(cs.fontSize);
    if(fs<11){el.style.fontSize='11px';fs=11;if(parseFloat(cs.letterSpacing)>1.2)el.style.letterSpacing='.06em';}
    if(fs>=18)return;
    var c=rgb(cs.color);if(!c||c.a<.2)return;var bg=bgOf(el);if(!bg)return;
    if(lum(bg)>.4)return;                                   // светлые плашки не трогаем
    if(ratio(c,bg)>=4.5)return;
    var k=0,n={r:c.r,g:c.g,b:c.b};
    while(ratio(n,bg)<4.5&&k<30){n.r+=(255-n.r)*.08;n.g+=(255-n.g)*.08;n.b+=(255-n.b)*.08;k++;}
    el.style.color='rgb('+Math.round(n.r)+','+Math.round(n.g)+','+Math.round(n.b)+')';
    if(c.a<1)el.style.opacity='1';
  }
  function pass(root){
    var all=(root||document.body).querySelectorAll('*');
    for(var i=0;i<all.length;i++){var e=all[i],t=false;for(var j=0;j<e.childNodes.length;j++){var ch=e.childNodes[j];if(ch.nodeType===3&&ch.nodeValue.trim()){t=true;break;}}if(t)fixEl(e);}
  }
  var timer=null;
  function schedule(){clearTimeout(timer);timer=setTimeout(function(){pass();},250);}
  function init(){
    PAGE=rgb(getComputedStyle(document.body).backgroundColor);if(!PAGE||PAGE.a<.5)PAGE=rgb(getComputedStyle(document.documentElement).backgroundColor);if(!PAGE||PAGE.a<.5)PAGE={r:5,g:6,b:10,a:1};
    nav();
    if(lum(PAGE)<.2){pass();setTimeout(pass,1200);try{new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});}catch(e){}}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
