var CACHE_NAME = 'warehouse-cache-v1';
var urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/base.css',
    '/static/css/store.css',
    '/static/js/main.js'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                return response || fetch(event.request);
            })
    );
});
