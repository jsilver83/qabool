from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from reversion.admin import VersionAdmin

from .models import *
# Register your models here.


class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'email', 'status_message_id')
    date_hierarchy = 'date_joined'
    fieldsets = UserAdmin.fieldsets + (
        ('Qabool Fileds', {
            'fields': ('mobile','nationality', 'saudi_mother', 'status_message',
                       'guardian_mobile', 'high_school_graduation_year'),
        }),
    )


class HelpDiskForStudent(User):
    class Meta:
        proxy = True


class HelpDiskForStudentAdmin(VersionAdmin):
    list_display = ('username', 'first_name', 'email', 'mobile', 'status_message_id', 'get_student_type')
    date_hierarchy = 'date_joined'
    fields = readonly_fields = ('username', 'first_name',
                                'last_name', 'mobile', 'email',
                                'nationality', 'saudi_mother', 'status_message',
                                'guardian_mobile', 'id',
                                'date_joined', 'high_school_graduation_year')
    search_fields = ['username', 'mobile', 'email', 'nationality__nationality_ar', 'nationality__nationality_en']
    list_filter = ('high_school_graduation_year', 'saudi_mother', 'nationality',)

    def get_queryset(self, request):
        qs = self.model.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return qs


class RegistrationStatusAdmin(admin.ModelAdmin):
    list_display = ('status_ar', 'status_en', 'status_code')


class RegistrationStatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_message_ar', 'status_message_en', 'status_id')


class NationalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'nationality_ar', 'nationality_en', 'show', 'display_order')
    search_fields = ['nationality_en']


class AgreementItemAdmin(admin.ModelAdmin):
    list_display = ('agreement_text_ar', 'agreement_text_en', 'show', 'display_order')


class LookupAdmin(admin.ModelAdmin):
    list_display = ('lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
    list_filter = ('lookup_type',)


class DistinguishedStudentAdmin(admin.ModelAdmin):
    list_display = ('government_id', 'student_name', 'city', 'attended')
    search_fields = ['government_id',]


admin.site.register(Nationality, NationalityAdmin)
admin.site.register(RegistrationStatus, RegistrationStatusAdmin)
admin.site.register(RegistrationStatusMessage, RegistrationStatusMessageAdmin)
admin.site.register(City)
admin.site.register(DeniedStudent)
admin.site.register(GraduationYear)
admin.site.register(Agreement)
admin.site.register(AgreementItem, AgreementItemAdmin)
admin.site.register(AdmissionSemester)
admin.site.register(User, UserAdmin)
admin.site.register(HelpDiskForStudent, HelpDiskForStudentAdmin)
admin.site.register(Lookup, LookupAdmin)
admin.site.register(DistinguishedStudent, DistinguishedStudentAdmin)

