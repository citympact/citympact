from django.contrib import admin
from django import forms
from .models import CityProject, CityProjectVote

class DescriptionModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj = None, **kwargs):
        kwargs['widgets'] = {'description': forms.Textarea}
        return super().get_form(request, obj, **kwargs)

admin.site.register(CityProject, DescriptionModelAdmin)
admin.site.register(CityProjectVote)
