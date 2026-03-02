from django import template

register = template.Library()

@register.filter
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def get_item(d, key):
    try:
        return d.get(key)
    except Exception:
        return None