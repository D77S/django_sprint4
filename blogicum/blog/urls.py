# from django.contrib.auth.forms import UserCreationForm
from django.urls import path
# from django.views.generic import DetailView

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('profile/<slug:username>/',
         views.UserDetailView.as_view(), name='profile'),
    path('edit_profile/', views.UserUpdateView, name='edit_profile'),
    path('create_post/', views.CreatePostView, name='create_post'),
]