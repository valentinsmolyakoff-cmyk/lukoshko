from pathlib import Path
from playwright.sync_api import sync_playwright
old=Path(__file__).resolve().parents[1]/'test-old-worker13.js'
old.write_text("self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));")
try:
 with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context();page=c.new_page();page.route('https://lukoshko-ai.vercel.app/api/advice',lambda r:r.abort())
  url='http://127.0.0.1:8000/'
  page.route(url,lambda r:r.fulfill(content_type='text/html',body='<html><body>Old installed game</body></html>'))
  page.goto(url);page.evaluate('async()=>{await navigator.serviceWorker.register("test-old-worker13.js");await navigator.serviceWorker.ready;localStorage.setItem("update-progress-test","keep")}');page.wait_for_function('()=>!!navigator.serviceWorker.controller')
  page.unroute(url)
  page.evaluate('async()=>{await navigator.serviceWorker.register("sw.js",{updateViaCache:"none"})}')
  page.wait_for_url('**build=23',timeout=30000);page.evaluate('()=>picturesReady')
  assert page.evaluate('()=>assetsLoaded');assert page.evaluate('()=>localStorage.getItem("update-progress-test")')=='keep'
  page.wait_for_function("async()=>{const c=await caches.open('lukoshko-v23');return !!(await c.match('./index.html'))}")
  c.set_offline(True);page.reload(wait_until='domcontentloaded');page.evaluate('()=>picturesReady');assert page.evaluate('()=>assetsLoaded')
  page.evaluate('()=>{save.sound=false;startLevel(7);startRound(G.level.r.findIndex(r=>r.k==="odd"))}')
  assert page.evaluate('()=>R.spec.k')=='odd'
  print('PASS old installed app auto-updated; progress retained; 281 PNGs + 24 hero layers available offline')
  b.close()
finally:old.unlink(missing_ok=True)
