self.addEventListener('push', event => {
  console.log('[Service Worker] Push Received.');

  let data = {
    title: 'اعلان پیش‌فرض',
    body: 'متنی برای اعلان وجود ندارد'
  };

  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      console.warn('داده پوش JSON نیست، متن ساده استفاده می‌شود:', event.data.text());
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: '/static/images/icon.png',
    badge: '/static/images/icon.png'
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});
