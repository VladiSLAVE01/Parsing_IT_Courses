from .models import Task
from django.forms import ModelForm, TextInput, Textarea, URLInput, Select

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']
        widgets = {
            "title": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите название",
            }),
            "description": Textarea(attrs={
                "class": "form-control",
                "placeholder": "Введите описание"
            }),
            'url': URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/course'
            }),
            'source': Select(attrs={
                'class': 'form-select'
            }),
            'price': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Бесплатно или 2990 руб.'
            }),
            'image_url': URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле url обязательным
        self.fields['url'].required = True
        self.fields['title'].required = True

        # Настраиваем placeholder для source
        self.fields['source'].empty_label = "Выберите источник"