from playwright.sync_api import sync_playwright
import json
ADVICE='В заданиях на память ребёнок часто находит верную пару. Предложите пройти простой лабиринт пальцем, останавливаясь на каждом повороте. Через пять минут можно попробовать уровень 29.'
with sync_playwright() as p:
 for name in ['chromium','webkit']:
  browser=getattr(p,name).launch(headless=True);c=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block');page=c.new_page();errors=[];calls=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def mock(r):calls.append(1);r.fulfill(status=200,content_type='application/json',body=json.dumps({'text':ADVICE}))
  page.route('https://lukoshko-ai.vercel.app/api/advice',mock)
  page.goto('http://127.0.0.1:8000/',wait_until='networkidle');page.evaluate('()=>picturesReady');assert not calls
  assert page.evaluate('()=>assetsLoaded')
  # Follow the real parent lock; no API before the correct answer.
  page.locator('#btnParent').click();assert not calls
  page.locator('#lockInput').fill(str(page.evaluate('()=>lockAnswer')));page.locator('#btnLockOk').click()
  page.wait_for_function("()=>document.getElementById('aiNote').textContent.startsWith('Рекомендация ИИ · Gemini')")
  assert len(calls)==1;assert page.locator('#aiOut').inner_text()==ADVICE
  page.evaluate('()=>loadParentAdvice(false)');assert len(calls)==1
  report=page.evaluate(r'''()=>{
   save.sound=false;const old=drawLabel;let pictures=0;const missing=new Set();
   drawLabel=function(t,...a){if(/\p{Extended_Pictographic}/u.test(String(t))){if(!pictureImages.has(pictureKey(t)))missing.add(String(t));else pictures++;}return old(t,...a)};
   let rounds=0;for(const l of LEVELS){startLevel(l.n);for(let i=0;i<l.r.length;i++){startRound(i);drawRound();rounds++;if(['catch','word','sort','rhythm'].includes(R.spec.k)){for(let j=0;j<12;j++){if(R.spec.k==='sort')spawnSortItem();else spawnItem();}drawRound();}}}
   return {rounds,pictures,missing:[...missing],loaded:[...pictureImages.values()].filter(i=>i.complete&&i.naturalWidth>0).length,hero:[...heroLayers.values()].every(i=>i.complete&&i.naturalWidth>0)};
  }''')
  assert report['rounds']==490 and not report['missing'] and report['loaded']==281 and report['hero'],report
  page.evaluate("()=>{save.outfit={head:'🎩',neck:'🧣',feet:'👟',back:'🎒',paws:'🧤',hand:'🔦'};renderHouse();showScreen('scrHouse');}");page.wait_for_timeout(200)
  page.screenshot(path='/tmp/house13-'+name+'.png',full_page=True)
  page.evaluate("()=>{startLevel(7);startRound(G.level.r.findIndex(r=>r.k==='odd'));}");page.wait_for_timeout(1300);page.screenshot(path='/tmp/odd13-'+name+'.png')
  # An explicit refresh failing must not masquerade as local or saved AI.
  page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.fulfill(status=503,body='{}'))
  page.evaluate('()=>loadParentAdvice(true)');assert 'Не удалось получить' in page.locator('#aiOut').inner_text()
  assert not errors,errors
  print(name,'PASS:',report,'API on parent login only; provider error visible')
  browser.close()
