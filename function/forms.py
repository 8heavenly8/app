from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True, label='Полное имя')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    address = forms.CharField(required=False, label='Адрес', widget=forms.Textarea(attrs={'rows': 2}))
    city = forms.CharField(max_length=100, required=False, label='Город')
    postal_code = forms.CharField(max_length=20, required=False, label='Индекс')
    email = forms.EmailField(required=True, label='Email')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=True)
        profile = user.profile
        profile.full_name = self.cleaned_data['full_name']
        profile.phone = self.cleaned_data['phone']
        profile.address = self.cleaned_data['address']
        profile.city = self.cleaned_data['city']
        profile.postal_code = self.cleaned_data['postal_code']
        profile.save()
        return user