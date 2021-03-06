# Generated by Django 2.1.5 on 2019-04-15 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationissues',
            name='related_field',
            field=models.CharField(choices=[('government_id_file', 'Government ID File'), ('personal_picture', 'Personal Picture'), ('high_school_certificate', 'High School Certificate'), ('courses_certificate', 'Courses Certificate'), ('mother_gov_id_file', 'Mother Government ID'), ('passport_file', 'Upload Passport'), ('birth_certificate', 'Birth Date Certificate')], db_index=True, max_length=50, null=True, verbose_name='Related Field'),
        ),
    ]
