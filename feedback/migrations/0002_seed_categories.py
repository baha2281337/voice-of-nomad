from django.db import migrations


DEFAULT_CATEGORIES = [
    ('infrastructure', 'Инфраструктура'),
    ('learning-process', 'Учебный процесс'),
    ('cafeteria', 'Столовая'),
    ('equipment', 'Оборудование'),
    ('sanitary-condition', 'Санитарное состояние'),
    ('sports-and-leisure', 'Спорт и отдых'),
    ('safety', 'Безопасность'),
    ('events', 'Мероприятия'),
    ('other', 'Другое'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('feedback', 'Category')
    database = schema_editor.connection.alias
    for order, (slug, name) in enumerate(DEFAULT_CATEGORIES, start=1):
        Category.objects.using(database).update_or_create(
            slug=slug,
            defaults={'name': name, 'sort_order': order * 10, 'is_active': True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
