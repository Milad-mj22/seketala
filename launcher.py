import os
import sys
import uuid
import wmi
import django
from django.core.management import call_command

# ======================
# بخش امنیت - قفل روی فلش USB خاص
# ======================
ALLOWED_USB_SERIAL = "027802854070"  # مقدار سریال فلش خودت اینجا بذار
ALLOWED_MAC = "dc:f5:05:72:e6:80"



def check_usb_key():
    try:
        c = wmi.WMI()
        for disk in c.Win32_DiskDrive():
            if 'USB' in disk.InterfaceType:
                serial = disk.SerialNumber.strip()
                if serial == ALLOWED_USB_SERIAL:
                    return True
        return False
    except:
        return False

def get_mac():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                   for ele in range(0,8*6,8)][::-1])
    return mac.lower()



if get_mac() != ALLOWED_MAC.lower():
    #print("❌ این برنامه فقط روی یک سیستم مجاز اجرا می‌شود.")
    sys.exit()

if not check_usb_key():
    #print("❌ لطفاً فلش مجاز را وصل کنید.")
    sys.exit()







# ======================
# تنظیم Django
# ======================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_management.settings")  # ← اسم پروژه Django

django.setup()

# اجرای migration و static
call_command("migrate")
call_command("collectstatic", interactive=False)

# اجرای سرور Django
call_command("runserver", "0.0.0.0:8000")
