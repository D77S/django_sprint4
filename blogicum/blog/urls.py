from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('category/<slug:category_slug>/',
         views.CategoryView.as_view(), name='category_posts'),

    # Путь для просмотра профиля пользователя.
    # Из шаблона он должен вызываться
    # по ссылке profile/<username>/
    # с одним атрибутом: {% url 'blog:profile' post.author %} ("имя автора").
    path('profile/<slug:username>/',
         views.UserDetailView.as_view(), name='profile'),

    # Путь для редактирования профиля пользователя.
    # Из шаблона он должен вызываться
    # по ссылке edit_profile/
    # вообще без атрибутов: {% url 'blog:edit_profile' %}.
    path('edit_profile/', views.UserUpdateView.as_view(), name='edit_profile'),

    # Путь для создания поста.
    # Из шаблона он должен вызываться
    # по ссылке posts/create/
    # вообще без аттритбутов: {% url 'blog:create_post' %}
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),

    # Путь для просмотра поста.
    # Из шаблона он должен вызываться
    # по ссылке posts/<int:pk>/
    # с одним атрибутом: {% url 'blog:post_detail' post.id %} ("номер поста").
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),

    # Путь для редактирования поста.
    # Из шаблона он должен вызываться
    # по ссылке posts/<post_id>/edit/
    # с одним атрибутом: {% url 'blog:edit_post' post.id %} ("номер поста").
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),

    # Путь для удаления поста.
    # Из шаблона он должен вызываться
    # по ссылке posts/<post_id>/delete/
    # с одним атрибутом: {% url 'blog:delete_post' post.id %} ("номер поста").
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),

    # Путь для создания комментария к посту.
    # Из шаблона он должен вызываться
    # по ссылке posts/<post_id>/comment/
    # с одним атрибутом: {% url 'blog:add_comment' post_id %} ("номер поста").
    path('posts/<int:post_pk>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),

    # Путь для редактирования комментария к посту.
    # Из шаблона он должен вызываться
    # по ссылке posts/<post_id>/edit_comment/<comment_id>/
    # с двумя атр-ми: {% url 'blog:edit_comment' comment.post_id comment.id %}
    # ("номер поста к которому комментарий" и "номер самого комментария").
    path('posts/<int:post_pk>/edit_comment/<int:comment_pk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),

    # Путь для удаления камента к посту.
    # Из шаблона он должен вызываться
    # по ссылке posts/<post_id>/delete_comment/<comment_id>/
    # с двумя атрибутами: {% url 'blog:delete_comment' post.id comment.id %}
    # ("номер поста к которому комментарий" и "номер самого комментария").
    path('posts/<int:post_pk>/delete_comment/<int:comment_pk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

]
