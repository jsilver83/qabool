# Generated by Django 2.1.5 on 2019-07-11 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0007_auto_20190509_1411'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verificationissues',
            options={'ordering': ['-related_field', '-display_order'], 'verbose_name_plural': 'Verification Issues'},
        ),
    ]
