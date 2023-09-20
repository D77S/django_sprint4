from django.urls import path
from django.views.generic import TemplateView

app_name = 'pages'

urlpatterns = [
    # Путь для статичной страницы "О проекте".
    # Из шаблона он должен вызываться
    # по ссылке about/
    # вообще без атрибутов: {% url 'pages:about' %}.
    path('about/', TemplateView.as_view(template_name='pages/about.html'),
         name='about'),

    # Путь для статичной страницы "Правила проекта".
    # Из шаблона он должен вызываться
    # по ссылке rules/
    # вообще без атрибутов: {% url 'pages:rules' %}.
    path('rules/', TemplateView.as_view(template_name='pages/rules.html'),
         name='rules'),
]
