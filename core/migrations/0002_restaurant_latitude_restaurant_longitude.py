# Generated by Django 4.2.7 on 2023-11-07 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
