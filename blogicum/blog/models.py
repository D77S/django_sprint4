from core.models import PublishedCreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TitleModel(models.Model):
    """Класс абстрактной модели,
    содержит только лишь поле заголовка.
    """
    title = models.CharField(
        blank=False,
        max_length=256,
        default='Empty',
        verbose_name='Заголовок',
        null=True
    )

    class Meta:
        abstract = True


class Category(PublishedCreatedModel, TitleModel):
    """Класс модели категории публикации,
    унаследован(-а) от абстрактов
    класса опубликованной модели и
    класса заголовка.
    """
    description = models.TextField(
        blank=False,
        default='Empty',
        verbose_name='Описание'
    )
    slug = models.SlugField(
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title if len(str(self.title)) < 30 \
            else str(self.title)[:30] + '...'


class Location(PublishedCreatedModel):
    """Класс модели локации публикации,
    унаследован(-а) от абстракта
    класса опубликованной модели.
    """
    name = models.CharField(
        blank=False,
        default='Empty',
        verbose_name='Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name if len(str(self.name)) < 30 \
            else str(self.name)[:30] + '...'


class Post(PublishedCreatedModel, TitleModel):
    """Класс модели поста (постов),
    унаследован(-а) от абстрактов
    класса опубликованной модели и
    класса заголовка.
    """
    text = models.TextField(
        blank=False,
        default='Empty',
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=False,
        auto_now_add=False,
        auto_now=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title if len(str(self.title)) < 30 \
            else str(self.title)[:30] + '...'


class Comment(models.Model):
    comment = models.CharField(
        'Комментарий',
        blank=False,
        help_text='Комментарий',
        max_length=150
        )


class UserUpdate(models.Model):
    """Класс модели для генерации формы
    для страницы редактирования профиля юзера.
    Ему будет разрешено редактировать:
    - имя,
    - фамилию,
    - логин,
    - емейл.
    """
    first_name = models.CharField(
        'Имя',
        blank=False,
        help_text='Обязательное поле. Не более 150 символов.',
        max_length=150
        )
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        help_text='Необязательное поле. Не более 150 символов.',
        max_length=150
        )
    login = models.CharField(
        'Login',
        blank=False,
        help_text='Обязательное поле. Не более 150 символов.',
        max_length=150
        )
    email = models.EmailField(
        'Email',
        blank=False,
        help_text='Обязательное поле. Не более 150 символов.',
        max_length=150
        )
