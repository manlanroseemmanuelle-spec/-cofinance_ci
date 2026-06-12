const CACHE_NAME = 'cofinance-ci-v4';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) => {
      return Promise.all(names.map((n) => caches.delete(n)));
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  // Ne JAMAIS utiliser le cache - toujours réseau
  event.respondWith(fetch(event.request).catch(() => {
    return new Response('Pas de connexion', { status: 503 });
  }));
});
