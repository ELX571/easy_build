from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile

# 1. BIRINCHI BOSQICH FORMASI: Ro'yxatdan o'tish va Rol tanlash
class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('client', 'Buyurtmachi (Mijoz)'),
        ('builder', 'Quruvchi (Usta)'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ismingiz'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Familiyangiz'}),
        }

    def save(self, commit=True):
        role = self.cleaned_data.pop('role')
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')

        if commit:
            user.save()
            # Yangilangan Profile modeliga rolni yozamiz
            Profile.objects.update_or_create(
                user=user,
                defaults={'role': role}
            )
        return user


# 2. IKKINCHI BOSQICH FORMASI: Profilni to'ldirish (Xatoliksiz toza versiya)
class SecondRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'phone',
            'city',
            'avatar',
        )
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998901234567'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: Toshkent, Samarqand'}),
        }


# 3. TIZIMGA KIRISH FORMASI
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Foydalanuvchi nomi'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'}))

# accounts/forms.py (yoki profilingiz formasi qayerda bo'lsa o'sha fayl):


# accounts/forms.py

# accounts/forms.py

# accounts/forms.py
# accounts/forms.py
from django import forms
from .models import Profile

class ProfileEditForm(forms.ModelForm):
    # Bu yerda biz explicitly (aniq) qilib select qilyapmiz
    city = forms.ChoiceField(
        choices=Profile.REGION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Profile
        fields = ['phone', 'city', 'bio', 'avatar']
        # Qolgan maydonlar uchun widgetlar
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'avatar': forms.FileInput(),
            'phone': forms.TextInput(),
        }