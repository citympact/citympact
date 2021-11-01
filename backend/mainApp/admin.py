from django.contrib import admin

# Register your models here.
from .models import CityProject, CityProjectVote

admin.site.register(CityProject)
admin.site.register(CityProjectVote)
