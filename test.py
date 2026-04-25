import requests

API_URL = 'https://seketalamanager.ir/data_analysis/api/receive-user/'

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "SECRET123"
}
payload = {
    "name": "علی احمدی",
    "eshterak": "123456789",
    "semat": "مدیر فروش",
    "sematid": "10",
    "phone": "09121234567"
}

response = requests.post(API_URL, json=payload, headers=headers)

print(response.status_code)
print(response.json())