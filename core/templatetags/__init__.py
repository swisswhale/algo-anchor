from django import template

register = template.Library()

@register.filter
def mul(value, multiplier):
    """
    Multiplies the value by the given multiplier.
    Usage: {{ value|mul:100 }}
    """
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return value
