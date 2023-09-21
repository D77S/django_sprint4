from django import forms
from django.contrib.auth.forms import UserChangeForm

from blog.models import Comment, Post, User


# Создаем объекта модели юзеров.
# Как и рекомендуется, запрашиваем его вот такой функцией
# на случай, если вдруг переопределялась стандартная.
# User = get_user_model()


class UserUpdateForm(UserChangeForm):
    """
    Форма для апдейта профайла юзера.
    Ему разрешено апдейтить только:
    фамилию, имя, username, email."""
    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email',
                  )


class CommentForm(forms.ModelForm):
    """
    Форма для вставки камента.
    Только сам камент, и всё.
    Логин коментатора потом подтянем автоматически."""
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """
    Форма для вставки поста.
    Почти все поля, кроме автора.
    (Его потом подтянем автоматически.)"""
    class Meta:
        model = Post
        fields = ('title',
                  'text',
                  'image',
                  'location',
                  'category',
                  'pub_date',
                  )
