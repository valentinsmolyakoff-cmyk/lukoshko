from playwright.sync_api import sync_playwright
import json
TEXT='Ребёнок уверенно находит одинаковые картинки. Сейчас стоит потренировать узнавание букв: попробуйте вместе искать первую букву имени на упаковках и вывесках. Для начала достаточно пяти минут спокойной игры.'
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},service_workers='block');calls=[]
  def answer(r):
   payload=json.loads(r.request.post_data);calls.append(payload)
   r.fulfill(status=200,content_type='application/json',body=json.dumps({'text':TEXT,'source':'ai','cached':False,'generatedAt':'2026-10-28T12:00:00Z','requestId':str(len(calls))}))
  page.route('https://lukoshko-ai.vercel.app/api/advice',answer)
  page.goto('http://127.0.0.1:8000/',wait_until='domcontentloaded');page.evaluate('()=>picturesReady');assert not calls
  page.locator('#btnParent').click();page.locator('#lockInput').fill(str(page.evaluate('()=>lockAnswer')));page.locator('#btnLockOk').click()
  page.wait_for_function("()=>document.getElementById('aiNote').textContent.includes('новый ответ')")
  assert len(calls)==1 and calls[-1]['refresh'] is False
  page.evaluate('()=>loadParentAdvice(false)');assert len(calls)==1
  page.evaluate('()=>{save.skills.memory={ok:10,miss:2};return loadParentAdvice(false)}');assert len(calls)==2
  page.locator('#btnAiRefresh').click();page.wait_for_function("()=>!document.getElementById('btnAiRefresh').disabled")
  assert len(calls)==3 and calls[-1]['refresh'] is True
  assert 'Gemini' not in page.locator('#scrParent').inner_text()
  page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.fulfill(status=429,content_type='application/json',body='{"error":"rate_limit"}'))
  page.evaluate('()=>loadParentAdvice(true)');assert 'лимит новых запросов' in page.locator('#aiOut').inner_text();assert TEXT in page.locator('#aiNote').inner_text()
  page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.fulfill(status=502,content_type='application/json',body='{"error":"provider_unavailable","upstreamStatus":503}'))
  page.evaluate('()=>loadParentAdvice(true)');assert 'перегружен' in page.locator('#aiOut').inner_text()
  print(engine,'PASS: login only; same data dedup; changed data refresh; explicit fresh generation; specific errors; old AI preserved')
  b.close()
