from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},service_workers='block');calls=[];errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  def mock(route):
   body=route.request.post_data_json;calls.append(body)
   scope=body.get('scope','parent');text=('На уровне '+str(body['level']['number'])+' получилось действовать внимательно. Попробуйте ещё раз найти все пары, открывая карточки не спеша.' if scope=='level' else 'В играх на память ребёнок уверенно находит пары. Предложите разложить знакомые предметы по группам, а потом снова пройти задание с карточками.')
   route.fulfill(status=200,content_type='application/json',body=json.dumps({'text':text,'scope':scope,'source':'ai','cached':False}))
  page.route('**/api/advice',mock);page.goto('http://127.0.0.1:8000',wait_until='networkidle');page.evaluate('()=>picturesReady');page.wait_for_timeout(400);assert not calls
  # Exercise actual wrong/correct quiz handlers; soft mistakes must reach AI facts.
  page.evaluate("""()=>{save.sound=false;const lv=LEVELS.find(l=>l.r.some(r=>r.k==='odd'));startLevel(lv.n);startRound(G.level.r.findIndex(r=>r.k==='odd'));R0.t0=performance.now()-5000;drawRound();const sp=R.spec;const bad=R._optRects.find(r=>r.v!==sp.items[sp.ans]),good=R._optRects.find(r=>r.v===sp.items[sp.ans]);const click=r=>handleQuizClick({x:r.x+r.w/2,y:r.y+r.h/2});click(bad);click(good);logRound();logRound();showResult(2,true);}""")
  summary=page.evaluate('()=>G.aiLevelSummary');assert summary['errors']==1 and len(summary['rounds'])==1,summary
  page.locator('#btnAiLevel').click();page.wait_for_function("()=>document.getElementById('resAi').textContent.startsWith('На уровне')");assert len(calls)==1 and calls[0]['scope']=='level';assert calls[0]['level']==summary
  page.locator('#btnAiLevel').click();page.wait_for_timeout(150);assert calls[-1]['refresh'] is True
  page.evaluate('()=>loadParentAdvice(false)');page.wait_for_timeout(150);assert calls[-1]['scope']=='parent';assert page.locator('#aiOut').inner_text()!=page.locator('#resAi').inner_text();assert calls[-1]['recent'][-1]['errs']==1
  page.evaluate('()=>{startLevel(29);showResult(1,false);}');page.locator('#btnAiLevel').click();page.wait_for_timeout(150);assert calls[-1]['level']['number']==29 and calls[-1]['level']['completed'] is False;assert not calls[-1]['refresh'];assert calls[-1]['level']['attempt']!=summary['attempt']
  assert not errors,errors
  print(engine,'PASS: distinct level/parent requests; actual attempt data; explicit refresh; new attempt isolated; round logging deduplicated')
  b.close()
