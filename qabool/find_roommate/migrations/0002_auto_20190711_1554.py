# Generated by Django 2.1.5 on 2019-07-11 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('find_roommate', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='housinguser',
            options={'ordering': ('user__first_name_ar',)},
        ),
    ]
