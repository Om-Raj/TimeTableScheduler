# Generated by Django 5.1.7 on 2025-06-25 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('days_per_week', models.PositiveSmallIntegerField(default=5)),
                ('slots_per_day', models.PositiveSmallIntegerField(default=8)),
            ],
        ),
    ]
