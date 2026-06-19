from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True, label='Полное имя')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    email = forms.EmailField(required=True, label='Email')
    address = forms.CharField(required=False, label='Адрес', widget=forms.Textarea(attrs={'rows': 2}))
    city = forms.CharField(max_length=100, required=False, label='Город')
    postal_code = forms.CharField(max_length=20, required=False, label='Индекс')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if not hasattr(user, 'profile'):
                Profile.objects.create(
                    user=user,
                    full_name=self.cleaned_data.get('full_name', ''),
                    phone=self.cleaned_data.get('phone', ''),
                    address=self.cleaned_data.get('address', ''),
                    city=self.cleaned_data.get('city', ''),
                    postal_code=self.cleaned_data.get('postal_code', '')
                )
            else:
                profile = user.profile
                profile.full_name = self.cleaned_data.get('full_name', '')
                profile.phone = self.cleaned_data.get('phone', '')
                profile.address = self.cleaned_data.get('address', '')
                profile.city = self.cleaned_data.get('city', '')
                profile.postal_code = self.cleaned_data.get('postal_code', '')
                profile.save()
        return user