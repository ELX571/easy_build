
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from accounts.models import Profile


class RegisterForm(UserCreationForm):
    # avatar = forms.ImageField(required=False)

    ROLE_CHOICES = (

    ('client', 'Client'),
    ('builder', 'Builder'),

    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select())

    class Meta:
        model = User
        fields = (
            'role',
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',

        )

        widgets = {

            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def save(self, commit=True):
        role = self.cleaned_data.pop('role')
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()
            from accounts.models import Role

            Role.objects.update_or_create(user=user, defaults={'role': role})

        return user

class SecondRegisterForm(ModelForm):

    class Meta:
        model = Profile
        fields = (
            'username',
            'bio',
            'avatar',
        )



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


