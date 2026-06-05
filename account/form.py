
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm


class RegisterForm(UserCreationForm):

    ROLE_CHOICES = (

    ('client', 'Client'),
    ('builder', 'Builder'),

    )

    role = forms.ChoiceField( choices=ROLE_CHOICES,widget=forms.Select(), )

    class Meta:
        model = User
        fields = (

            'username',
            'role',
            'first_name',
            'last_name',

        )

        widgets = {

            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            **self.cleaned_data,
        )

        return user



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
