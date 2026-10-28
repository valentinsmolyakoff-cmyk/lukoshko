"""Pixel-level visibility checks for letter/digit tasks, not only data/assets."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},service_workers='block')
  page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.fulfill(status=200,content_type='application/json',body='{"text":"Ребёнок осваивает новые задания. Поиграйте вместе пять минут, не торопясь с ответом. Отмечайте конкретные удачные действия и завершайте занятие, когда ребёнок устал."}'))
  page.goto('http://127.0.0.1:8000/',wait_until='domcontentloaded');page.evaluate('()=>picturesReady')
  result=page.evaluate(r'''()=>{
   save.sound=false;let checked=0;const invisible=[];const old=drawLabel;
   drawLabel=function(t,x,y,...args){old(t,x,y,...args);
    if(!['mem','seq','odd','choice','diff','sort'].includes(R?.spec.k)||!/^\p{L}$|^\d$/u.test(String(t)))return;
    const size=parseFloat(ctx.font.match(/([\d.]+)px/)?.[1]||32);let w=Math.ceil(size*.8),h=Math.ceil(size*.85);
    const xx=Math.max(0,Math.floor((x-w/2)*DPR)),yy=Math.max(0,Math.floor((y-h/2)*DPR));
    const d=ctx.getImageData(xx,yy,Math.ceil(w*DPR),Math.ceil(h*DPR)).data;let dark=0;
    for(let i=0;i<d.length;i+=4)if(d[i]<120&&d[i+1]<120&&d[i+2]<150&&d[i+3]>180)dark++;
    checked++;if(dark<8)invisible.push({level:G.level.n,k:R.spec.k,t:String(t),dark,fill:String(ctx.fillStyle)});
   };
   for(const level of LEVELS){startLevel(level.n);for(let i=0;i<level.r.length;i++){startRound(i);ctx.clearRect(0,0,Wd,Hd);ctx.fillStyle='white';ctx.fillRect(0,0,Wd,Hd);drawRound();}}
   drawLabel=old;return {checked,invisible};
  }''')
  assert result['checked']>100 and not result['invisible'],result
  print(engine,'visible letter/digit renders:',result['checked'],'invisible:',len(result['invisible']))
  page.evaluate("()=>{const l=LEVELS.find(l=>l.r.some(r=>r.q.includes('начинается слово «кот»')));startLevel(l.n);startRound(l.r.findIndex(r=>r.q.includes('начинается слово «кот»')));}")
  page.wait_for_timeout(1300);page.screenshot(path='/tmp/kot14-'+engine+'.png')
  assert page.evaluate("()=>R._optRects.some(r=>r.v==='К')")
  gain=page.evaluate("()=>{const before=G.score;const r=R._optRects.find(r=>r.v==='К');handleQuizClick({x:r.x+r.w/2,y:r.y+r.h/2});return G.score-before;}")
  assert gain>=20,gain
  page.evaluate("()=>{save.outfit={head:'🎩',neck:'🧣',feet:'👟',back:'🎒',paws:'🧤',hand:'🔦'};renderHouse();showScreen('scrHouse');}")
  page.screenshot(path='/tmp/hero14-'+engine+'.png',full_page=True)
  b.close()
