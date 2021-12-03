from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom d'utilisateur")
    email = forms.EmailField(required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="E-Mail")

    first_name = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Prénom")
    last_name = forms.CharField(max_length=100,
        required=True, widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom de famille")
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

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Mot de passe")
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmation du mot de passe")


    MIN_PASSWORD_LENGTH = 8

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        exisitngUser = User.objects.filter(email=email)
        if exisitngUser.count() > 0:
            raise ValidationError("Le compte e-mail fourni correspond déjà à " \
                + "un compte.", "email_exists")
        return email

    def clean_password1(self):
        """
        Simple validation of the password, to make sure:
         - the length is greater than 8,
         - there is at least one digit
         - there is at least one letter
        """

        password1 = self.cleaned_data.get("password1")
        if len(password1) < NewUserForm.MIN_PASSWORD_LENGTH:
            raise ValidationError("Le mot de passse doit contenir au moins " \
                + "%d caractères" % NewUserForm.MIN_PASSWORD_LENGTH)

        if not any(c.isdigit() for c in password1):
            raise ValidationError("Le mot de passe doit contenir au moins " \
                + "un chiffre.")

        if not any(c.isalpha() for c in password1):
            raise ValidationError("Le mot de passe doit contenir au moins " \
                + "une lettre.")

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
        user.save()

        link = "activate.html"

        body = "<p>Bonjour %s %s,<br>" % (user.first_name, user.last_name) \
            + "Merci de <a href=\"%s\">valider votre compte</a></p>" % link \
            + "<p><small>Si votre navigateur n'affiche pas le liens, " \
            + "vous pouvez copier le lien suivant dans la barre d'adresse de " \
            + "votre navigateur WEB:<br>%s</small></p>" % link

        email = EmailMessage(
            'Confirmation de compte',
            body,
            MAIL_FROM_EMAIL,
            [user.email],
            [], # No BCC
            )
        return user

    class Meta:
        model = User
        fields = ["username"]
