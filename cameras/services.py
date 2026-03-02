# cameras/services.py
import cv2
from threading import Thread, Lock
from onvif import ONVIFCamera

from cameras.ai import AiManager

class CameraStream:
    def __init__(self, camera_id, rtsp_url):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.capture = cv2.VideoCapture(rtsp_url)
        self.frame = None
        self.lock = Lock()
        self.running = True
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        self.capture.release()


class CameraManager:
    _instances = {}

    def __init__(self):
        self.ai_modules = AiManager()

    @classmethod
    def get_camera(cls, camera_id, rtsp_url=None):
        if camera_id not in cls._instances:
            if not rtsp_url:
                raise ValueError("RTSP URL required for new camera")
            cls._instances[camera_id] = CameraStream(camera_id, rtsp_url)
        return cls._instances[camera_id]

    @classmethod
    def stop_all(cls):
        for cam in cls._instances.values():
            cam.stop()
