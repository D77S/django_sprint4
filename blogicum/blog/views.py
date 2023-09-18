from django.db.models import QuerySet
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView

from blog.models import Category, Post

from .models import User

# TRUNCATE_LIST_TO = 5
PAGINATE_BY_THIS = 10


def posts_selected() -> QuerySet:
    """Функция, ничего не принимает,
    возвращает Queryset модели (таблицы) Post
    с заджойненными к ней моделями (таблицами)
    Category, Location, User."""
    return Post.objects.select_related(
        'category',
        'location',
        'author')


def index(request) -> HttpResponse:
    """
    Функция для отображения главной страницы."""
    posts = posts_selected().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()).order_by(
            '-pub_date')  # [:TRUNCATE_LIST_TO]
    paginator = Paginator(posts, PAGINATE_BY_THIS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'post_list': posts,
        'page_obj': page_obj,
        }
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug: str) -> HttpResponse:
    """Функция для отображения всех постов одной из категорий,
    принимает request и
    слаг той категории, все посты которой надо отобразить,
    возвращает отрендеренную страницу (все посты заданной категории).
    """
    posts_or_404 = get_list_or_404(
        posts_selected().filter(
            category__slug=category_slug,
            category__is_published=True,
            pub_date__lte=timezone.now()).order_by(
                '-pub_date'), is_published=True)
    selected_category_or_404 = get_object_or_404(
        Category.objects.all(),
        slug=category_slug)
    context = {'post_list': posts_or_404,
               'category': selected_category_or_404
               }
    return render(request, 'blog/category.html', context)


class UserDetailView(DetailView):
    """Класс для CBV, которая
    отображает детализированную информацию
    об одном конкретном пользователе.

    Должно отображаться:
    - информация о пользователе (доступна всем посетителям),
    - публикации пользователя (доступны всем посетителям),
    - ссылка на страницу редактирования профиля для изменения имени,
    фамилии, логина и адреса электронной почты (доступна только залогиненному
    пользователю — хозяину аккаунта),
    - ссылка на страницу изменения пароля (доступна только
    залогиненному пользователю — хозяину аккаунта).

    Наследован от стандартного DetailView,
    но переопределяем:
    - модель, объект которой нам нужен,
    - имя шаблона показывания,
    - имя переменной в urls, в которую принят идентификатор объекта модели,
    - имя поля модели, с которым надо сопоставлять предыдущий, когда он slug,
    - имя переменной контекста, через которую транспортируем всё в шаблон.

    А вот наследоваться от LoginRequiredMixin НЕ НАДО,
    так как часть информации должна быть видна
    и незалогинненному юзеру.
    """
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'
    # еще надо чтобы выводился список всех постов данного
    # (залогинившегося) юзера
    # ??наверное, надо апдейтить контекст??
    # эти публикации потом в шаблоне будут извлекаться, после пагинатора,
    # командой {% for post in page_obj %}
    # т.е. их, наверное, надо приапдейтить к контексту под ключом post(???)

    # и ещё их надо пагинировать по 10 штук
    paginate_by = PAGINATE_BY_THIS


class UserUpdateView(UpdateView, LoginRequiredMixin):
    """Класс для CBV, которая
    апдейтит профиль залогиненного юзера.

    Наследован от стандартного UpdateView,
    и еще от LoginRequiredMixin, так как апдейтить профиль (свой!)
    разрешено только залогиненному юзеру.
    """
    # model = User
    template_name = 'blog/user.html'
    # slug_url_kwarg = 'username'
    # slug_field = 'username'
    # context = {
    #    'form': None,  # user_update_form,
    #    }


class CreatePostView(CreateView, LoginRequiredMixin):
    """Класс для CBV, которая
    создает новый пост залогиненного юзера.

    Наследован от стандартного DetailView,
    и еще от LoginRequiredMixin, так как создавать новый пост
    разрешено только залогиненному юзеру.
    """
    # model = ???
    # form_class = ???
    # fields = '__all__'
    # template_name = '...'
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        # Присвоить полю "имя автора" - объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class PostDetailView(DetailView):
    """Класс для CBV, которая
    отображает все данные
    по одному конкретному посту.

    Наследован от стандартного DetailView,
    (??еще не решил, надо ли также наследоваться
    от LoginRequiredMixin. Наверное всё же нет.??).
    """
    template_name = 'blog/detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.object.select_related('author')
        return context

    # posts = posts_selected().filter(
    #    pk=id, is_published=True,
    #    category__is_published=True)
    # post = get_object_or_404(posts, pub_date__lte=timezone.now())
    # context = {'post': post}


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
    # success_url = reverse_lazy('birthday:list')
