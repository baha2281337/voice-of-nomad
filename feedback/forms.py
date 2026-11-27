from django import forms

from .models import Category, Feedback


class FeedbackSubmissionForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('kind', 'category', 'title', 'description', 'location', 'is_anonymous')
        labels = {
            'kind': 'Тип обращения',
            'category': 'Категория',
            'title': 'Заголовок',
            'description': 'Описание',
            'location': 'Место (необязательно)',
            'is_anonymous': 'Опубликовать анонимно',
        }
        help_texts = {
            'is_anonymous': 'Ваш аккаунт сохранится для связи с администрацией, но имя не будет видно в общей ленте.',
        }
        widgets = {
            'kind': forms.Select(attrs={'class': 'text-input'}),
            'category': forms.Select(attrs={'class': 'text-input'}),
            'title': forms.TextInput(attrs={
                'class': 'text-input',
                'maxlength': 160,
                'placeholder': 'Кратко сформулируйте тему',
            }),
            'description': forms.Textarea(attrs={
                'class': 'text-input',
                'rows': 5,
                'placeholder': 'Опишите предложение или проблему подробнее',
            }),
            'location': forms.TextInput(attrs={
                'class': 'text-input',
                'maxlength': 160,
                'placeholder': 'Например, корпус или аудитория',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
