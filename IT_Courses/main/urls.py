from django.urls import path
from . import views
#Отсылается к функциям в views
urlpatterns = [
    path('', views.index, name="home"),
    path('courses/', views.courses, name="courses"),
    path('create/', views.create_course, name="create_courses"),
    path('parse/', views.parse_dashboard, name="parse_dashboard"),
    path('parse/hexlet/', views.parse_hexlet, name="parse_hexlet"),
    path('parse/stepik/', views.parse_stepik, name="parse_stepik"),
    path('parse/all/', views.parse_all, name="parse_all"),
    path('export/links/', views.export_links, name='export_links'),
    path('courses/links/', views.courses_with_links, name='courses_with_links'),

]