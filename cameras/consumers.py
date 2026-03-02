import cv2
import base64
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from vidgear.gears import CamGear

from cameras.models import Camera
from channels.db import database_sync_to_async
# cameras/consumers.py
import base64
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from cameras.services import CameraManager
from channels.db import database_sync_to_async

class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        camera_obj = await  self.get_camera(int(self.camera_id))
        self.camera = CameraManager.get_camera(self.camera_id,rtsp_url=camera_obj.get_live_feed_url())
        await self.accept()
        await self.stream_video()

    async def stream_video(self):
        while True:
            frame = self.camera.get_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                await self.send(base64.b64encode(buffer).decode('utf-8'))
            await asyncio.sleep(0.04)  # ~25 FPS

    @database_sync_to_async
    def get_camera(self, camera_id):
        return Camera.objects.get(id=camera_id)
