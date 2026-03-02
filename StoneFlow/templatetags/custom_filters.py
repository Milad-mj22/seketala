from django import template

from StoneFlow.models import Step
from jalali_date import datetime2jalali
from datetime import date, datetime


register = template.Library()


@register.filter
def split_license(plate):
    if not plate:
        return ['--', '--', '---', '--']

    if isinstance(plate, list):
        # اگر لیست است (مثلاً هنگام نمایش فرم با خطا)، همان لیست را برگردان
        return plate

    try:
        parts = plate.split('-')
        if len(parts) == 4:
            return parts
    except Exception:
        pass

    return ['--', '--', '---', '--']




@register.filter
def split(value, delimiter=','):
    if not value:
        return []
    # اگر بخوای فقط یک جداکننده باشه (مثلاً کامای فارسی)
    if delimiter == ',':
        # جدا کردن هم با کامای انگلیسی و هم فارسی
        import re
        return [item.strip() for item in re.split(r'[،,]', value)]
    else:
        return [item.strip() for item in value.split(delimiter)]



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter
def get_next_step(steps, current_order):
    try:
        if current_order =='':
            current_order =1
        current_order = int(current_order.order)
        current_order+=1
        # next_steps = steps.filter(order__gt=current_order).order_by('order')
        next_steps = Step.objects.filter(order = current_order)
        if next_steps.exists():
            return next_steps.first()
        return None
        # return next_steps.first() if next_steps.exists() else None
    except:
        return None
    



@register.filter
def to_jalali(value):
    if isinstance(value, str):
        try:
            # تلاش برای تبدیل رشته به datetime
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return ''  # اگر فرمت اشتباه بود، برگرد رشته خالی

    if isinstance(value, (datetime, date)):
        return datetime2jalali(value).strftime('%Y/%m/%d')
    
    return ''



@register.filter
def get_item(d, key):
    try:
        return d.get(key)
    except Exception:
        return None
    

@register.filter
def sum_total(table_data):
    return sum(total for _, total in table_data)