# Generated by Django 4.2.7 on 2024-02-07 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_restaurantservice_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='reported',
            field=models.BooleanField(default=False),
        ),
    ]
