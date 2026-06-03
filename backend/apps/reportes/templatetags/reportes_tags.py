from django import template

register = template.Library()


@register.filter
def attr(value, name):
    return getattr(value, name, None)


@register.filter
def item(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)
