from django.contrib import admin
from django.urls import path, include
#Основоной urls файл и ведет в main/urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),

]
