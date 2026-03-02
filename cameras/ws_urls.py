from django.urls import re_path
from . import consumers

ws_camera_urlpatterns = [
    re_path(r'ws/camera/(?P<camera_id>\d+)/$', consumers.CameraConsumer.as_asgi()),
]