# Generated by Django 4.2.7 on 2024-03-13 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_remove_restaurant_category_restaurant_address_ru'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='business_2gis',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='business_instagram',
            field=models.TextField(blank=True, null=True),
        ),
    ]
