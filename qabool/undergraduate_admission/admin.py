import time

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportMixin
from pagedown.widgets import AdminPagedownWidget
from reversion.admin import VersionAdmin

from undergraduate_admission.views.admin_side_views import get_student_record_serialized
from .forms.phase2_forms import YES_NO_CHOICES
from .models import *


class StudentResource(resources.ModelResource):
    class Meta:
        model = AdmissionRequest
        exclude = ('id',)
        # import_id_fields = ('username',)
        fields = ('semester', 'high_school_gpa', 'qudrat_score', 'tahsili_score', 'status_message',
                  'birthday', 'birthday_ah', 'high_school_graduation_year', 'kfupm_id', 'first_name_ar',
                  'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en', 'second_name_en',
                  'third_name_en', 'family_name_en', 'high_school_name', 'high_school_system',
                  'high_school_province', 'admission_note', 'admission_note2', 'admission_note3', 'government_id_place',
                  'government_id_expiry', 'birth_place', 'high_school_city', 'phase2_start_date', 'phase2_end_date',
                  'eligible_for_housing', 'high_school_gpa_student_entry', 'student_full_name_ar',
                  'student_full_name_en', 'gender', 'verification_committee_member',
                  'email', 'mobile', 'nationality', 'guardian_mobile', 'student_notes', )
        skip_unchanged = True
        report_skipped = True


class AdmissionRequestAdmin(ImportExportMixin, VersionAdmin):
    list_display = ('government_id', 'semester', 'kfupm_id', 'get_student_full_name', 'mobile',
                    'student_type', 'admission_total', 'status_message', )

    fieldsets = (
        (None, {
            'fields': (('user', 'government_id', 'semester', 'status_message', 'gender', ),
                       ('first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar'),
                       ('first_name_en', 'second_name_en', 'third_name_en', 'family_name_en'),
                       ('student_type', 'nationality', 'saudi_mother', 'saudi_mother_gov_id'),
                       'mobile', 'guardian_mobile',
                       ('high_school_gpa', 'qudrat_score', 'tahsili_score', 'admission_total', ),
                       'high_school_gpa_student_entry',
                       ('high_school_graduation_year', 'high_school_system'),
                       ('show_docs_links',),
                       'student_notes',
                       ('admission_note', 'admission_note2', 'admission_note3', ), )
        }),
        ('Important Dates', {
            'classes': ('collapse',),
            'fields': ('phase2_start_date', 'phase2_end_date',
                       'phase3_start_date', 'phase3_end_date',),
        }),
        ('Committee Fields', {
            'classes': ('collapse',),
            'fields': ('verification_committee_member',
                       'verification_issues',
                       'verification_notes'),
        }),
        ('Phase 3 Fields', {
            'classes': ('collapse',),
            'fields': (
                'kfupm_id',
                'admission_letter_print_date', 'medical_report_print_date', 'phase3_submit_date'),
        }),
        ('Withdrawal Fields', {
            'classes': ('collapse',),
            'fields': ('withdrawal_date', 'withdrawal_university', 'withdrawal_reason'),

        }),
        ('Awareness Week Fields', {
            'classes': ('collapse',),
            'fields': ('eligible_for_housing',
                       'tarifi_week_attendance_date', ),

        }),
        ('Yesser Data Dump', {
            'classes': ('collapse',),
            'fields': (
                ('show_yesser_high_school_data_dump', ),
                ('show_yesser_qudrat_data_dump', ),
                ('show_yesser_tahsili_data_dump', ),
            ),
        }),

        ('Phase 2 Fields - Uploaded Documents', {
            'classes': ('collapse',),
            'fields': ('high_school_certificate',
                       'personal_picture',
                       'mother_gov_id_file',
                       'birth_certificate',
                       'government_id_file',
                       'passport_file',
                       'courses_certificate',
                       ),
        }),
        ('Phase 2 Fields - Personal Information', {
            'classes': ('collapse',),
            'fields': (
                       ('government_id_type', 'government_id_issue', 'government_id_expiry', 'government_id_place', ),
                       ('passport_number', 'passport_place', 'passport_expiry', ),
                       ('birthday', 'birthday_ah', 'birth_place', ),
                       ('high_school_id', 'high_school_name', 'high_school_name_en', ),
                       ('high_school_province_code', 'high_school_province', 'high_school_province_en', ),
                       ('high_school_city_code', 'high_school_city', 'high_school_city_en', ),
                       ('high_school_major_code', 'high_school_major_name', 'high_school_major_name_en', ),
                       ('blood_type', 'student_address', ),
                       ('social_status', 'kids_no', ),
                       ('is_employed', 'employer_name', ),
                       ('is_disabled', 'disability_needs', 'disability_needs_notes', ),
                       ('is_diseased', 'chronic_diseases', 'chronic_diseases_notes', ), 'phase2_submit_date'
                       ),
        }),
        ('Phase 2 Fields - Vehicle Info', {
            'classes': ('collapse',),
            'fields': (
                       'have_a_vehicle', 'vehicle_owner', 'vehicle_plate_no',
                       ('driving_license_file', 'vehicle_registration_file')
            ),
        }),
        ('Phase 2 Fields - Guardian Information', {
            'classes': ('collapse',),
            'fields': (
                'guardian_name', 'guardian_government_id', 'guardian_relation', 'guardian_email',
                'guardian_po_box', 'guardian_postal_code', 'guardian_city', 'guardian_job', 'guardian_employer',
            ),
        }),
        ('Phase 2 Fields - Relative Information', {
            'classes': ('collapse',),
            'fields': (
                'relative_name', 'relative_relation', 'relative_phone', 'relative_po_box', 'relative_postal_code',
                'relative_city', 'relative_job', 'relative_employer',
            ),
        }),
        ('Phase 2 Fields - Bank Account', {
            'classes': ('collapse',),
            'fields': (
                'bank_name', 'bank_account', 'bank_account_identification_file',
            ),
        }),
    )
    date_hierarchy = 'request_date'
    readonly_fields = ('id', 'government_id', 'student_type', 'admission_total', 'phase2_submit_date',
                       'phase3_submit_date', 'admission_letter_print_date', 'medical_report_print_date',
                       'show_docs_links', 'show_yesser_high_school_data_dump', 'show_yesser_qudrat_data_dump',
                       'show_yesser_tahsili_data_dump', )
    search_fields = ['user__username', 'kfupm_id', 'mobile', 'email',
                     'nationality', 'student_full_name_ar', 'student_full_name_en', ]
    list_filter = ('semester', 'high_school_graduation_year', 'gender', 'status_message__general_status',
                   'status_message', 'nationality',)
    actions = ['yesser_update']
    resource_class = StudentResource

    def make_yesser_data_dump_readable(self, obj, which_dump):
        attr = getattr(obj, which_dump)

        if attr:
            html_to_be_displayed = '<div style="direction:ltr"><br><br>' \
                                   '==============================================<br>'
            attr = attr.replace('\n', '<br>').replace('\'', '').replace('{', '').replace('}', '').replace(' ', '&nbsp;')
            html_to_be_displayed += attr + '==============================================<br></div>'
            return format_html(html_to_be_displayed)

    def show_yesser_high_school_data_dump(self, obj):
        return self.make_yesser_data_dump_readable(obj, 'yesser_high_school_data_dump')

    def show_yesser_qudrat_data_dump(self, obj):
        return self.make_yesser_data_dump_readable(obj, 'yesser_qudrat_data_dump')

    def show_yesser_tahsili_data_dump(self, obj):
        return self.make_yesser_data_dump_readable(obj, 'yesser_tahsili_data_dump')

    show_yesser_high_school_data_dump.short_description = _('Fetched Yesser High School Data Dump')
    show_yesser_qudrat_data_dump.short_description = _('Fetched Yesser Qudrat Data Dump')
    show_yesser_tahsili_data_dump.short_description = _('Fetched Yesser Tahsili Data Dump')

    def show_docs_links(self, obj):
        docs_links_html = '<br><br>'

        if obj.high_school_certificate:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('High School Certificate'),
                                           url=reverse('download_user_file_admin', args=('high_school_certificate', obj.id)))
        if obj.personal_picture:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Personal Picture'),
                                           url=reverse('download_user_file_admin', args=('personal_picture', obj.id)))
        if obj.mother_gov_id_file:
            docs_links_html += format_html("<a href='{url} target='_blank'>{text}</a><br>",
                                           text=_('Mother Government ID'),
                                           url=reverse('download_user_file_admin', args=('mother_gov_id_file', obj.id)))
        if obj.birth_certificate:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Birth Date Certificate'),
                                           url=reverse('download_user_file_admin', args=('birth_certificate', obj.id)))
        if obj.government_id_file:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Government ID File'),
                                           url=reverse('download_user_file_admin', args=('government_id_file', obj.id)))
        if obj.passport_file:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Upload Passport'),
                                           url=reverse('download_user_file_admin', args=('passport_file', obj.id)))
        if obj.courses_certificate:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Courses Certificate'),
                                           url=reverse('download_user_file_admin', args=('courses_certificate', obj.id)))
        if obj.vehicle_registration_file:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Vehicle Registration File'),
                                           url=reverse('download_user_file_admin', args=('vehicle_registration_file', obj.id)))

        if obj.driving_license_file:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Driving License File'),
                                           url=reverse('download_user_file_admin', args=('driving_license_file', obj.id)))

        if obj.bank_account_identification_file:
            docs_links_html += format_html("<a href='{url}' target='_blank'>{text}</a><br>",
                                           text=_('Bank Account Identification File'),
                                           url=reverse('download_user_file_admin',
                                                       args=('bank_account_identification_file', obj.id)))

        return format_html(docs_links_html)

    show_docs_links.short_description = _("Documents")

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(AdmissionRequestAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in['admission_note', 'admission_note2', 'admission_note3']:
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)

        if db_field.name == 'high_school_system':
            formfield.widget = forms.Select(choices=Lookup.get_lookup_choices('HIGH_SCHOOL_TYPE'))

        if db_field.name in ['have_a_vehicle', 'is_employed', 'is_disabled', 'is_diseased']:
            formfield.widget = forms.RadioSelect(choices=YES_NO_CHOICES)

        if db_field.name == 'guardian_relation':
            formfield.widget = forms.Select(choices=Lookup.get_lookup_choices('PERSON_RELATION'))

        if db_field.name == 'social_status':
            formfield.widget = forms.RadioSelect(choices=Lookup.get_lookup_choices('SOCIAL_STATUS', False))

        if db_field.name == 'disability_needs':
            formfield.widget = forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('DISABILITY', False))

        if db_field.name == 'chronic_diseases':
            formfield.widget = forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('CHRONIC_DISEASES', False))

        if db_field.name == 'blood_type':
            formfield.widget = forms.Select(choices=Lookup.get_lookup_choices('BLOOD_TYPE', add_dashes=True))

        return formfield

    # Update selected students and sync them with Yesser
    def yesser_update(self, request, queryset):
        log = ''
        changed_students = 0
        for student in queryset:
            time.sleep(0.2)
            result = get_student_record_serialized(student, True)
            if result['changed']:
                changed_students += 1
            # if result['log']:
            #     log += '<br>' + result['log']

        self.message_user(request, "%d student(s) were successfully sync'd with yesser." % changed_students)

    yesser_update.short_description = _("Sync with Yesser")

    def get_queryset(self, request):
        return self.model.objects.all().order_by('request_date')


class StatusMessagesInline(admin.TabularInline):
    model = RegistrationStatus


class DeniedStudentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('semester', 'government_id', 'student_name', 'message',
                    'last_trial_date', 'trials_count')
    search_fields = ['government_id', ]


class KFUPMIDsPoolResource(resources.ModelResource):
    class Meta:
        model = KFUPMIDsPool
        import_id_fields = ('id',)
        fields = ('id', 'semester', 'kfupm_id',)
        skip_unchanged = True
        report_skipped = True


class KFUPMIDsPoolAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('semester', 'kfupm_id', 'assigned_student',)
    resource_class = KFUPMIDsPoolResource
    search_fields = ['kfupm_id']
    list_filter = ['semester']


class LookupResource(resources.ModelResource):
    class Meta:
        model = Lookup
        import_id_fields = ('id',)
        fields = ('id', 'lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class ImportantDateSidebarResource(resources.ModelResource):
    class Meta:
        model = ImportantDateSidebar
        import_id_fields = ('id',)
        fields = ('title_ar', 'title_en', 'description_ar', 'description_en', 'show', 'display_order', 'id')
        skip_unchanged = True
        report_skipped = True


class ImportantDateSidebarAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('title_ar', 'description_ar', 'show', 'display_order')
    resource_class = ImportantDateSidebarResource


class LookupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
    list_filter = ('lookup_type',)
    resource_class = LookupResource


class RegistrationStatusResource(resources.ModelResource):
    class Meta:
        model = RegistrationStatus
        import_id_fields = ('id',)
        fields = ('general_status', 'status_message_ar', 'status_message_en', 'status_message_code', 'id')
        skip_unchanged = True
        report_skipped = True


class RegistrationStatusAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('general_status', 'status_message_code', 'status_message_ar', 'status_message_en', 'id')
    resource_class = RegistrationStatusResource


class AdmissionSemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_name', 'phase1_start_date', 'phase1_end_date', 'phase2_start_date', 'phase2_end_date',
                    'phase3_start_date', 'phase3_end_date', 'high_school_gpa_weight', 'qudrat_score_weight',
                    'tahsili_score_weight',)


class GraduationYearAdmin(admin.ModelAdmin):
    list_display = ('graduation_year_ar', 'graduation_year_en', 'description', 'show', 'display_order',)


class TarifiReceptionDateAdmin(admin.ModelAdmin):
    list_display = ('semester', 'reception_date', 'slots', 'remaining_slots', 'slot_start_date', 'slot_end_date',)
    list_filter = ('semester',)


class AgreementAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }
    list_display = ('id', 'semester', 'agreement_type', 'show')
    list_filter = ('agreement_type',)


class VerificationIssuesAdmin(admin.ModelAdmin):
    list_display = ('semester', 'agreement_type', 'show')


# Display Qabool in the page title and header
admin.site.site_header = _('Qabool')
admin.site.index_title = _('Qabool Administration')
admin.site.site_title = _('Administration')

admin.site.register(TarifiReceptionDate, TarifiReceptionDateAdmin)
admin.site.register(ImportantDateSidebar, ImportantDateSidebarAdmin)
admin.site.register(RegistrationStatus, RegistrationStatusAdmin)
admin.site.register(City)
admin.site.register(VerificationIssues)
admin.site.register(DeniedStudent, DeniedStudentAdmin)
admin.site.register(GraduationYear, GraduationYearAdmin)
admin.site.register(Agreement, AgreementAdmin)
admin.site.register(AdmissionSemester, AdmissionSemesterAdmin)
admin.site.register(AdmissionRequest, AdmissionRequestAdmin)
admin.site.register(Lookup, LookupAdmin)
admin.site.register(KFUPMIDsPool, KFUPMIDsPoolAdmin)
