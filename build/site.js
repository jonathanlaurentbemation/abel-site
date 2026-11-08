(function(){
  // en-tête : replié et opaque après un petit scroll
  var h=document.querySelector('.hdr');
  var tt=document.querySelector('.totop');
  function sc(){var y=window.scrollY;if(h){h.classList.toggle('scrolled',!document.body.classList.contains('hashero')||y>30);}if(tt)tt.classList.toggle('on',y>300);}
  sc();window.addEventListener('scroll',sc,{passive:true});
  // diaporama accueil
  var sl=[].slice.call(document.querySelectorAll('.slider .sl'));
  // ordre aléatoire à chaque visite
  for(var k=sl.length-1;k>0;k--){var r=Math.floor(Math.random()*(k+1));var t=sl[k];sl[k]=sl[r];sl[r]=t;}
  sl.forEach(function(s,idx){s.classList.toggle('on',idx===0);});
  if(sl.length>1){var i=0;setInterval(function(){sl[i].classList.remove('on');i=(i+1)%sl.length;sl[i].classList.add('on');},5000);}
  // chat Célia (iframe chargée à la première ouverture)
  var panel=document.getElementById('celia');
  window.openCelia=function(){if(!panel)return;var f=panel.querySelector('iframe');if(!f.src)f.src=f.dataset.src;panel.classList.add('open');panel.setAttribute('aria-hidden','false');};
  window.closeCelia=function(){panel.classList.remove('open');panel.setAttribute('aria-hidden','true');if(location.hash==='#open-celia')history.replaceState(null,'',location.pathname+location.search);};
  document.addEventListener('click',function(e){var a=e.target.closest('a[href="#open-celia"]');if(a){e.preventDefault();openCelia();}
    var l=e.target.closest('.gi');if(l){e.preventDefault();lb(l.getAttribute('href'));}
    if(e.target.closest('nav a')){document.body.classList.remove('nav-open');}});
  if(location.hash==='#open-celia')openCelia();
  window.addEventListener('hashchange',function(){if(location.hash==='#open-celia')openCelia();});
  // lightbox
  function lb(u){var d=document.getElementById('lb');if(!d){d=document.createElement('div');d.id='lb';d.innerHTML='<img alt="">';d.onclick=function(){d.classList.remove('on')};document.body.appendChild(d);}
    d.querySelector('img').src=u;d.classList.add('on');}
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){var d=document.getElementById('lb');if(d)d.classList.remove('on');if(panel)closeCelia();}});
  // références : ordre aléatoire à chaque visite (et limite au nombre voulu sur les pages d'accueil)
  [].forEach.call(document.querySelectorAll('.shuffle'),function(g){var c=[].slice.call(g.children);
    for(var k=c.length-1;k>0;k--){var r=Math.floor(Math.random()*(k+1));var t=c[k];c[k]=c[r];c[r]=t;}
    var n=+g.dataset.n||c.length;c.forEach(function(x,idx){if(idx<n)g.appendChild(x);else x.remove();});});
  // filtres références
  var fb=document.querySelectorAll('.filters button');
  [].forEach.call(fb,function(b){b.addEventListener('click',function(){[].forEach.call(fb,function(x){x.classList.remove('on')});b.classList.add('on');
    var f=b.dataset.f;[].forEach.call(document.querySelectorAll('#refgrid .rc'),function(c){c.classList.toggle('hide',f&&(' '+c.dataset.cats+' ').indexOf(' '+f+' ')<0);});});});
  // carte : Google Maps avec le style du site d'origine ; secours Leaflet/Esri si Google refuse la clé
  var m=document.getElementById('map');
  var GKEY='AIzaSyCweAaiYWMVlgOWk7036PrD5FAeiL9Ghos';
  var STYLE=[{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ff0000"},{"visibility":"off"}]},{"featureType":"landscape.man_made","elementType":"geometry.stroke","stylers":[{"color":"#838383"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#c2c2c2"},{"visibility":"on"},{"lightness":"-2"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#edc200"}]},{"featureType":"road.highway","elementType":"labels.text.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"},{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#bfbfbf"}]},{"featureType":"road.arterial","elementType":"labels.text.fill","stylers":[{"color":"#050505"}]},{"featureType":"road.arterial","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"road.local","elementType":"geometry.fill","stylers":[{"color":"#d4d4d4"}]},{"featureType":"road.local","elementType":"labels.text.fill","stylers":[{"color":"#5b5b5b"}]},{"featureType":"road.local","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#f5a301"},{"visibility":"on"}]},{"featureType":"water","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"water","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]}];
  var POS={lat:50.51466,lng:4.05039}, ADDR='ABEL, Rue de la Roche 3/B, 7061 Thieusies, Belgique';
  var VILLES=[[50.4542,3.9523],[50.4806,4.1866],[50.5794,4.0707]]; // Mons, La Louvière, Soignies
  var POP='<b>Hey, nous sommes ici !</b><br>Nous serons heureux de vous rencontrer en nos bureaux.';
  function leaflet(){if(m.dataset.lf)return;m.dataset.lf=1;var n=m.cloneNode(false);m.parentNode.replaceChild(n,m);m=n;
    var l=document.createElement('link');l.rel='stylesheet';l.href='https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';document.head.appendChild(l);
    var s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
    s.onload=function(){var map=L.map(m,{scrollWheelZoom:false,maxZoom:16});
      var A='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
      L.tileLayer(A+'World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',{attribution:'Tiles &copy; Esri',maxZoom:16}).addTo(map);
      L.tileLayer(A+'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}',{maxZoom:16}).addTo(map);
      map.fitBounds(VILLES.concat([[POS.lat,POS.lng]]),{padding:[30,30]});
      var ic=L.divIcon({className:'',html:'<div class="pin"></div>',iconSize:[34,34],iconAnchor:[17,34],popupAnchor:[0,-34]});
      L.marker([POS.lat,POS.lng],{icon:ic}).addTo(map).bindPopup(POP);};
    document.head.appendChild(s);}
  window.gm_authFailure=function(){leaflet();};
  window.initAbelMap=function(){
    var map=new google.maps.Map(m,{styles:STYLE,scrollwheel:false,mapTypeControl:false,streetViewControl:false,fullscreenControl:false});
    var b=new google.maps.LatLngBounds();VILLES.forEach(function(v){b.extend({lat:v[0],lng:v[1]});});b.extend(POS);map.fitBounds(b,30);
    function pin(p){var mk=new google.maps.Marker({map:map,position:p});var iw=new google.maps.InfoWindow({content:POP});mk.addListener('click',function(){iw.open(map,mk);});}
    try{new google.maps.Geocoder().geocode({address:ADDR},function(r,st){pin(st==='OK'?r[0].geometry.location:POS);});}catch(e){pin(POS);}
  };
  var GOK=/(^|\.)abel\.be$/.test(location.hostname);
  if(m){var go=function(){if(m.dataset.on)return;m.dataset.on=1;
    if(!GOK){leaflet();return;}
    var s=document.createElement('script');s.src='https://maps.googleapis.com/maps/api/js?key='+GKEY+'&callback=initAbelMap&language=fr';
    s.onerror=leaflet;document.head.appendChild(s);};
    if('IntersectionObserver' in window){new IntersectionObserver(function(e,o){if(e[0].isIntersecting){go();o.disconnect();}},{rootMargin:'400px'}).observe(m);}else go();}
})();
