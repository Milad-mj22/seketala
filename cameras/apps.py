from django.apps import AppConfig



# apps.py
from django.apps import AppConfig
from cameras.services import CameraManager

class CamerasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cameras'

    def ready(self):
        from django.conf import settings
        try:
            from cameras.models import Camera

            cameras = Camera.objects.all()
            for cam in cameras:
                CameraManager.get_camera(str(cam.id), cam.get_live_feed_url())
        except Exception as e:
            #print(e)
            pass  # migrations stage, DB not ready

