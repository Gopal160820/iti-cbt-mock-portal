from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allows looking up a value in a dict using a variable key."""
    return dictionary.get(key)

@register.filter
def get_attribute(obj, attr_name):
    """Allows accessing an object attribute dynamically."""
    return getattr(obj, attr_name, "")