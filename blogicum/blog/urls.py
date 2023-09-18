# from django.contrib.auth.forms import UserCreationForm
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),

    # путь для просмотра профиля пользователя
    # из шаблона он должен вызываться
    # по ссылке profile/<username>/
    # с одним атрибутом:
    # {% url 'blog:profile' post.author %}
    # ("имя автора")
    path('profile/<slug:username>/',
         views.UserDetailView.as_view(), name='profile'),

    # путь для редактирования профиля пользователя
    # из шаблона он должен вызываться
    # по ссылке (??в задании не задано, сами задаем??)
    # вообще без атрибутов
    # {% url 'blog:edit_profile' %}
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('edit_profile/', views.UserUpdateView.as_view(), name='edit_profile'),

    # путь для создания поста
    # из шаблона он должен вызываться
    # по ссылке posts/create/
    # вообще без аттритбутов
    # {% url 'blog:create_post' %}
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),

    # путь для просмотра поста
    # из шаблона он должен вызываться
    # по ссылке (??в задании не задано, сами задаем??)
    # с одним атрибутом:
    # {% url 'blog:post_detail' post.id %}
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),

    # путь для редактирования поста
    # из шаблона он должен вызываться
    # по ссылке posts/<post_id>/edit/
    # с одним атрибутом:
    # {% url 'blog:edit_post' post.id %}
    # ("номер поста для редактирования")
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),

    # путь для удаления поста
    # из шаблона он должен вызываться
    # по ссылке posts/<post_id>/delete/
    # с одним атрибутом:
    # {% url 'blog:delete_post' post.id %}
    # ("номер поста для удаления")
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),

    # путь для создания комментария к посту
    # из шаблона он должен вызываться
    # по ссылке posts/<post_id>/comment/
    # с одним атрибутом:
    # {% url 'blog:add_comment' post_id %}
    # ("номер поста к которому комментарий")
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/<int:post_pk>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),

    # путь для редактирования комментария к посту
    # из шаблона он должен вызываться
    # по ссылке posts/<post_id>/edit_comment/<comment_id>/
    # с двумя атрибутами:
    # {% url 'blog:edit_comment' comment.post_id comment.id %}
    # ("номер поста к которому комментарий" и "номер самого комментария")
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/<int:post_pk>/edit_comment/<int:comment_pk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),

    # путь для удаления камента к посту
    # из шаблона он должен вызываться
    # по ссылке posts/<post_id>/delete_comment/<comment_id>/
    # с двумя атрибутами:
    # {% url 'blog:delete_comment' post.id comment.id %}
    # ("номер поста к которому комментарий" и "номер самого комментария")
    # (??наверное, надо будет потом запросить - кто залогинен сейчас??)
    path('posts/<int:post_pk>/delete_comment/<int:comment_pk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

]
