from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import PublishedCreatedModel

User = get_user_model()

UPLOAD_DIR = 'posts_pics/'  # А сюда хотим грузить фотки юзеров потом.


class TitleModel(models.Model):
    """Класс абстрактной модели,
    содержит только лишь поле заголовка.
    """
    title = models.CharField(
        blank=False,
        max_length=256,
        verbose_name='Заголовок',
        null=True
    )

    class Meta:
        abstract = True


class Category(PublishedCreatedModel, TitleModel):
    """Класс модели категории публикации,
    унаследован от абстрактов
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
    унаследован от абстракта
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
    унаследован от абстрактов
    класса опубликованной модели и
    класса заголовка.
    """
    text = models.TextField(
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
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
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Картинка',
        upload_to=UPLOAD_DIR,
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title if len(str(self.title)) < 30 \
            else str(self.title)[:30] + '...'


class Comment(models.Model):
    """Класс модели камента.
    Отложенной публикации (как у модели постов) - нет.
    (Поля is_published нет.)
    Публиковать сразу как камент написан.
    """
    text = models.TextField(
        'Комментарий',
        blank=False,
        help_text='Комментарий',
        max_length=150
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации комментария'
    )
