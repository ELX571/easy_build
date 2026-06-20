from django import forms
from django.contrib.auth.models import User
from accounts.models import Profile


class RegisterForm(forms.Form):
    ROLE_CHOICES = (
        ('client', 'Buyurtmachi (Mijoz)'),
        ('builder', 'Quruvchi (Usta)'),
    )

    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ismingiz'})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Familiyangiz'})
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Foydalanuvchi nomi'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Email (ixtiyoriy)'})
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Parol (kamida 6 belgi)'})
    )
    re_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parolni takrorlang'})
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select())

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu username allaqachon band!")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('re_password')
        if p1 and p2 and p1 != p2:
            self.add_error('re_password', "Parollar mos emas!")
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Foydalanuvchi nomi'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parol'})
    )


class ProfileEditForm(forms.ModelForm):
    city = forms.ChoiceField(choices=Profile.REGION_CHOICES, widget=forms.Select())

    class Meta:
        model = Profile
        fields = ['phone', 'city', 'bio', 'avatar', 'telegram', 'whatsapp']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'O\'zingiz haqingizda...'}),
            'avatar': forms.FileInput(),
            'telegram': forms.TextInput(attrs={'placeholder': '@username'}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}),
        }