# Generated by Django 4.0.4 on 2024-09-26 08:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('borrowings', '0002_alter_borrowing_actual_return_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowing',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
