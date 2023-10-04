from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserUpdateForm
from .models import Category, Comment, Post, User

PAGINATE_BY_THIS = 10


def author_selected(username_required) -> User:
    """
    Возвращает один (нужный) объект модели авторов постов."""
    return get_object_or_404(User, username=username_required)
    # return get_object_or_404(User, username=self.kwargs['username'])


def posts_just_selected() -> QuerySet:
    """
    Возвращает queryset модели Post с заджойненными к ней моделями
    Category, Location, User, без фильтрации,
    только сортировка по дате публикации."""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).order_by('-pub_date')


def posts_selected() -> QuerySet:
    """
    Возвращает queryset модели Post с заджойненными к ней моделями
    Category, Location, User, с фильтрацией,
    сортировка по дате публикации,
    с присоединенным полем счетчика каментов."""
    return posts_just_selected().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments'))


def posts_selected_with_unpublished_and_future() -> QuerySet:
    """
    Возвращает queryset модели Post с заджойненными к ней моделями
    Category, Location, User, без фильтрации,
    сортировка по дате публикации,
    с присоединенным полем счетчика каментов."""
    return posts_just_selected().annotate(
        comment_count=Count('comments'))


class PaginateMixin:
    """
    Миксин пагинирования - в трех местах потом.
    """
    paginate_by = PAGINATE_BY_THIS


class DispatchPostMixin:
    """
    Миксин переопределения диспетчера
    по проверке на авторство постов там, где
    надо убедиться, что на действие претендует автор.
    """
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:  # type: ignore
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['pk']}))  # type: ignore
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class IndexView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает главную страницу."""
    # model = Post # если задан get_qweryset, то эта команда лишняя уже
    # Пагинирование задано подмешиванием миксина пагинирования.
    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet:
        return posts_selected()


class CategoryView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает все (почти) посты заданной категории."""
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet:
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'])
        if not category.is_published:
            raise Http404
        return posts_just_selected().filter(
            category=category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()).annotate(
                comment_count=Count('comments'))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'])
        return context


class UserDetailView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает детализированную информацию
    об одном конкретном пользователе."""

    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_queryset(self) -> QuerySet:
        return posts_selected_with_unpublished_and_future().filter(
            author=author_selected(self.kwargs['username'])
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = author_selected(self.kwargs['username'])
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    апдейтит профиль залогиненного юзера."""
    form_class = UserUpdateForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает новый пост залогиненного юзера."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        if form.instance.pub_date < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})  # type: ignore


class PostDetailView(DetailView):
    """Класс для CBV, которая
    отображает все данные
    по одному конкретному посту,
    включая каменты к нему."""

    template_name = 'blog/detail.html'

    def get_object(self, queryset=None) -> Post:
        object = get_object_or_404(Post.objects.select_related(
            'category', 'author', 'location'), id=self.kwargs['pk'])
        if (self.request.user == object.author
           or object.pub_date <= timezone.now()
           and object.is_published
           and object.category.is_published):
            return object
        raise Http404

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()  # type: ignore
        return context


class PostUpdateView(DispatchPostMixin, LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    редактирует пост, если залогинен его автор."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self) -> str:
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form) -> HttpResponse:
        if form.instance.pub_date < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)


class PostDeleteView(DispatchPostMixin, LoginRequiredMixin, DeleteView):
    """Класс для CBV, которая
    удаляет пост залогиненного юзера."""
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})  # type: ignore


class DispatchCommentMixin:
    """
    Миксин переопределения диспетчера
    по проверке на авторство каментов там, где
    надо убедиться, что на действие претендует автор.
    """
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:  # type: ignore
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_pk']}))  # type: ignore
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает комментарий залогиненного юзера."""
    model = Comment
    form_class = CommentForm
    template_name = 'includes/comments.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_pk'])
        return super().form_valid(form)


class CommentUpdateView(DispatchCommentMixin, LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    редактирует комментарий залогиненного юзера."""
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})


class CommentDeleteView(DispatchCommentMixin, LoginRequiredMixin, DeleteView):
    """Класс для CBV, которая
    удаляет комментарий залогиненного юзера."""
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})
