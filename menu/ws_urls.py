from django.urls import re_path,path
from .consumer import MenuWebSocketConsumer


ws_menu_urlpatterns = [
   path('ws/menu_updates/', MenuWebSocketConsumer.as_asgi())
]



