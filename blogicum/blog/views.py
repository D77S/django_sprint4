from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from typing import Any

from .forms import CommentForm, PostForm, UserUpdateForm
from .models import Category, Comment, Post, User

PAGINATE_BY_THIS = 10


def author_selected(self):
    """
    Возвращает один (нужный) объект модели авторов постов."""
    return get_object_or_404(User, username=self.kwargs['username'])


def posts_just_selected() -> QuerySet:
    """
    Возвращает queryset модели Post
    с заджойненными к ней моделями
    Category, Location, User,
    без фильтрации,
    только сортировка по дате публикации."""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).order_by('-pub_date')


def posts_selected() -> QuerySet:
    """
    Возвращает queryset модели Post
    с заджойненными к ней моделями
    Category, Location, User,
    с фильтрацией,
    сортировка по дате публикации,
    с присоединенным полем счетчика каментов."""
    return posts_just_selected().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments'))


def posts_selected_with_unpublished_and_future() -> QuerySet:
    """
    Возвращает queryset модели Post
    с заджойненными к ней моделями
    Category, Location, User,
    без фильтрации,
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
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['pk']}))  # type: ignore
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class IndexView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает главную страницу.

    Наследован от стандартного ListView,
    но переопределяем:
    - имя шаблона показывания,
    - величину пагинирования,
    - queryset показываемый, в который мы кладем
    queryset модели Post с заджойненными к ней моделями
    Category, Location, User, с фильтрацией,
    сортировка по дате публикации."""

    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet:
        return posts_selected()


class CategoryView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает все (почти) посты заданной категории.

    Наследован от стандартного ListView,
    но переопределяем:
    - имя шаблона показывания,
    - величину пагинирования,
    - queryset показываемый, в который мы кладем
    queryset модели Post с заджойненными к ней моделями
    Category, Location, User, с фильтрацией,
    сортировка по дате публикации.
    А перед его вычислением - получаем объект модели категорий,
    используя имя категории, переданное сюда в упаковке kwargs."""

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
            pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'])
        return context


class UserDetailView(PaginateMixin, ListView):
    """Класс для CBV, которая
    отображает детализированную информацию
    об одном конкретном пользователе.

    Наследован от стандартного DetailView,
    но переопределяем:
    - имя шаблона показывания,
    - имя переменной в urls, в которую принят идентификатор объекта модели,
    - имя поля модели, с которым надо сопоставлять предыдущий, когда он slug,
    - имя переменной контекста, через которую транспортируем всё в шаблон,
    - величину пагинирования,
    - queryset показываемый, в который мы кладем
    queryset модели Post с заджойненными к ней моделями
    Category, Location, User, без фильтрации,
    сортировка по дате публикации, отфильтровав одного нужного автора.
    А перед его вычислением - получаем объект модели юзеров,
    используя имя автора, переданное сюда в упаковке kwargs.

    И еще увеличиваем контекст,
    добавив к родительскому объект нужного автора."""

    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_queryset(self) -> QuerySet:
        return posts_selected_with_unpublished_and_future().filter(
            author=author_selected(self)
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = author_selected(self)
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    апдейтит профиль залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как апдейтить профиль (свой!)
    разрешено только залогиненному юзеру.

    Переопределяем:
    - форму показываемую,
    - имя шаблона показывания,
    - локатор при успешном завершении обратно из шаблона,
    - объект показываемый, в который мы кладем объект юзера из запроса.
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

     Переопределяем:
    - модель, куда потом сунем созданный объект,
    - форму показываемую,
    - имя шаблона показывания,
    - метод валидации формы, чтобы он дополнительно к родительскому еще делал:
        - юзера в нее помещаем из залогиненного,
        - и еще проверяем, что юзер не установил pub_date в прошлом,
    - локатор при успешном завершении обратно из шаблона.
    """
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
    включая каменты к нему.

    Переопределяем:
    - объект показываемый, в который мы кладем объект модели Post,
    по ключу pk из пути, заджойнив к нему категорию, автора, локацию.
    Если только залогиненный юзер - автор поста,
    время опубликации уже наступило, и категория не снята.

    И еще увеличиваем контекст,
    добавив к родительскому:
    - объект формы камента;
    - все уже имеющиеся каменты данного поста."""

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
    редактирует пост, если залогинен его автор.

    Наследован от стандартного UpdateView.

    Переопределяем:
    - локатор при успешном завершении обратно из шаблона -
    на только что проапдейтенный пост,
    - дистпетчера чтоб не прошел неавтор,
    - валидатор формы для проверки, что не вписали прошедшее время публикации.
    """

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
    удаляет пост залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалить пост
    разрешено только залогиненному юзеру.
    Перед удалением поста должна открываться
    подтверждающая страница, содержащая удаляемый пост.

    Переопределяем:
    - модель используемую,
    - шаблон показываемый,
    - локатор успешного завершения шаблона,
    - дистпетчера чтоб не прошел неавтор.
    """
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})  # type: ignore


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс для CBV, которая
    создает комментарий залогиненного юзера.

    Наследован от стандартного CreateView,
    и еще от LoginRequiredMixin, так как создать камент
    разрешено только залогиненному юзеру.

    Переопределяем:
    - локатор успешного завершения шаблона,
    - валидатор формы.

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


class DispatchCommentMixin:
    """
    Миксин переопределения диспетчера
    по проверке на авторство каментов там, где
    надо убедиться, что на действие претендует автор.
    """
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_pk']}))  # type: ignore
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class CommentUpdateView(DispatchCommentMixin, LoginRequiredMixin, UpdateView):
    """Класс для CBV, которая
    редактирует комментарий залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как редактировать камент
    разрешено только залогиненному юзеру.

    Переопределяем:
    - диспетчера, что не прошел неавтор,
    - объект в шаблон, один нужный камент,
    - локатор успешного завершения шаблона.
    """
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})


class CommentDeleteView(DispatchCommentMixin, LoginRequiredMixin, DeleteView):
    """Класс для CBV, которая
    удаляет комментарий залогиненного юзера.

    Наследован от стандартного DeleteView,
    и еще от LoginRequiredMixin, так как удалять камент
    разрешено только залогиненному юзеру.

    Переопределяем:
    - диспетчера, что не прошел неавтор,
    - локатор успешного завершения шаблона.
    """
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_pk']})
