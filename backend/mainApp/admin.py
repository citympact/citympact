from django.contrib import admin
from django import forms
from .models import *

class DescriptionModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj = None, **kwargs):
        kwargs['widgets'] = {
            'summary': forms.Textarea,
            'description': forms.Textarea,
        }
        return super().get_form(request, obj, **kwargs)

admin.site.register(CityProject, DescriptionModelAdmin)
admin.site.register(CityProjectVote)
admin.site.register(CityProjectComment)
admin.site.register(CityProjectQuestion)
admin.site.register(CityProjectAnswer)

admin.site.register(Proposition)
admin.site.register(PropositionSignature)
admin.site.register(PropositionComment)

admin.site.register(RegisteredUser)
