/* DOVOD · assets/strength.js · v1.2 · 2026-11-12 (прогноз для собирающихся: пунктирная рамка, «прогноз (20/40)») · v1.1 · 2026-11-12 (данные — data/strength.js: все рейтинговые турниры и серии календаря; подсказка — шанс эталона A) · v1.0 · 2026-11-12
   Значок «сила состава»: 5 столбиков (как сигнал связи) + слово. Считает робот refresh_mafiastats (две группы: рейтинговые и серии,
   поправка на размер — шанс игрока уровня A, MMR 1700, дойти до финала/подиума против шанса при равных). Используется на «Турниры», «Календарь», главной. */
(function(){
  var L=['мягкий','ниже среднего','средний','выше среднего','экстремальный'];
  var C={'мягкий':'#5ec8c0','ниже среднего':'#7aa7d6','средний':'#b9c0cc','выше среднего':'#f0a64a','экстремальный':'#ff5a5a'};
  var css='.dvs{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:8px;border:1px solid var(--dvs);color:var(--dvs);background:color-mix(in srgb,var(--dvs) 10%,transparent);font:700 12px/1 Inter,system-ui,sans-serif;white-space:nowrap;vertical-align:middle}'+
    '.dvs .bars{display:inline-flex;align-items:flex-end;gap:2px;height:12px}.dvs .bars i{display:block;width:3px;border-radius:1px;background:currentColor;opacity:.25}.dvs .bars i.on{opacity:1}'+
    '.dvs.proj{border-style:dashed;background:transparent}.dvs .lb{color:#9aa2b1;font-weight:600}.dvs.mini{padding:2px 5px;border-radius:6px;gap:0}.dvs.mini .bars{height:10px}';
  var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  function bars(k){var h='';for(var i=1;i<=5;i++)h+='<i class="'+(i<=k?'on':'')+'" style="height:'+(2+i*2)+'px"></i>';return '<span class="bars">'+h+'</span>';}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  window.DVS={
    html:function(x,mini){if(!x||!x.lvl)return '';var k=L.indexOf(x.lvl)+1;if(!k)return '';
      var tip=(x.proj?'Прогноз — состав ещё собирается: записано '+x.reg+' из '+x.exp+'. Оценка — как если бы турнир был на '+x.reg+' человек ('+x.places+' мест в '+(x.goal==='подиум'?'тройке':'финале')+'). ':'')+
        'Сила состава: '+x.lvl+' — '+x.rank+'-й из '+x.of+' ('+x.win+')'+
        (x.ch!=null?'. Шанс игрока уровня A пройти в '+(x.goal==='подиум'?'тройку':'финал')+': '+Math.round(x.ch)+'% (если бы все были равны — '+Math.round(x.eq)+'%)':'')+
        (x.pts!=null?'. Очки состава '+x.pts+' (L=3, S=2, A=1), C и выше: '+x.cplus:'');
      var pc=x.proj?' proj':'';
      return mini?'<span class="dvs mini'+pc+'" style="--dvs:'+C[x.lvl]+'" title="'+esc(tip)+'">'+bars(k)+'</span>'
                 :'<span class="dvs'+pc+'" style="--dvs:'+C[x.lvl]+'" title="'+esc(tip)+'">'+bars(k)+'<span class="lb">'+(x.proj?'прогноз ('+x.reg+'/'+x.exp+'):':'сила состава:')+'</span>'+esc(x.lvl)+'</span>';},
    byId:function(id){var S=window.DV_STRENGTH;if(S&&S[String(id)])return S[String(id)];var T=(window.TOURNAMENTS_DB&&window.TOURNAMENTS_DB.tournaments)||[];for(var i=0;i<T.length;i++)if(String(T[i].id)===String(id))return T[i].strength||null;return null;}
  };
})();
