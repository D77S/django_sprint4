from django.db.models import QuerySet
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView  # , UpdateView

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


class UserDetailView(DetailView):
    """Класс для CBV,
    а конкретно для той, которая отображает
    детализированную информацию об одном
    конкретном пользователе.
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


def UserUpdateView(request) -> HttpResponse:
    """ """
    # model = User
    template_name = 'blog/user.html'
    # slug_url_kwarg = 'username'
    # slug_field = 'username'
    context = {
        'form': None,  # user_update_form,
        }
    return render(request, template_name, context)


def CreatePostView(request) -> HttpResponse:
    """"""
    context = {}
    return render(request, 'blog/create.html', context)


def index(request) -> HttpResponse:
    """Функция для отображения главной страницы."""
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


def post_detail(request, id: int) -> HttpResponse:
    """Функция для отображения всех данных
    по одному конкретному посту,
    принимает стандартное заклинание request и
    номер того поста, данные по которому надо отобразить,
    возвращает отрендеренную страницу (пост детально).
    """
    posts = posts_selected().filter(
        pk=id, is_published=True,
        category__is_published=True)
    post = get_object_or_404(posts, pub_date__lte=timezone.now())
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug: str) -> HttpResponse:
    """Функция для отображения всех постов одной из категорий,
    принимает стандартное заклинание request и
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