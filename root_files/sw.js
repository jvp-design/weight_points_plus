const staticCacheName = 'site-static-v1';
const dynamicCacheName = 'site-dynamic-v2';
const assets = [
    '/',
    '/static/js/app.js',
    '/static/js/nav.js',
    '/static/js/toggle-visibility.js',
    '/static/css/dist/styles.css',
    '/static/css/nav.css',
    '/static/images/favicons/favicon.ico',
    '/static/images/farmers_market/Color/Farmers%20Market-color.svg',
    '/static/images/logo.svg',
    'https://fonts.googleapis.com/css2?family=Poppins&display=swap',
    'https://fonts.gstatic.com/s/poppins/v19/pxiEyp8kv8JHgFVrJJfecg.woff2',
    'https://unpkg.com/alpinejs@3.9.5/dist/cdn.min.js',
    // '/pages/fallback.html'
];


// install event
self.addEventListener('install', evt => {
    //console.log('service worker installed');
    evt.waitUntil(
        caches.open(staticCacheName).then((cache) => {
            console.log('caching shell assets');
            cache.addAll(assets);
        })
    );
});

// activate event
self.addEventListener('activate', evt => {
    //console.log('service worker activated');
    evt.waitUntil(
        caches.keys().then(keys => {
            //console.log(keys);
            return Promise.all(keys
                .filter(key => key !== staticCacheName)
                .map(key => caches.delete(key))
            );
        })
    );
});

// fetch event
self.addEventListener('fetch', evt => {
    //console.log('fetch event', evt);
    evt.respondWith(
        caches.match(evt.request).then(cacheRes => {
            return cacheRes || fetch(evt.request);
        }).catch(() => {
            if(evt.request.url.indexOf('.html') > -1){
                return caches.match('/fallback.html');
            }
        })
    );
});
