from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.models import Category, Comment, Post

from .forms import CommentForm, PostForm, UserUpdateForm
from .models import User

# TRUNCATE_LIST_TO = 5
PAGINATE_BY_THIS = 10


def posts_just_selected() -> QuerySet:
    """Возвращает Queryset модели (таблицы) Post
    с заджойненными к ней моделями (таблицами)
    Category, Location, User,
    без фильтрации,
    только сортировка по дате публикации."""
    return Post.objects.select_related(
               'category',
               'location',
               'author').order_by('-pub_date')


def posts_selected() -> QuerySet:
    """Возвращает Queryset модели (таблицы) Post
    с заджойненными к ней моделями (таблицами)
    Category, Location, User,
    с фильтрацией,
    сортировка по дате публикации."""
    return (Post.objects
            .select_related(
                'category',
                'location',
                'author').filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()).annotate(
                    comment_count=Count('comments')).order_by('-pub_date'))


def posts_selected_with_unpublished_and_future():
    return (Post.objects
            .select_related(
                'category',
                'location',
                'author')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date'))


class IndexView(ListView):
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY_THIS

    def get_queryset(self):
        return posts_selected()


class CategoryView(ListView):
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY_THIS

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'])
        if not category.is_published:
            raise Http404
        return posts_just_selected().filter(
            category=category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'])
        return context


class UserDetailView(ListView):
    """Класс для CBV, которая
    отображает детализированную информацию
    об одном конкретном пользователе.

    Наследован от стандартного DetailView,
    но переопределяем:
    - модель, объект которой нам нужен,
    - имя шаблона показывания,
    - имя переменной в urls, в которую принят идентификатор объекта модели,
    - имя поля модели, с которым надо сопоставлять предыдущий, когда он slug,
    - имя переменной контекста, через которую транспортируем всё в шаблон.
    """
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'
    paginate_by = PAGINATE_BY_THIS

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        return posts_selected_with_unpublished_and_future().filter(
            author=author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    апдейтит профиль залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как апдейтить профиль (свой!)
    разрешено только залогиненному юзеру.
    """
    form_class = UserUpdateForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает новый пост залогиненного юзера.

    Наследован от стандартного DetailView,
    и еще от LoginRequiredMixin, так как создавать новый пост
    разрешено только залогиненному юзеру.
    """
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})  # type: ignore


class PostDetailView(DetailView):
    """Класс для CBV, которая
    отображает все данные
    по одному конкретному посту,
    включая каменты к нему.
    """
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        object = get_object_or_404(Post.objects.select_related(
            'category', 'author', 'location'), id=self.kwargs['pk'])
        if (self.request.user == object.author or
            object.pub_date <= timezone.now() and
            object.is_published and
                object.category.is_published):
            return object
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()  # type: ignore
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    редактирует пост, если залогинен его автор.

    Наследован от стандартного UpdateView.
    """

    template_name = 'blog/create.html'  # Тот же, что и для создания поста.
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['pk']}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.instance.pub_date < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для CBV, которая
    удаляет пост залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалить пост
    разрешено только залогиненному юзеру.
    Перед удалением поста должна открываться
    подтверждающая страница, содержащая удаляемый пост.
    """
    model = Post

    template_name = 'blog/create.html'  # Да. Именно этот.
    # Тот же, что и для создания поста.

    success_url = reverse_lazy('blog:profile')

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})  # type: ignore

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['pk']}))

        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает комментарий залогиненного юзера.

    Наследован от стандартного CreateView,
    и еще от LoginRequiredMixin, так как создать камент
    разрешено только залогиненному юзеру.
    """
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


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    редактирует комментарий залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как редактировать камент
    разрешено только залогиненному юзеру.
    """
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_pk']}))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Класс для CBV, которая
    удаляет комментарий залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалять камент
    разрешено только залогиненному юзеру.
    """
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_pk']}))

        return super().dispatch(request, *args, **kwargs)
