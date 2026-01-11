# main/services/parser_service.py
from django.db import transaction
from ..models import Task


class ParserService:
    @staticmethod
    def parse_hexlet():
        """Парсинг Hexlet с сохранением ссылок"""
        from ..parsers.hexlet_parser import HexletParser

        parser = HexletParser()
        courses = parser.parse()

        if not courses:
            print("DEBUG: Парсер вернул пустой список")
            return 0

        saved_count = 0
        links_count = 0
        print(f"DEBUG: Получено {len(courses)} курсов от парсера")

        with transaction.atomic():
            for i, course_data in enumerate(courses):
                print(f"\nDEBUG: Обработка курса {i + 1}: {course_data['title'][:50]}...")
                print(f"DEBUG: URL курса: {course_data.get('url', 'НЕТ ССЫЛКИ')}")

                # Используем get_or_create вместо ручной проверки
                task, created = Task.objects.get_or_create(
                    title=course_data['title'],
                    source='hexlet',
                    defaults={
                        'description': course_data.get('description', ''),
                        'url': course_data.get('url', ''),  # ← Сохраняем ссылку
                        'price': course_data.get('price', ''),
                        'image_url': course_data.get('image_url', ''),
                        'start_end': course_data.get('start_end', ''),
                        'is_paid': course_data.get('is_paid', False),
                        'language': course_data.get('language', 'ru'),
                    }
                )

                if created:
                    saved_count += 1
                    if course_data.get('url'):
                        links_count += 1
                        print(f"DEBUG: СОЗДАН новый курс со ссылкой")
                else:
                    # Если курс уже существовал, но не было ссылки - обновляем
                    if not task.url and course_data.get('url'):
                        task.url = course_data['url']
                        task.save()
                        links_count += 1
                        print(f"DEBUG: ОБНОВЛЕН существующий курс: добавлена ссылка")

        print(f"\nDEBUG: ИТОГО: Добавлено новых курсов: {saved_count}, Получено ссылок: {links_count}")
        return saved_count

    @staticmethod
    def parse_stepik():
        """Парсинг Stepik"""
        from ..parsers.stepik_adapter import StepikAdapter

        courses = StepikAdapter.run_sync()

        if not courses:
            return 0

        saved_count = 0
        for course_data in courses:
            task, created = Task.objects.get_or_create(
                title=course_data['title'],
                source='stepik',
                defaults=course_data
            )
            if created:
                saved_count += 1

        return saved_count

    @staticmethod
    def parse_all():
        """Запуск всех парсеров"""
        results = {
            'hexlet': ParserService.parse_hexlet(),
            'stepik': ParserService.parse_stepik(),
        }
        results['total'] = results['hexlet'] + results['stepik']
        return results