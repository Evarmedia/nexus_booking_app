# Generated by Django 5.1.6 on 2025-03-05 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_alter_hairstylist_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hairstylist',
            name='user',
        ),
    ]
