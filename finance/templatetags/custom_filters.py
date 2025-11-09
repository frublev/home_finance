from django import template

register = template.Library()

@register.filter
def intspace(value):
    try:
        return f"{float(value):,.2f}".replace(',', ' ')
    except (ValueError, TypeError):
        return value
