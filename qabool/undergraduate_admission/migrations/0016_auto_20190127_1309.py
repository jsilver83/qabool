# Generated by Django 2.1.5 on 2019-01-27 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0015_auto_20190127_1258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admissionrequest',
            name='verification_documents_incomplete',
        ),
        migrations.RemoveField(
            model_name='admissionrequest',
            name='verification_picture_acceptable',
        ),
        migrations.RemoveField(
            model_name='admissionrequest',
            name='verification_status',
        ),
    ]