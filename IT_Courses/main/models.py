from django.db import models
class Task(models.Model):
    SOURCE_CHOICES = [
        ('hexlet', 'Hexlet'),
        ('stepik', 'Stepik'),
        ('manual', 'Вручную'),
    ]
    # Основные поля
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Ссылка на курс")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='hexlet')

    # Поля из Hexlet
    price = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True)
    start_end = models.CharField(max_length=200, blank=True)  # для Hexlet

    # Поля из Stepik
    is_paid = models.BooleanField(default=False)
    learners_count = models.IntegerField(default=0)
    time_to_complete = models.IntegerField(null=True, blank=True)  # в минутах
    language = models.CharField(max_length=50, blank=True)
    reviews_count = models.IntegerField(default=0)
    rating = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=200, blank=True)

    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.title} ({self.get_source_display()})"

    class Meta: # Наименования в админ панели
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def get_source_display(self):
        """Отображаемое название источника"""
        if self.source == 'hexlet':
            return 'Hexlet'
        elif self.source == 'stepik':
            return 'Stepik'
        return self.source