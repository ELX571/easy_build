
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm


class RegisterForm(UserCreationForm):
    # avatar = forms.ImageField(required=False)

    ROLE_CHOICES = (

    ('client', 'Client'),
    ('builder', 'Builder'),

    )

    role = forms.ChoiceField( choices=ROLE_CHOICES,widget=forms.Select(), )

    class Meta:
        model = User
        fields = (
            'role',
            'first_name',
            'last_name',

        )

        widgets = {

            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            **self.cleaned_data,
        )

        return user

class SecondRegisterForm(ModelForm):
    avatar = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = (
            'username',
        )



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')



