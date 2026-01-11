# main/parsers/stepik_adapter.py
import asyncio
from .stepik_parser import StepikParser

class StepikAdapter:
    def __init__(self):
        self.parser = StepikParser()

    def parse(self, data):
        transformed_data = self._adapt_data(data)
        # адаптация данных для StepikParser
        return self.parser.parse_raw(data)
    """Адаптер для преобразования данных Stepik в нашу модель"""

    @staticmethod
    def transform_course(stepik_course):
        """Преобразует курс Stepik в формат для модели Task"""
        return {
            'title': stepik_course.get('title', 'Без названия'),
            'description': stepik_course.get('summary', '') or stepik_course.get('description', ''),
            'source': 'stepik',
            'is_paid': stepik_course.get('is_paid', False),
            'price': f"{stepik_course.get('price', 0)} {stepik_course.get('currency_code', 'RUB')}"
            if stepik_course.get('price') else "Бесплатно",
            'image_url': stepik_course.get('cover', ''),
            'learners_count': stepik_course.get('learners_count', 0),
            'time_to_complete': stepik_course.get('time_to_complete'),
            'language': stepik_course.get('language', 'ru'),
            'reviews_count': stepik_course.get('reviews_count', 0),
            'rating': stepik_course.get('avg_rating'),
            'category': ', '.join([cat.get('title', '') for cat in stepik_course.get('categories', [])]),
        }

    @staticmethod
    async def parse_async():
        """Асинхронный запуск парсера"""
        # Импортируем тут чтобы избежать циклических импортов
        from IT_Courses.main.services.parser_service import ParserService
        from .stepik_parser import StepikParser
        parser = StepikParser(max_concurrent=7)
        courses_data, course_ids = await parser.parse()

        transformed_courses = []
        if courses_data:
            # Предполагаем, что courses_data - это словарь с ключами
            for list_name, list_info in courses_data.items():
                if 'courses' in list_info:
                    for course in list_info['courses']:
                        transformed_courses.append(
                            StepikAdapter.transform_course(course)
                        )

        return transformed_courses

    @staticmethod
    def run_sync():
        """Синхронный запуск асинхронного парсера"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(StepikAdapter.parse_async())
        except Exception as e:
            print(f"Ошибка в Stepik парсере: {e}")
            return []
        finally:
            loop.close()

    def _adapt_data(self, data):
        # Здесь логика адаптации данных
        # Например, меняем структуру JSON или добавляем нужные поля
        return {
            'raw_data': data,
            'source': 'stepik',
            # другие необходимые преобразования
        }