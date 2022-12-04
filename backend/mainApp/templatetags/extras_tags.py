from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='thumbnailize')
def thumbnailize(value):
    """Appends the resize suffix to an image url."""
    try:
        chunks = value.split(".")
        chunks[-2] += "_"+("x".join([str(x) for x in settings.IMG_THUMBNAIL_SIZE]))
        value = ".".join(chunks)
    except:
        # An exception is raised when no valid image name is provided.
        # In a such case, we just ignore (and so return the input value).
        pass
    return value

@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def is_manager(user):
    return user.groups.all().filter(name="Manager").count() > 0

@register.filter
def is_superuser(user):
    return user.is_superuser
