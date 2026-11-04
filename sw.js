// 능선 서비스 워커 (pipeline/app_patch.py): 늘 최신 파일을 먼저, 인터넷이 끊겼을 때만 저장본
const C = 'neungseon-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  const r = e.request; if(r.method !== 'GET') return;
  const u = new URL(r.url); if(u.origin !== location.origin) return;
  e.respondWith(fetch(r).then(res => { if(res.ok && (r.mode === 'navigate' || /\.(png|jpg|webmanifest)$/.test(u.pathname))){ const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); } return res; })
    .catch(() => caches.match(r).then(m => m || Response.error())));
});
