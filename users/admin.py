from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Список полей в таблице всех пользователей
    list_display = ['email', 'username', 'is_staff']

    # Поля, которые видны при СОЗДАНИИ нового пользователя
    # МЫ УБРАЛИ ОТСЮДА 'usable_password', который вызывал ошибку
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password'),
        }),
    )

    # Поля, которые видны при РЕДАКТИРОВАНИИ существующего пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

# Важно: если CustomUser уже зарегистрирован, сначала разрегистрируйте его или просто используйте этот код:
admin.site.unregister(CustomUser) if admin.site.is_registered(CustomUser) else None
admin.site.register(CustomUser, CustomUserAdmin)