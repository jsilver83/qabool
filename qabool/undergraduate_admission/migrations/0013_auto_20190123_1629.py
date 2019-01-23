# Generated by Django 2.1.5 on 2019-01-23 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('undergraduate_admission', '0012_auto_20190121_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agreementitem',
            name='agreement',
        ),
        migrations.DeleteModel(
            name='HelpDiskForStudent',
        ),
        migrations.AlterModelOptions(
            name='registrationstatusmessage',
            options={'ordering': ('display_order',), 'verbose_name_plural': 'Admission: Registration Status Messages'},
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='agreement_footer_ar',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='agreement_footer_en',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='agreement_header_ar',
        ),
        migrations.RemoveField(
            model_name='agreement',
            name='agreement_header_en',
        ),
        migrations.RemoveField(
            model_name='registrationstatusmessage',
            name='status',
        ),
        migrations.AddField(
            model_name='agreement',
            name='agreement_text_ar',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='Agreement Text (Arabic)'),
        ),
        migrations.AddField(
            model_name='agreement',
            name='agreement_text_en',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='Agreement Text (English)'),
        ),
        migrations.AddField(
            model_name='agreement',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Show'),
        ),
        migrations.AddField(
            model_name='agreement',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='status_messages', to='undergraduate_admission.RegistrationStatusMessage', verbose_name='Status Message'),
        ),
        migrations.AddField(
            model_name='registrationstatusmessage',
            name='admin_note',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Admin note'),
        ),
        migrations.AddField(
            model_name='registrationstatusmessage',
            name='display_order',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Display Order'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='agreement_type',
            field=models.CharField(choices=[('INITIAL', 'Initial agreements'), ('CONFIRMED', 'Confirmation agreements'), ('CONFIRMED-N', 'Confirmation agreements for None Saudi'), ('CONFIRMED-T', 'Confirmation agreements for Transfer students'), ('STUDENT-AGREEMENT_1', 'Student agreements 1'), ('STUDENT-AGREEMENT_2', 'Student agreements 2'), ('STUDENT-AGREEMENT_3', 'Student agreements 3'), ('STUDENT-AGREEMENT_4', 'Student agreements 4'), ('HOUSING-AGREEMENT', 'Student Housing: Initial agreements'), ('HOUSING-ROOMMATE-REQUEST-AGREEMENT', 'Student Housing: Request agreements'), ('HOUSING-ROOMMATE-SEARCH-INSTRUCTIONS', 'Student Housing: Search Instructions'), ('HOUSING-ROOMMATE-REQUEST-INSTRUCTIONS', 'Student Housing: Request Instructions'), ('AWARENESS-WEEK-AGREEMENT', 'Awareness week agreements')], max_length=100, null=True, verbose_name='Agreement Type'),
        ),
        migrations.AlterField(
            model_name='agreement',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agreements', to='undergraduate_admission.AdmissionSemester', verbose_name='Semester'),
        ),
        migrations.AlterField(
            model_name='registrationstatusmessage',
            name='status_message_ar',
            field=models.TextField(max_length=1000, verbose_name='Registration Status Message AR'),
        ),
        migrations.AlterField(
            model_name='registrationstatusmessage',
            name='status_message_code',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='registrationstatusmessage',
            name='status_message_en',
            field=models.TextField(max_length=1000, verbose_name='Registration Status Message EN'),
        ),
        migrations.DeleteModel(
            name='AgreementItem',
        ),
    ]
