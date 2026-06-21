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
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'Ismingiz'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'Familiyangiz'}))
    city = forms.ChoiceField(choices=Profile.REGION_CHOICES, widget=forms.Select())

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone', 'city', 'bio', 'avatar', 'telegram', 'whatsapp']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67 (Masalan)'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Masalan: Men 5 yillik tajribaga ega ustaman...'}),
            'avatar': forms.FileInput(),
            'telegram': forms.TextInput(attrs={'placeholder': '@username (Masalan)'}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67 (Masalan)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile.save()
        return profile