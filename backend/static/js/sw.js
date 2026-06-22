self.addEventListener('push', function(event) {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Todom';
  const options = { body: data.body || '', data: data.data || {} };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = '/';
  event.waitUntil(clients.openWindow(url));
});
