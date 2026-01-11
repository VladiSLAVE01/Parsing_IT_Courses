# test_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IT_Courses.settings')
django.setup()

from main.models import Task

# Проверяем, есть ли курсы в базе
count = Task.objects.count()
print(f"Всего курсов в базе: {count}")

if count > 0:
    print("\nПоследние 5 курсов:")
    for task in Task.objects.all().order_by('-created_at')[:5]:
        print(f"- {task.title} ({task.source}) - URL: {task.url}")
else:
    print("База данных пуста. Добавьте курсы через парсинг или форму создания.")