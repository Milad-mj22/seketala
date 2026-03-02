
from pywebpush import webpush, WebPushException
from django.conf import settings
from ..models import Profile

def send_push_notification(user, message):
    try:
        profile = Profile.objects.get(user=user)

        if not profile.push_endpoint:
            #print(f"User {user.username} has no push subscription.")
            return

        webpush(
            subscription_info={
                "endpoint": profile.push_endpoint,
                "keys": {
                    "p256dh": profile.push_p256dh,
                    "auth": profile.push_auth
                },
            },
            data=message,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=settings.VAPID_CLAIMS
        )
        #print(f"Notification sent to {user.username}")
    except WebPushException as ex:
        print(f"Error sending push notification to {user.username}: {ex}")