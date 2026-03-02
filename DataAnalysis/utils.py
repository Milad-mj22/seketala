import jdatetime
from datetime import datetime
import re
def jalali_date_time_to_gregorian(jalali_date, time_str):
    """
    jalali_date: '1404-10-12'
    time_str: '14:32:10'
    """
    jy, jm, jd = map(int, jalali_date.split("-"))
    hour, minute = map(int, time_str.split(":"))

    j_date = jdatetime.date(jy, jm, jd)
    g_date = j_date.togregorian()

    return datetime(
        g_date.year,
        g_date.month,
        g_date.day,
        hour,
        minute,
       
    )



import re

def extract_payment_methods(nahveh_text):
    """
    استخراج روش پرداخت از رشته nahveh
    - اگر [] وجود داشته باشد، محتوا داخل براکت برگردد
    - اگر [] نبود، اگر شامل 'نقدي' بود فقط 'نقدي' برگردد
    - در غیر اینصورت کل متن را برگرداند
    """
    if not nahveh_text:
        return set()

    # 1️⃣ اگر براکت وجود داشته باشد
    if '[' in nahveh_text and ']' in nahveh_text:
        matches = re.findall(r'\[\s*(.*?)\s*\]', nahveh_text)
        return set(matches) if matches else set()
    
    # 2️⃣ اگر شامل "نقدي" بود
    elif 'نقدي' in nahveh_text:
        return {'نقدي'}
    
    # 3️⃣ در غیر اینصورت کل متن
    else:
        return {nahveh_text.strip()}



from datetime import datetime, time, timedelta
from django.utils import timezone

from datetime import datetime, time, timedelta
from django.utils import timezone


def get_date_range(selected_date):
    # Start at 03:00 of selected date
    start = datetime.combine(selected_date, time(3, 0))

    # End at 03:00 of next day
    end = start + timedelta(days=1)

    return start, end