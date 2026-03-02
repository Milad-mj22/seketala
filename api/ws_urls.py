from django.urls import re_path,path
from .consumer import APIWebSocketConsumer


ws_api_urlpatterns = [
   path('ws/api_updates/', APIWebSocketConsumer.as_asgi())
]



