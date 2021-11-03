from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='thumbnailize')
def thumbnailize(value):
    """Appends the resize suffix to an image url."""
    print("thumbnailize:", value, settings.IMG_THUMBNAIL_SIZE)
    try:
        chunks = value.split(".")
        chunks[-2] += "_"+("x".join([str(x) for x in settings.IMG_THUMBNAIL_SIZE]))
        value = ".".join(chunks)
        print(" - value=", value)
    except:
        # An exception is raised when no valid image name is provided.
        # In a such case, we just ignore (and so return the input value).
        pass
    return value
