# Generated by Django 4.2.7 on 2024-03-13 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_alter_category_icon_alter_subcategory_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='category',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='address_ru',
            field=models.TextField(blank=True, null=True),
        ),
    ]
