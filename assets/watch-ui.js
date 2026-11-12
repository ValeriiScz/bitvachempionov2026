/* DOVOD · assets/watch-ui.js · v1.0 · 2026-11-13 · смотровая на телефоне (дизайн-ревью):
   1) эфир — наверху экрана: «крошки» скрыты (есть ← и ⤴ в шапке), быстрые ссылки и режимы — под эфиром;
   2) мини-плеер: когда эфир уходит за верх экрана, он остаётся в углу (как в YouTube), тап — вернуться к эфиру;
   3) всё нажимаемое — не меньше 40 px. На компьютере ничего не меняется. Работает с любой смотровой (watchNNN.html). */
(function(){
  if(window.__dvWatch)return;window.__dvWatch=1;
  var M=window.matchMedia('(max-width:820px)');
  var css=document.createElement('style');
  css.textContent='@media(max-width:820px){'+
    '.dv-crumb{display:none!important}'+
    '.hd{padding-top:8px!important}'+
    '.gnav button{width:44px!important;height:40px!important;font-size:18px!important}'+
    '.tabs button{min-height:44px}'+
    '.qnav a{padding:10px 12px!important;font-size:13px!important}'+
    '.modes button{min-height:40px}'+
    '#golive,.snd,button.snd{min-height:36px;padding-left:12px;padding-right:12px}'+
    '.dvw-ph{position:relative}'+
    '.dvw-pip{position:fixed!important;top:calc(8px + env(safe-area-inset-top,0px));right:8px;width:52vw!important;max-width:320px;z-index:9500;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.65);outline:1px solid rgba(255,255,255,.18);background:#000}'+
    '.dvw-pip .snd,.dvw-pip .tcap,.dvw-pip .lbl{display:none!important}'+
    '.dvw-back{position:fixed;top:calc(8px + env(safe-area-inset-top,0px));right:8px;z-index:9501;width:52vw;max-width:320px;height:100%;max-height:30vw;background:transparent;border:0}'+
    '.dvw-x{position:fixed;z-index:9502;top:calc(12px + env(safe-area-inset-top,0px));right:12px;width:28px;height:28px;border-radius:50%;border:0;background:rgba(0,0,0,.7);color:#fff;font:700 16px/28px Inter,sans-serif;text-align:center}'+
  '}';
  document.head.appendChild(css);
  function init(){
    if(!M.matches)return;
    var stage=document.getElementById('stage'),box=document.getElementById('stagebox')||(stage&&stage.parentNode),tabs=document.getElementById('tabs'),
        modes=document.getElementById('modes'),qnav=document.getElementById('qnav'),rot=document.getElementById('rotate');
    // порядок под эфиром: столы → режимы → быстрые ссылки
    var cand=[box,tabs,rot].filter(function(e){return e&&e.parentNode&&e.parentNode===(rot||tabs||box).parentNode;});
    var after=cand.sort(function(a,b){return a.compareDocumentPosition(b)&4?-1:1;}).pop()||rot||tabs||box;   // самый нижний из «эфир/столы/подсказка»
    if(after&&after.parentNode){
      if(qnav&&qnav.parentNode)after.parentNode.insertBefore(qnav,after.nextSibling);
      if(modes&&modes.parentNode)after.parentNode.insertBefore(modes,after.nextSibling);
    }
    if(!stage||!('IntersectionObserver' in window))return;
    // мини-плеер
    var ph=document.createElement('div');ph.className='dvw-ph';stage.parentNode.insertBefore(ph,stage);ph.appendChild(stage);
    var closed=false,x=null;
    function pipOn(){if(closed||!stage.querySelector('iframe'))return;ph.style.height=ph.offsetHeight+'px';stage.classList.add('dvw-pip');
      if(!x){x=document.createElement('button');x.className='dvw-x';x.textContent='×';x.setAttribute('aria-label','Скрыть мини-плеер');
        x.onclick=function(e){e.stopPropagation();closed=true;pipOff();};document.body.appendChild(x);}}
    function pipOff(){stage.classList.remove('dvw-pip');ph.style.height='';if(x){x.remove();x=null;}}
    new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){pipOff();closed=false;}else if(e.boundingClientRect.top<0)pipOn();});},{threshold:0}).observe(ph);
    stage.addEventListener('click',function(e){if(stage.classList.contains('dvw-pip')&&!e.target.closest('iframe')){window.scrollTo({top:0,behavior:'smooth'});}},true);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
