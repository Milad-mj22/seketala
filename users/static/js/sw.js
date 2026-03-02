// static/js/sw.js یا static/sw.js بسته به مسیرت

self.addEventListener('install', (event) => {
    console.log('SW v3: installed');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('SW v3: activated');
});
self.addEventListener('push', (event) => {
    console.log('SW v3: push event received');

    let title = 'اعلان جدید';
    let body = '';

    if (event.data) {
        const raw = event.data.text();
        console.log('SW v3: raw push payload =', raw);

        try {
            const json = JSON.parse(raw);
            title = json.title || title;
            body = json.body || body;
            console.log('SW v3: parsed JSON payload', json);
        } catch (e) {
            console.log('SW v3: payload is plain text, not JSON');
            body = raw;
        }
    }

    const options = {
        body: body,
        icon: '/static/images/icon.png',
    };

    event.waitUntil(
        (async () => {
            console.log('SW v3: calling showNotification with:', { title, body });
            await self.registration.showNotification(title, options);
            console.log('SW v3: showNotification resolved');
        })()
    );
});
