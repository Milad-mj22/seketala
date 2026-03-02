self.addEventListener("push", function(event) {
    const data = event.data.json();
    self.registration.showNotification(data.title, {
        body: data.message,
        icon: "/static/icons/notification-icon.png",
    });
});
