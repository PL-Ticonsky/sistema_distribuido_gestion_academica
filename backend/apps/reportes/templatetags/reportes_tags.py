from django import template

register = template.Library()


@register.filter
def attr(value, name):
    return getattr(value, name, None)
