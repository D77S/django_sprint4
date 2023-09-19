#  from typing import Any

from blog.models import Category, Comment, Post
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.paginator import Paginator
from django.db.models import Count, QuerySet
#  from django.db.models.query import QuerySet
from django.http import Http404  # , HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404  # , render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm
from .models import User

# TRUNCATE_LIST_TO = 5
PAGINATE_BY_THIS = 10


def posts_selected() -> QuerySet:
    """Функция, ничего не принимает,
    возвращает Queryset модели (таблицы) Post
    с заджойненными к ней моделями (таблицами)
    Category, Location, User
    с фильтрацией по нужным полям."""
    return (Post.objects
            .select_related(
                'category',
                'location',
                'author')
            .filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now())
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date'))


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY_THIS
    queryset = posts_selected()


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY_THIS

    def get_queryset(self):
        return get_list_or_404(
            posts_selected().filter(
                category__slug=self.kwargs['category_slug']))

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
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'
    paginate_by = PAGINATE_BY_THIS

    def get_queryset(self):
        return get_list_or_404(
            posts_selected().filter(
                author_id__username=self.kwargs['username']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class UserUpdateView(UpdateView, LoginRequiredMixin):
    """Класс для CBV, которая
    апдейтит профиль залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как апдейтить профиль (свой!)
    разрешено только залогиненному юзеру.
    """
    model = User
    fields = 'first_name', 'last_name', 'login', 'email'
    template_name = 'blog/user.html'
    # slug_url_kwarg = 'username'
    # slug_field = 'username'
    # context = {
    #    'form': None,  # user_update_form,
    #    }


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает новый пост залогиненного юзера.

    Наследован от стандартного DetailView,
    и еще от LoginRequiredMixin, так как создавать новый пост
    разрешено только залогиненному юзеру.
    """
    model = Post
    # form_class = ???
    # fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        # Присвоить полю "имя автора" - объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class PostDetailView(DetailView):
    """Класс для CBV, которая
    отображает все данные
    по одному конкретному посту,
    включая каменты к нему.

    Наследован от стандартного DetailView.
    """
    template_name = 'blog/detail.html'
    model = Post

    # тест проверяет обращение к странице неопубликованного поста от
    # пользователя-не автора. Ожидает ошибку 404 - страница не найдена.
    def get_object(self, queryset=None):
        object = get_object_or_404(Post.objects.select_related(
            'category', 'author', 'location'), id=self.kwargs['pk'])
        if object.category is not None:
            if object.is_published and object.category.is_published and (
             self.request.user == object.author or
             object.pub_date <= timezone.now()):
                return object
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()  # type: ignore
        return context


class PostUpdateView(UpdateView):
    """Класс для CBV, которая
    редактирует пост, если залогинен его автор.

    Наследован от стандартного UpdateView.
    """
    # model = ???
    # form_class = ???
    # fields = '__all__'

    template_name = 'blog/create_post.html'  # Да. Именно этот.
    # Тот же, что и для создания поста.

    # Права на редактирование должны быть только у автора публикации.
    # Остальные пользователи должны перенаправляться
    # на страницу просмотра поста.
    # После окончания редактирования пользователь должен переадресовываться
    # на страницу отредактированной публикации.
    success_url = reverse_lazy('blog:post_detail')


class PostDeleteView(DeleteView, LoginRequiredMixin):
    """Класс для CBV, которая
    удаляет пост залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалить пост
    разрешено только залогиненному юзеру.

    Перед удалением поста должна открываться
    подтверждающая страница, содержащая удаляемый пост.
    """
    # model = ???
    # form_class = ???
    # fields = '__all__'

    template_name = 'blog/create_post.html'  # Да. Именно этот.
    # Тот же, что и для создания поста.

    success_url = reverse_lazy('blog:profile')


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
    # Подумаем, куда потом перенаправлять юзера после создания.

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(id=self.kwargs['post_pk'])
        return super().form_valid(form)


class CommentUpdateView(UpdateView, LoginRequiredMixin):
    """Класс для CBV, которая
    редактирует комментарий залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как редактировать камент
    разрешено только залогиненному юзеру.
    """
    model = Comment
    form_class = CommentForm
    # fields = '__all__'
    template_name = 'blog/comment.html'
    # Подумаем, куда потом перенаправлять юзера после создания.

    # pk_url_kwarg: The name of the URLConf keyword
    # argument that contains the primary key.
    # By default, pk_url_kwarg is 'pk'.

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            raise PermissionError
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(DeleteView, LoginRequiredMixin):
    """Класс для CBV, которая
    удаляет комментарий залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалять камент
    разрешено только залогиненному юзеру.
    """
    model = Comment
    form_class = CommentForm
    # fields = '__all__'
    template_name = 'blog/comment.html'
    # Подумаем, куда потом перенаправлять юзера после создания.
    success_url = reverse_lazy('blog:post_detail')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            raise PermissionError
        return super().dispatch(request, *args, **kwargs)
