# Generated by Django 4.2.7 on 2024-05-17 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_user_email_alter_user_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
