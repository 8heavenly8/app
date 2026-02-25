from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.validators import UnicodeUsernameValidator # Добавьте этот импорт
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        validators=[UnicodeUsernameValidator()],
        help_text="Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_",
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")