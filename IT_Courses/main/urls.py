from django.urls import path
from . import views
#Отсылается к функциям в views
urlpatterns = [
    path('', views.index, name="home"),
    path('courses/', views.courses, name="courses"),
    path('create', views.create, name="create"),
    path('parse/', views.parse_courses, name="parse"),
]