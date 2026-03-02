import subprocess
import sys
import threading
import time
from django.apps import AppConfig
from multiprocessing import Process

from manage import celery_process

class SocialappsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SocialApps'



    def ready(self):
        import os
        # if os.environ.get('RUN_MAIN') == 'true':
        #     start_celery()


def start_celery():
    global celery_process
    if celery_process is None:
        #print("🔥 Starting Celery worker in background...")
        celery_process = subprocess.Popen([
            sys.executable,
            "-m", "celery",
            "-A", "celery_app",
            "worker",
            "--loglevel=info",
            "--pool=solo"
        ])
        time.sleep(5)