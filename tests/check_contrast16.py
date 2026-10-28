from playwright.sync_api import sync_playwright
import json
AUDIT=r'''()=>{
const rgba=s=>{const a=String(s).match(/[\d.]+/g);return a?[+a[0],+a[1],+a[2],a[3]===undefined?1:+a[3]]:[0,0,0,0]};
const blend=(a,b)=>a.slice(0,3).map((v,i)=>v*a[3]+b[i]*(1-a[3]));
const lum=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
const ratio=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
let checked=0,fail=[];
for(const el of document.querySelectorAll('body *')){
 if(['SCRIPT','STYLE','CANVAS','SVG','PATH'].includes(el.tagName))continue;
 const text=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();if(!/[\p{L}\p{N}]/u.test(text))continue;
 const st=getComputedStyle(el),rect=el.getBoundingClientRect();if(!rect.width||!rect.height||st.visibility==='hidden')continue;
 const chain=[];for(let p=el;p;p=p.parentElement)chain.unshift(p);
 if(chain.some(p=>getComputedStyle(p).display==='none'))continue;
 let samples=[[255,255,255]],opacity=1;
 for(const p of chain){const s=getComputedStyle(p);opacity*=+s.opacity;
  samples=samples.map(bg=>blend(rgba(s.backgroundColor),bg));
  const stops=s.backgroundImage.match(/rgba?\([^)]+\)/g)||[];if(stops.length){samples=samples.flatMap(bg=>stops.map(t=>blend(rgba(t),bg))).slice(-30);}
 }
 if(opacity<.05)continue;
 const color=rgba(st.color);color[3]*=opacity;
 const value=Math.min(...samples.map(bg=>ratio(blend(color,bg),bg)));
 const size=parseFloat(st.fontSize),bold=+st.fontWeight>=700,target=(size>=24||(size>=18.66&&bold))?3:4.5;
 checked++;if(value+.03<target)fail.push({text:text.slice(0,75),tag:el.tagName,id:el.id,cls:el.className,color:st.color,ratio:+value.toFixed(2),target});
}
return {checked,fail};}'''
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},service_workers='block')
  page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.abort());page.goto('http://127.0.0.1:8000/',wait_until='domcontentloaded');page.evaluate('()=>picturesReady')
  reports={}
  for screen,setup in [('menu','renderMenu();showScreen("scrMenu")'),('map','renderMap();showScreen("scrMap")'),('house','renderHouse();showScreen("scrHouse")'),('parent','renderParent();showScreen("scrParent")'),('lock','openParentGate()'),('intro','startLevel(1)'),('result','startLevel(1);showResult(3,true)')]:
   page.evaluate('()=>{save.sound=false;'+setup+'}');page.wait_for_timeout(1400 if screen=='result' else 450)
   reports[screen]=page.evaluate(AUDIT)
  print(engine,'DOM:',json.dumps(reports,ensure_ascii=False))
  assert not any(r['fail']for r in reports.values()),reports
  page.evaluate('()=>{save.levels=Object.fromEntries(LEVELS.map(l=>[l.n,{stars:3}]));save.skills={attention:{ok:95,miss:5},letters:{ok:8,miss:30}};save.medals=9;ensureDaily().tasks.forEach(t=>t.done=true);save.outfit={head:"🎩",neck:"🧣",feet:"👟",back:"🎒",paws:"🧤"};}')
  for width in [320,768]:
   page.set_viewport_size({'width':width,'height':844})
   for setup in ['renderMenu();showScreen("scrMenu")','renderMap();showScreen("scrMap")','renderHouse();showScreen("scrHouse")','renderParent();showScreen("scrParent");document.getElementById("btnAiRefresh").disabled=true','openParentGate();document.getElementById("lockErr").textContent="Неверно. Попробуйте ещё раз."']:
    page.evaluate('()=>{'+setup+'}');extra=page.evaluate(AUDIT);assert not extra['fail'],extra
  page.set_viewport_size({'width':390,'height':844})
  print(engine,'extra states PASS: completed map/daily, unlocked wardrobe, disabled button, error; 320/768px')
  report=page.evaluate(r'''()=>{
   function lum(c){return c.map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0)}
   const old=drawLabel;let checked=0;const fail=[];
   drawLabel=function(t,x,y,...args){
    if(!pictureImages.has(pictureKey(t))&&/[\p{L}\p{N}?]/u.test(String(t))){
     const m=ctx.getTransform(),xx=Math.round(m.a*x+m.c*y+m.e),yy=Math.round(m.b*x+m.d*y+m.f);
     if(xx>=0&&xx<cvs.width&&yy>=0&&yy<cvs.height){
      const d=Array.from(ctx.getImageData(xx,yy,1,1).data).slice(0,3),s=String(ctx.fillStyle);let fg;
      if(s.startsWith('#'))fg=[1,3,5].map(i=>parseInt(s.slice(i,i+2),16));else fg=(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
      if(fg.length===3){const a=lum(fg),b=lum(d),r=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);checked++;const fs=parseFloat(ctx.font.match(/([\d.]+)px/)?.[1]||16),threshold=(fs>=24||(/bold|[7-9]00/.test(ctx.font)&&fs>=18.66))?3:4.5;if(r<threshold)fail.push({level:G.level.n,k:R.spec.k,text:t,ratio:r,fg:s,bg:d});}
     }
    }return old(t,x,y,...args);
   };
   save.sound=false;
   for(const l of LEVELS){startLevel(l.n);for(let i=0;i<l.r.length;i++){startRound(i);drawBackground();drawRound();if(R.spec.k==='word'){R.idx=Math.min(2,R.word.length);drawBackground();drawRound();}}}
   drawLabel=old;return {checked,fail};
  }''')
  print(engine,'CANVAS:',json.dumps(report,ensure_ascii=False));assert not report['fail'],report
  page.evaluate("()=>{document.getElementById('lvlIntro').classList.remove('show');save.outfit={};renderHouse();showScreen('scrHouse');}");page.screenshot(path='/tmp/natural16-'+engine+'.png',full_page=True)
  page.evaluate("()=>{save.outfit={head:'🎩',neck:'🧣',feet:'👟',back:'🎒',paws:'🧤',hand:'🔦'};renderHouse();}");page.screenshot(path='/tmp/natural16-outfit-'+engine+'.png',full_page=True)
  b.close()
