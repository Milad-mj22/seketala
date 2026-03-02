import jdatetime
from django.utils import timezone


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