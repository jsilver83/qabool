# Generated by Django 2.1.5 on 2019-08-01 10:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tarifi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarifidata',
            name='creation_date',
        ),
        migrations.AddField(
            model_name='tarifidata',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created On'),
        ),
        migrations.AddField(
            model_name='tarifidata',
            name='desk_no',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Desk No'),
        ),
        migrations.AlterField(
            model_name='tarifiactivityslot',
            name='attender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_slots', to=settings.AUTH_USER_MODEL, verbose_name='Attender'),
        ),
        migrations.AlterField(
            model_name='tarifidata',
            name='received_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students_received', to=settings.AUTH_USER_MODEL, verbose_name='Received By'),
        ),
    ]