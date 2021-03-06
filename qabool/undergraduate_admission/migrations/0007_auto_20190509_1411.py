# Generated by Django 2.1.5 on 2019-05-09 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0006_auto_20190505_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='admissionrequest',
            name='phase2_re_upload_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Phase 2 Re-Upload Date'),
        ),
        migrations.AlterField(
            model_name='admissionrequest',
            name='request_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Request Date'),
        ),
    ]
