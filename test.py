import requests

url = "http://192.168.1.107:8200/data_analysis/api/receive-user/"
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

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())