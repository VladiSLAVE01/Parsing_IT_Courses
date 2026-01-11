# main/management/commands/parse_stepik.py
from django.core.management.base import BaseCommand
from .stepik_adapter import StepikAdapter
class Command(BaseCommand):
    help = 'Парсинг курсов с Stepik.org'

    def handle(self, *args, **options):
        self.stdout.write('Запуск парсера Stepik...')
        try:
            # Импортируем тут
            from ..services.parser_service import ParserService
            count = ParserService.parse_stepik()
            self.stdout.write(
                self.style.SUCCESS(f'Успешно! Добавлено {count} курсов с Stepik')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {e}')
            )

    def parse_stepik_data(data):
        try:
            adapter = StepikAdapter()
            return adapter.parse(data)
        except Exception as e:
            print(f"Error parsing Stepik data: {e}")
            return []