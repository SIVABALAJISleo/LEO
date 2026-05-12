const CACHE_NAME = 'hyper-cache-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/src/main.tsx',
    '/src/index.css',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
