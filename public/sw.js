const CACHE_NAME = 'academic-tool-v4';
const STATIC_ASSETS = [
  '/favicon.svg'
];

// Install: Cache essential shell assets
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).catch(() => {})
  );
});

// Activate: Purge all stale versioned caches immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('Purging outdated service worker cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim()).catch(() => {})
  );
});

// Fetch: Strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests and API/Tunnel/Auth calls
  if (request.method !== 'GET' || url.pathname.startsWith('/api') || url.pathname.includes('/auth/') || url.hostname.includes('trycloudflare.com')) {
    return;
  }

  // 1. Navigation requests: ALWAYS Network-First to guarantee latest bundle index.html
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match('/index.html').then((cached) => cached || fetch(request).catch(() => new Response('Offline', { status: 503 })));
      })
    );
    return;
  }

  // 2. Static Assets: Network-first with cache fallback
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone)).catch(() => {});
          }
          return networkResponse;
        })
        .catch(() => caches.match(request).then((cached) => cached || new Response('', { status: 404 })))
    );
    return;
  }

  // Default passthrough
  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request).catch(() => new Response('', { status: 404 })))
  );
});
