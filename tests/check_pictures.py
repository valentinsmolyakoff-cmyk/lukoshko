from playwright.sync_api import sync_playwright
from pathlib import Path
import json
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844});errors=[];calls=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def advice(route):
  calls.append(route.request.post_data)
  route.fulfill(status=200,content_type='application/json',body=json.dumps({'text':'В заданиях на память ребёнок часто находит верную пару. Предложите пройти простой лабиринт пальцем, останавливаясь на каждом повороте. Через пять минут можно попробовать уровень 29.'},ensure_ascii=False))
 page.route('https://lukoshko-ai.vercel.app/api/advice',advice)
 page.goto('http://127.0.0.1:8000/',wait_until='networkidle');page.evaluate('()=>picturesReady')
 assert len(calls)==1, calls
 print('Advice started on page load exactly once')
 page.evaluate('async()=>{await loadParentAdvice();await loadParentAdvice(true);renderParent();showScreen("scrParent");await loadParentAdvice();G.level=LEVELS[0];await aiAdviceForLevel();}')
 assert len(calls)==1,len(calls)
 print('Reopening parent page, refresh and level result do not create another request')
 # Simulate an OS with no emoji font: any uncaught emoji text must fail the test.
 report=page.evaluate(r'''()=>{
  save.sound=false;
  const native=systemFillText;const old=ctx.fillText.bind(ctx);const missing=new Set();let pictures=0;
  ctx.fillText=function(t,...args){if(/\p{Extended_Pictographic}/u.test(String(t))){if(!pictureImages.has(pictureKey(t)))missing.add(String(t));else pictures++;}return old(t,...args)};
  let rounds=0;
  for(const level of LEVELS){startLevel(level.n);for(let i=0;i<level.r.length;i++){
    startRound(i);drawRound();rounds++;
    if(['catch','word','sort','rhythm'].includes(R.spec.k)){for(let n=0;n<12;n++){if(R.spec.k==='sort')spawnSortItem();else spawnItem();}drawRound();}
  }}
  return {rounds,pictures,missing:[...missing],loaded:[...pictureImages.values()].filter(im=>im.complete&&im.naturalWidth>0).length,total:pictureImages.size};
 }''')
 print('Rendering coverage:',report)
 assert report['rounds']==490 and not report['missing'] and report['loaded']==report['total']
 # All symbols in task data must have an asset, including those not randomly spawned.
 missing=page.evaluate(r'''()=>{
 const bad=new Set();const visit=v=>{if(typeof v==='string'){for(const ch of (v.match(/\p{Extended_Pictographic}(?:\uFE0F|\p{Emoji_Modifier})?(?:\u200D\p{Extended_Pictographic}(?:\uFE0F|\p{Emoji_Modifier})?)*/gu)||[]))if(!pictureImages.has(pictureKey(ch)))bad.add(ch)}else if(Array.isArray(v))v.forEach(visit);else if(v&&typeof v==='object')Object.values(v).forEach(visit)};visit(LEVELS);return [...bad];}''')
 assert not missing,missing
 page.evaluate("()=>{startLevel(7);startRound(G.level.r.findIndex(r=>r.k==='odd'));}");page.wait_for_timeout(200);page.screenshot(path='/tmp/luko-odd-fixed.png')
 outfits=[{}, {'head':'🎩','neck':'🧣','feet':'👟','back':'🎒','paws':'🧤','hand':'🔦'}, {'head':'👑','eyes':'🕶️','hand':'🪄'}]
 for i,o in enumerate(outfits):
  svg=page.evaluate('(o)=>heroSVG(o)',o)
  q=b.new_page(viewport={'width':420,'height':390});q.set_content('<body style="margin:0;background:#fff5e7;display:grid;place-items:center"><div style="width:410px">'+svg+'</div>');q.screenshot(path=f'/tmp/luko-profile-{i}.png');q.close()
 print('JS errors:',errors);assert not errors
 b.close()
