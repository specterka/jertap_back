# Generated by Django 4.2.7 on 2023-12-01 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_user_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country_code',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
