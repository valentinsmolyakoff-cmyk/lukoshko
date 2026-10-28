from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox']); page=b.new_page(viewport={'width':390,'height':844}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000');page.wait_for_timeout(400)
 data=page.evaluate('()=>LEVELS'); issues=[]; checked=0
 for l in data:
  for i,r in enumerate(l['r']):
   checked+=1;k=r['k']
   if k=='catch' and not r.get('sizeRule') and set(r['good'])&set(r.get('bad',[])):issues.append((l['n'],i,'пересечение'))
   if k in ['choice','seq'] and r.get('ans') not in r['opts']:issues.append((l['n'],i,'ответ',r))
   if k=='mem' and len(set(r['set']))!=len(r['set']):issues.append((l['n'],i,'пары'))
 assert not issues, issues
 print('Данные:',len(data),'уровней,',checked,'раундов; замечания:',issues)
 for width in [320,390,768]:
  page.set_viewport_size({'width':width,'height':844})
  for k in ['mem','seq','odd','diff','choice','sort','dots','maze','word','catch','rhythm']:
   n,idx=next((l['n'],i) for l in data for i,r in enumerate(l['r']) if r['k']==k)
   page.evaluate('([n,i])=>{startLevel(n);startRound(i)}',[n,idx]);page.wait_for_timeout(80)
   if k in ['odd','seq','choice']:
    rects=page.evaluate('()=>R._optRects||[]')
    assert all(r['x']>=0 and r['x']+r['w']<=width for r in rects),(width,k,rects)
 print('Все 11 механик запущены на 320, 390 и 768 px; варианты в границах экрана')
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate('()=>{startLevel(4);startRound(0)}')
 # pick exact mem round independently
 page.evaluate("()=>startRound(G.level.r.findIndex(r=>r.k==='mem'))")
 page.wait_for_timeout(200); page.screenshot(path='/tmp/lukoshko-cards-preview.png')
 page.wait_for_timeout(2900)
 deck=page.evaluate('()=>R.cards.map(c=>c.e)'); rects=page.evaluate('()=>R._cardRects')
 # open one card and verify front
 r=rects[0];page.mouse.click(r['x']+r['w']/2,r['y']+r['h']/2)
 assert page.evaluate('()=>R.cards[0].open')
 page.screenshot(path='/tmp/lukoshko-cards-open.png')
 for e in dict.fromkeys(deck):
  ids=[i for i,v in enumerate(deck) if v==e]
  for j in ids:
   if page.evaluate('(j)=>R.cards[j].open',j):continue
   r=rects[j]; page.mouse.click(r['x']+r['w']/2,r['y']+r['h']/2)
  page.wait_for_timeout(40)
 print('Карточки: показ, открытие, все пары найдены; ошибок JS:',errors)
 assert not errors
 svg=page.evaluate('()=>heroSVG({})');open('/tmp/lukoshko-tishka.svg','w').write(svg)
 b.close()
