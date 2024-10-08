# Generated by Django 4.2.7 on 2024-01-10 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_clamrequest_is_approved'),
        ('owner_dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurantnotification',
            name='user',
        ),
        migrations.AddField(
            model_name='restaurantnotification',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.restaurant'),
            preserve_default=False,
        ),
    ]
