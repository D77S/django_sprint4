from django import forms

from .models import Comment, UserUpdate


class UserUpdateForm(forms.ModelForm):
    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = UserUpdate
        # Указываем, что надо отобразить все поля.
        fields = '__all__'


class CommentForm(forms.ModelForm):
    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Comment
        # Указываем, что надо отобразить все поля.
        fields = ('text',)
