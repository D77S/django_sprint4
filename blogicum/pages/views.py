from django.http import HttpResponse
from django.shortcuts import render


def page_not_found(request, exception) -> HttpResponse:
    '''
    View-функция, возвращает
    рендер кастомной страницы ошибки ненайденной страницы (404).'''
    return render(request, 'pages/404.html', status=404)


def server_failure(request) -> HttpResponse:
    '''
    View-функция, возвращает
    рендер кастомной страницы ошибки сервера (500).'''
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason='') -> HttpResponse:
    '''
    View-функция, возвращает
    рендер кастомной страницы ошибки токена (403).'''
    return render(request, 'pages/403csrf.html', status=403)
