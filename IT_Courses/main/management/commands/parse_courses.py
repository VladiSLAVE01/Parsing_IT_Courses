# main/management/commands/parse_courses.py
from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from main.models import Task

class Command(BaseCommand):
    help = 'Парсинг курсов с Hexlet.io'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем парсинг курсов...')

        # Импортируем здесь, чтобы избежать циклических импортов

        # Очистим старые данные (опционально)
        Task.objects.all().delete()

        count_courses = ["courses_front_end_dev", "courses_backend_development"]

        for course_type in count_courses:
            url = f"https://ru.hexlet.io/{course_type}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                data = soup.find_all("div", tabindex="0")

                for i in data:
                    try:
                        name = i.find("p", class_="mantine-focus-auto m_b6d8b162 mantine-Text-root").text
                        start_end = i.find("span", class_="mantine-focus-auto m_b6d8b162 mantine-Text-root").text
                        money = i.find("p", style="font-size:var(--mantine-font-size-xl)").text
                        image = i.find("img", class_="m_9e117634 mantine-Image-root mantine-visible-from-xs")["src"]

                        # Сохраняем в базу данных
                        Task.objects.create(
                            title=name,
                            task=start_end,
                            price=money,
                            image_url=image
                        )

                        self.stdout.write(f'Добавлен курс: {name}')

                    except AttributeError:
                        continue  # пропускаем элементы без нужных данных
                    except Exception as e:
                        self.stdout.write(f'Ошибка при сохранении: {e}')
                        continue

            except requests.RequestException as e:
                self.stdout.write(f'Ошибка при запросе {url}: {e}')
                continue

        self.stdout.write(self.style.SUCCESS('Парсинг завершен!'))