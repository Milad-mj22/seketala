import requests

try:
    response = requests.get("https://updates.push.services.mozilla.com", timeout=10)
    print("Mozilla Push server OK ✅", response.status_code)
except Exception as e:
    print("Mozilla Push server ERROR ❌", e)

try:
    response = requests.get("https://fcm.googleapis.com/fcm/send", timeout=10)
    #print("Google FCM OK ✅", response.status_code)
except Exception as e:
    print("Google FCM ERROR ❌", e)
