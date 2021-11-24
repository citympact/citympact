from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import *


# Every time a normal user is created, we want an associated registered user to
# also be created. 
@receiver(post_save, sender=User)
def create_registered_user(sender, instance, created, **kwargs):
    if created:
        p = RegisteredUser.objects.create(user=instance)
        p.save()
