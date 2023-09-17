from django.contrib import admin
from django.urls import include, path

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
]
