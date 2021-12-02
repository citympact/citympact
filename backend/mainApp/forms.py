from django import forms
from django.contrib.auth.models import User
from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}))

    first_name = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class RegisteredUserForm(forms.ModelForm):
    zip_code = forms.DecimalField(max_digits=10, decimal_places=0)
    zip_code.widget.attrs.update({"class": "form-control"})
    city = forms.CharField(max_length=254)
    city.widget.attrs.update({"class": "form-control"})
    birth_year = forms.DecimalField(max_digits=10, decimal_places=0)
    birth_year.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = RegisteredUser
        fields = ["zip_code", "city", "birth_year"]

class NewUserForm(UserForm):

    password1 = forms.CharField(label='mot de passe',
        widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={"class": "form-control"}))


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Le mot de passe ne correspond pas à sa confirmation.")
        return password2

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username"]
