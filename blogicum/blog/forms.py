from django import forms
from .models import UserUpdate


class UserUpdateForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = UserUpdate
        # Указываем, что надо отобразить все поля.
        fields = '__all__'
