import jdatetime
from django.utils import timezone
from datetime import timedelta  # اضافه کردن این خط برای استفاده از timedelta


def format_jalali_datetime(dt):
    """
    Convert a timezone-aware datetime to Jalali string:
    1404/11/15 12:00:00 ق.ظ
    """
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    dt = timezone.localtime(dt)

    jdt = jdatetime.datetime.fromgregorian(datetime=dt)



    am_pm = "ق.ظ" if jdt.hour < 12 else "ب.ظ"

    return f"{jdt:%Y/%m/%d %H:%M:%S} {am_pm}"



def havale_format_jalali_datetime(dt):
    """
    Convert a timezone-aware datetime to Jalali string:
    1404/11/15 12:00:00 ق.ظ
    """
    temp  = dt
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    dt = timezone.localtime(dt)
    
    if (dt.hour>=23 and dt.minute>=47) :
        dt = dt + timedelta(days=2)  # افزودن یک روز به تاریخ
    else:
        dt = dt + timedelta(days=1)  # افزودن یک روز به تاریخ
        
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)



    am_pm = "ق.ظ" if jdt.hour < 12 else "ب.ظ"

    return f"{jdt:%Y/%m/%d}"



def format_jalali_date(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    dt = timezone.localtime(dt)

    jdt = jdatetime.datetime.fromgregorian(datetime=dt)

    am_pm = "ق.ظ" if jdt.hour < 12 else "ب.ظ"

    return f"{jdt:%Y/%m/%d}"

