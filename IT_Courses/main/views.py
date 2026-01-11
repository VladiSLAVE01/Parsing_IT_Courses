# main/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from .services.parser_service import ParserService
from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from datetime import datetime
def hexlet_courses_view(request):
    """Страница с курсами Hexlet"""
    service = ParserService()

    # Получаем курсы с ссылками
    courses = service.get_hexlet_courses_with_links()

    # ИЛИ получаем готовый HTML блок
    html_block = service.get_hexlet_html_block()

    context = {
        'courses': courses,
        'html_block': html_block,
        'courses_count': len(courses),
    }

    return render(request, 'hexlet_courses.html', context)

def parse_dashboard(request):
    """Dashboard для управления парсерами"""
    stats = {
        'total': Task.objects.count(),
        'hexlet': Task.objects.filter(source='hexlet').count(),
        'stepik': Task.objects.filter(source='stepik').count(),
    }

    return render(request, 'main/parse_dashboard.html', {'stats': stats})

def index(request):
    return render(request, 'main/index.html')


def courses(request):
    source_filter = request.GET.get('source', 'all')

    if source_filter == 'hexlet':
        tasks = Task.objects.filter(source='hexlet')
    elif source_filter == 'stepik':
        tasks = Task.objects.filter(source='stepik')
    elif source_filter == 'with_links':
        tasks = Task.objects.exclude(url__isnull=True).exclude(url='')
    else:
        tasks = Task.objects.all()

    # Статистика
    stats = {
        'total': Task.objects.count(),
        'hexlet': Task.objects.filter(source='hexlet').count(),
        'stepik': Task.objects.filter(source='stepik').count(),
        'with_links': Task.objects.exclude(url__isnull=True).exclude(url='').count(),
    }

    context = {
        'tasks': tasks.order_by('-created_at'),
        'stats': stats,
        'current_source': source_filter,
        'title': 'Список курсов'
    }
    return render(request, 'main/courses.html', context)

def parse_hexlet(request):
    """Парсинг Hexlet с сохранением ссылок - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        # Используем исправленный сервис парсинга
        count = ParserService.parse_hexlet()  # ← ВАЖНО: вызываем сервис!

        # Получаем статистику для сообщения
        hexlet_courses = Task.objects.filter(source='hexlet')
        hexlet_with_links = hexlet_courses.exclude(url__isnull=True).exclude(url='').count()

        messages.success(
            request,
            f'✓ Парсинг Hexlet завершен! '
            f'Добавлено/обновлено: {count} курсов. '
            f'Курсов со ссылками: {hexlet_with_links}.'
        )

        # Сохраняем информацию о парсинге
        request.session['last_parsed'] = {
            'date': datetime.now().isoformat(),
            'source': 'hexlet',
            'count': count,
        }

    except Exception as e:
        messages.error(request, f'✗ Ошибка при парсинге Hexlet: {str(e)}')
        print(f"ERROR in parse_hexlet: {e}")  # Для отладки

    return redirect('parse_dashboard')


def export_links(request):
    """Экспорт всех ссылок в HTML"""
    courses = Task.objects.filter(url__isnull=False).exclude(url='')

    # Генерируем HTML
    html_content = f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Ссылки на курсы</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .course {{ margin: 15px 0; padding: 10px; border-left: 4px solid #007bff; }}
            .source {{ color: #666; font-size: 0.9em; }}
            .date {{ color: #999; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <h1>Ссылки на IT курсы</h1>
        <p>Экспортировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <p>Всего ссылок: {courses.count()}</p>

        <div id="links">
    '''

    for course in courses:
        html_content += f'''
        <div class="course">
            <h3><a href="{course.url}" target="_blank">{course.title}</a></h3>
            <p>{course.description[:200] if course.description else ''}</p>
            <div class="source">Источник: {course.get_source_display()}</div>
            <div class="date">Добавлено: {course.created_at.strftime('%d.%m.%Y')}</div>
        </div>
        '''

    html_content += '''
        </div>
    </body>
    </html>
    '''

    # Создаем HTTP ответ с файлом
    response = HttpResponse(html_content, content_type='text/html')
    response[
        'Content-Disposition'] = f'attachment; filename="course_links_{datetime.now().strftime("%Y%m%d_%H%M")}.html"'
    return response


def courses_with_links(request):
    """Страница только с курсами, имеющими ссылки"""
    courses = Task.objects.filter(url__isnull=False).exclude(url='')

    # Статистика
    stats = {
        'total': Task.objects.count(),
        'hexlet': Task.objects.filter(source='hexlet').count(),
        'stepik': Task.objects.filter(source='stepik').count(),
        'with_links': courses.count(),
    }

    context = {
        'title': 'Курсы со ссылками',
        'tasks': courses,
        'stats': stats,
        'current_source': 'with_links',
    }

    return render(request, 'main/courses.html', context)

def parse_stepik(request):
    """Запуск парсера Stepik"""
    try:
        count = ParserService.parse_stepik()
        messages.success(request, f'Добавлено {count} курсов с Stepik')
    except Exception as e:
        messages.error(request, f'Ошибка парсинга Stepik: {e}')

    return redirect('parse_dashboard')


def parse_all(request):
    """Запуск всех парсеров"""
    try:
        results = ParserService.parse_all()
        messages.success(request,
                         f'Парсинг завершен! Добавлено {results["total"]} курсов '
                         f'(Hexlet: {results["hexlet"]}, Stepik: {results["stepik"]})'
                         )
    except Exception as e:
        messages.error(request, f'Ошибка: {e}')

    return redirect('parse_dashboard')


def create_course(request):
    """Страница для создания курса вручную"""
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            title = request.POST.get('title', '').strip()

            if not title:
                messages.error(request, 'Название курса обязательно!')
                return render(request, 'main/create.html')

            # Создаем курс
            Task.objects.create(
                title=title,
                description=request.POST.get('description', '').strip(),
                url=request.POST.get('url', '').strip(),
                source=request.POST.get('source', 'manual'),
                price=request.POST.get('price', '').strip(),
                image_url=request.POST.get('image_url', '').strip(),
                # Определяем платный/бесплатный по цене
                is_paid='бесплатно' not in request.POST.get('price', '').lower(),
                language='ru',
            )

            messages.success(request, '✅ Курс успешно добавлен!')
            return redirect('courses')

        except Exception as e:
            messages.error(request, f'❌ Ошибка: {str(e)}')
            return render(request, 'main/create.html')

    # Если GET запрос - просто показываем форму
    return render(request, 'main/create.html')