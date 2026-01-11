# main/services/parser_service.py
from django.db import transaction
from ..models import Task
from ..parsers.hexlet_parser import HexletParser
from ..parsers.stepik_adapter import StepikAdapter
from ..parsers.parse_stepik import Command

class ParserService:
    @staticmethod
    def parse_hexlet():
        """Парсинг Hexlet"""
        # Импортируем тут, чтобы избежать циклических импортов
        from ..parsers.hexlet_parser import HexletParser

        parser = HexletParser()
        courses = parser.parse()

        if not courses:
            return 0

        with transaction.atomic():
            for course_data in courses:
                Task.objects.update_or_create(
                    title=course_data['title'],
                    source='hexlet',
                    defaults=course_data
                )

        return len(courses)

    @staticmethod
    def parse_stepik():
        """Парсинг Stepik (синхронная обертка)"""
        # Импортируем тут
        from ..parsers.stepik_adapter import StepikAdapter

        courses = StepikAdapter.run_sync()

        if not courses:
            return 0

        with transaction.atomic():
            for course_data in courses:
                Task.objects.update_or_create(
                    title=course_data['title'],
                    source='stepik',
                    defaults=course_data
                )

        return len(courses)

    @staticmethod
    def parse_all():
        """Запуск всех парсеров"""
        results = {
            'hexlet': 0,
            'stepik': 0,
            'total': 0
        }

        try:
            results['hexlet'] = ParserService.parse_hexlet()
        except Exception as e:
            print(f"Ошибка парсинга Hexlet: {e}")

        try:
            results['stepik'] = ParserService.parse_stepik()
        except Exception as e:
            print(f"Ошибка парсинга Stepik: {e}")

        results['total'] = results['hexlet'] + results['stepik']
        return results

    def __init__(self):
        self.hexlet_parser = HexletParser()
        self.stepik_adapter = StepikAdapter()

    def parse_data(self, source, data):
        print(f"Parsing data from {source}...")

        if source == 'hexlet':
            result = self.hexlet_parser.parse(data)
            print(f"Hexlet parsed {len(result) if isinstance(result, list) else 1} items")
            return result

        elif source == 'stepik':
            print(f"Stepik data type: {type(data)}, length: {len(data) if hasattr(data, '__len__') else 'N/A'}")

            # Способ 1: через адаптер
            result = self.stepik_adapter.parse(data)

            # Способ 2: через функцию (раскомментировать если нужно)
            # result = parse_stepik_data(data)

            print(f"Stepik parsed {len(result) if isinstance(result, list) else 1} items")
            return result

        else:
            raise ValueError(f"Unknown source: {source}")


    def get_hexlet_courses_with_links(self):
        """
        Возвращает курсы Hexlet с HTML ссылками
        """
        hexlet_parser = HexletParser()
        courses = hexlet_parser.parse()

        # Добавляем HTML ссылки к каждому курсу
        for course in courses:
            course['html_link'] = f'<a href="{course["url"]}" target="_blank">{course["title"]}</a>'

        return courses


    def get_hexlet_html_block(self):
        """
        Возвращает готовый HTML блок с курсами Hexlet
        """
        hexlet_parser = HexletParser()
        return hexlet_parser.generate_html_block()