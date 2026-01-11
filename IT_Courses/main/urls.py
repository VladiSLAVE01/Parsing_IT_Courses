from django.urls import path
from . import views
#Отсылается к функциям в views
urlpatterns = [
    path('', views.index, name="home"),
    path('courses/', views.courses, name="courses"),
    path('create/', views.create, name="create"),
    # Ендпоинты парсинга
    path('parse/', views.parse_dashboard, name="parse_dashboard"),
    path('parse/hexlet/', views.parse_hexlet, name="parse_hexlet"),
    path('parse/stepik/', views.parse_stepik, name="parse_stepik"),
    path('parse/all/', views.parse_all, name="parse_all"),

]