import floppyforms.__future__ as forms

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportMixin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        import_id_fields = ('username', 'kfupm_id')
        fields = ('semester', 'username', 'high_school_gpa', 'qudrat_score', 'tahsili_score', 'status_message',
                  'birthday', 'birthday_ah', 'high_school_graduation_year', 'kfupm_id', 'first_name_ar',
                  'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en', 'second_name_en',
                  'third_name_en', 'family_name_en', 'high_school_name', 'high_school_system',
                  'high_school_province', 'admission_letter_note', 'admission_note', 'government_id_place',
                  'government_id_expiry', 'birth_place', 'high_school_city', 'phase2_start_date', 'phase2_end_date',
                  'eligible_for_housing', 'english_placement_test_score', 'english_speaking_test_score',
                  'english_level', )
        skip_unchanged = True
        report_skipped = True


class MyUserAdmin(ImportExportMixin, VersionAdmin, UserAdmin):
    list_display = ('id', 'username', 'kfupm_id', 'get_student_full_name', 'email', 'admission_total',
                    'status_message_id', )
    date_hierarchy = 'date_joined'
    fieldsets = UserAdmin.fieldsets + (
        ('Qabool Fields', {
            'fields': ('semester', 'kfupm_id', 'mobile','nationality', 'saudi_mother', 'status_message',
                       'admission_note',
                       'guardian_mobile', 'high_school_graduation_year', 'high_school_system','high_school_gpa',
                       'qudrat_score', 'tahsili_score', 'admission_letter_note', ),
        }),
    )
    resource_class = UserResource


class Student(User):
    class Meta:
        proxy = True


class StudentAdmin(VersionAdmin):
    list_display = ('username', 'kfupm_id', 'get_student_full_name', 'email', 'mobile',
                    'student_type', 'admission_total', 'status_message_id',)
    date_hierarchy = 'date_joined'
    exclude = ('password', 'groups', 'last_login', 'is_superuser', 'is_staff', 'user_permissions')
    readonly_fields = ('username', 'id', 'is_active', 'date_joined')
    search_fields = ['username', 'kfupm_id', 'mobile', 'email', 'nationality__nationality_ar',
                     'nationality__nationality_en']
    list_filter = ('high_school_graduation_year', 'saudi_mother', 'nationality',)

    def get_queryset(self, request):
        qs = self.model.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return qs


class VerifyStudent(User):
    class Meta:
        proxy = True


class VerifyStudentAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('id', ) # dummy but necessary syntactically

    def __init__(self, *args, **kwargs):
        super(VerifyStudentAdminForm, self).__init__(*args, **kwargs)
        self.fields['verification_status'].widget = \
            forms.CheckboxSelectMultiple(choices=Lookup.get_lookup_choices('VERIFICATION_STATUS', False))
        self.fields['verification_notes'].widget = admin.widgets.AdminTextareaWidget()


# TODO: Enhance the form and add script to manage student pictures for the committee.
class VerifyStudentAdmin(VersionAdmin):
    list_display = ('username', 'kfupm_id', 'get_student_full_name', 'email', 'mobile',
                    'high_school_gpa', 'qudrat_score', 'tahsili_score', 'status_message_id', 'student_type', )
    date_hierarchy = 'date_joined'
    list_filter = ('high_school_graduation_year', 'saudi_mother', 'nationality', )
    fields = ('get_student_full_name', 'id', 'kfupm_id', 'username', 'email', 'mobile',
              'is_active', 'date_joined', 'high_school_gpa',
              'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
              'second_name_en', 'third_name_en', 'family_name_en', 'high_school_name', 'high_school_system',
              'high_school_province', 'high_school_city', 'birthday', 'birthday_ah',
              'nationality','saudi_mother', 'birth_place', 'government_id_expiry',
              'personal_picture', 'government_id_file', 'high_school_certificate',
              'courses_certificate', 'mother_gov_id_file', 'birth_certificate', 'passport_file',
              'verification_documents_incomplete', 'get_verification_status', 'verification_status',
              'verification_notes', )
    readonly_fields = ('get_student_full_name', 'id', 'kfupm_id', 'username', 'status_message_id', 'email', 'mobile',
                       'is_active', 'date_joined', 'high_school_gpa', 'get_verification_status',
                       'nationality','saudi_mother', )
    form = VerifyStudentAdminForm
    search_fields = ['username', 'kfupm_id', 'mobile', 'email', 'nationality__nationality_ar',
                     'nationality__nationality_en']

    def get_queryset(self, request):
        qs = self.model.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return qs


class HelpDiskForStudent(User):
    class Meta:
        proxy = True


class HelpDiskForStudentAdmin(VersionAdmin):
    list_display = ('username', 'get_student_full_name', 'email', 'mobile', 'student_type', 'kfupm_id', 'status_message_id')
    date_hierarchy = 'date_joined'
    fields = readonly_fields = ('username', 'get_student_full_name', 'mobile', 'email',
                                'nationality', 'saudi_mother', 'status_message',
                                'guardian_mobile', 'id',
                                'date_joined', 'high_school_graduation_year', 'kfupm_id',
                                'high_school_name', 'high_school_province', 'high_school_gpa', )
    search_fields = ['username', 'mobile', 'email', 'nationality__nationality_ar',
                     'nationality__nationality_en', 'kfupm_id']
    list_filter = ('high_school_graduation_year', 'saudi_mother', 'nationality',)

    def get_queryset(self, request):
        qs = self.model.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return qs

class StatusMessagesInline(admin.TabularInline):
    model = RegistrationStatusMessage

class RegistrationStatusAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('status_ar', 'status_en', 'status_code')
    inlines = [
        StatusMessagesInline,
    ]


class NationalityAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'nationality_ar', 'nationality_en', 'show', 'display_order')
    search_fields = ['nationality_en']


class DistinguishedStudentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('government_id', 'student_name', 'city', 'attended')
    search_fields = ['government_id',]


class DeniedStudentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('government_id', 'student_name', 'message', 'semester')
    search_fields = ['government_id',]


class KFUPMIDsPoolResource(resources.ModelResource):
    class Meta:
        model = KFUPMIDsPool
        import_id_fields = ('id',)
        fields = ('id', 'semester', 'kfupm_id', )
        skip_unchanged = True
        report_skipped = True


class KFUPMIDsPoolAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('semester', 'kfupm_id', )
    resource_class = KFUPMIDsPoolResource


class AgreementItemResource(resources.ModelResource):
    class Meta:
        model = AgreementItem
        import_id_fields = ('id',)
        fields = ('agreement', 'agreement_text_ar', 'agreement_text_en', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class AgreementItemAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('agreement', 'agreement_text_ar', 'agreement_text_en', 'show', 'display_order')
    list_filter = ('agreement',)
    resource_class = AgreementItemResource


# class AgreementItemInline(admin.TabularInline):
#         model = AgreementItem
#
# class AgreementAdmin(admin.ModelAdmin):
#     inlines = [
#         AgreementItemInline,
#     ]

class LookupResource(resources.ModelResource):
    class Meta:
        model = Lookup
        import_id_fields = ('id',)
        fields = ('id', 'lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class LookupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
    list_filter = ('lookup_type',)
    resource_class = LookupResource


class RegistrationStatusMessageResource(resources.ModelResource):
    class Meta:
        model = RegistrationStatusMessage
        import_id_fields = ('id',)
        # import_id_fields = ('status_message_code',)
        fields = ('status_message_ar', 'status_message_en', 'status_message_code', 'status_id', 'id')
        skip_unchanged = True
        report_skipped = True


class RegistrationStatusMessageAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('status_message_ar', 'status_message_en', 'status_message_code', 'status_id', 'id')
    resource_class = RegistrationStatusMessageResource


# Update selected students status to (admitted). You can see the message id No.1 in RegistrationStatusMessage model.
def Mark_Partial_Admitted(modeladmin, request, queryset):
    queryset.update(status_message_id='1')
    Mark_Partial_Admitted.short_description = "Mark as Partial Admitted"

# Update selected students status to (rejected). You can see the message id No.3 in RegistrationStatusMessage model.
def Mark_Rejected(modeladmin, request, queryset):
    queryset.update(status_message_id='3')
    Mark_Rejected.short_description = "Mark as Rejected"
# TODO: Should we do in the admin dashboard or in the front-end using template?.


# class CutOff(User):
#     class Meta:
#         proxy = True


# TODO: display specific fields with criteria and enhance the search field.
# class CutOffAdmin(admin.ModelAdmin):
#     list_display = ('username', 'kfupm_id', 'get_student_full_name', 'mobile',
#                     'status_message_id', 'student_type',)
#     # date_hierarchy = 'date_joined'
#     list_filter = ('high_school_graduation_year', 'saudi_mother', 'nationality',)
#     fields = ('get_student_full_name', 'id', 'kfupm_id', 'username', 'email', 'mobile',
#               'is_active', 'date_joined', 'high_school_gpa',
#               'first_name_ar', 'second_name_ar', 'third_name_ar', 'family_name_ar', 'first_name_en',
#               'second_name_en', 'third_name_en', 'family_name_en', 'high_school_name', 'high_school_system',
#               'high_school_province', 'high_school_city', 'birthday', 'birthday_ah',
#               'nationality', 'saudi_mother', 'birth_place', 'government_id_expiry',
#               'personal_picture', 'government_id_file', 'high_school_certificate',
#               'courses_certificate', 'mother_gov_id_file', 'birth_certificate', 'passport_file',
#               'verification_documents_incomplete', 'get_verification_status', 'verification_status',
#               'verification_notes',)
#     readonly_fields = ('get_student_full_name', 'id', 'kfupm_id', 'username', 'status_message_id', 'email', 'mobile',
#                        'is_active', 'date_joined', 'high_school_gpa', 'get_verification_status',
#                        'nationality', 'saudi_mother',)
#
#     search_fields = ['username', 'kfupm_id', 'mobile', 'email', 'nationality__nationality_ar',
#                      'nationality__nationality_en']
#     actions = [Mark_Partial_Admitted, Mark_Rejected]


class TarifiReceptionDateAdmin(admin.ModelAdmin):
    list_display = ('semester', 'reception_date', 'slots', 'remaining_slots', 'slot_start_date', 'slot_end_date', )
    list_filter = ('semester', )

# Display Qabool in the page title and header
admin.site.site_header = _('Qabool')
admin.site.index_title = _('Qabool Administration')
admin.site.site_title = _('Administration')

admin.site.register(TarifiReceptionDate, TarifiReceptionDateAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(ImportantDateSidebar)
admin.site.register(RegistrationStatus, RegistrationStatusAdmin)
# Use TabularInline in the RegistrationStatusMessage model.
admin.site.register(RegistrationStatusMessage, RegistrationStatusMessageAdmin)
admin.site.register(City)
admin.site.register(DeniedStudent, DeniedStudentAdmin)
admin.site.register(GraduationYear)
# Use TabularInline in the Agreement model.
# admin.site.register(Agreement, AgreementAdmin)
admin.site.register(Agreement)
admin.site.register(AgreementItem, AgreementItemAdmin)
admin.site.register(AdmissionSemester)
admin.site.register(User, MyUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(HelpDiskForStudent, HelpDiskForStudentAdmin)
admin.site.register(Lookup, LookupAdmin)
admin.site.register(DistinguishedStudent, DistinguishedStudentAdmin)
admin.site.register(KFUPMIDsPool, KFUPMIDsPoolAdmin)
admin.site.register(VerifyStudent, VerifyStudentAdmin)
# admin.site.register(CutOff, CutOffAdmin)