from django import forms
from django.contrib.auth.models import User
from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email']

class RegisteredUserForm(forms.ModelForm):
    zip_code = forms.DecimalField(max_digits=10, decimal_places=0)
    zip_code.widget.attrs.update({'class': 'form-control'})
    city = forms.CharField(max_length=254)
    city.widget.attrs.update({'class': 'form-control'})
    birth_year = forms.DecimalField(max_digits=10, decimal_places=0)
    birth_year.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = RegisteredUser
        fields = ['zip_code', 'city', 'birth_year']
