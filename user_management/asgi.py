"""
ASGI config for user_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management.settings')

application = get_asgi_application()



import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from menu.ws_urls import ws_menu_urlpatterns
from api.ws_urls import ws_api_urlpatterns
from cameras.ws_urls import ws_camera_urlpatterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_management.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        ws_menu_urlpatterns + ws_api_urlpatterns + ws_camera_urlpatterns # Combine URL patterns from both apps
    ),
})

