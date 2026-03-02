

import sys
import os

# تنظیم مسیر پروژه
sys.path.insert(0, '/home/seketal1/Seketala_Kitchen_Flow/passenger_wsgi.py')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
