/* Лукошко — service worker.
   Задача: игра открывается даже без интернета (планшет в машине, слабый Wi-Fi в саду).
   При обновлении игры поменяйте номер версии в CACHE — старый кеш удалится сам. */
const CACHE = 'lukoshko-v25';
const FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
  './favicon-32.png',
  './photo.css',
  './photo.js',
  './photo-materials.js',
  './assets/photo/forest-web.jpg',
  './assets/photo/table-web.jpg',
  './assets/photo/house-web.jpg'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(FILES.map(url=>new Request(url,{cache:'reload'})))).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(k=>k.startsWith('lukoshko-')&&k!==CACHE).map(k=>caches.delete(k)));
    await self.clients.claim();
    const scope=new URL('./',self.location.href).pathname;
    const windows=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    await Promise.all(windows.map(async client=>{
      const u=new URL(client.url);
      if(u.origin===self.location.origin&&u.pathname.startsWith(scope)&&u.searchParams.get('build')!=='18'){
        u.searchParams.set('build','18');client.navigate(u.href).catch(()=>{});
      }
    }));
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // страницу всегда пробуем взять свежую, иначе — из кеша
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req).then(r => r || caches.match('./index.html')))
    );
    return;
  }

  // остальное — из кеша, с тихим обновлением в фоне
  e.respondWith(
    caches.match(req).then(hit => {
      const net = fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => hit);
      return hit || net;
    })
  );
});
