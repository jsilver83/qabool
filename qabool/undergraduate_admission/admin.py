from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *
# Register your models here.


class UserAdmin(VersionAdmin):
    list_display = ('username', 'first_name', 'email', 'status_message_id')
    date_hierarchy = 'date_joined'
    exclude = ('password',)


class HelpDiskForStudent(User):
    class Meta:
        proxy = True


class HelpDiskForStudentAdmin(VersionAdmin):
    list_display = ('username', 'first_name', 'email', 'mobile', 'status_message_id', 'get_student_type')
    date_hierarchy = 'date_joined'
    fields = readonly_fields = ('username', 'first_name',
                                'last_name', 'mobile', 'email',
                                'nationality', 'saudi_mother', 'status_message',
                                'date_joined', 'high_school_graduation_year')
    search_fields = ['username', 'mobile', 'email', 'nationality__nationality_ar', 'nationality__nationality_en']

    def get_queryset(self, request):
        qs = self.model.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        return qs


class UserAuth(User):
    class Meta:
        proxy = True


class UserAuthAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'email', 'status_message_id')
    date_hierarchy = 'date_joined'
    fields = ('first_name', 'last_name', 'mobile', 'is_staff', 'is_superuser', 'is_active', 'groups')


class RegistrationStatusAdmin(admin.ModelAdmin):
    list_display = ('status_ar', 'status_en', 'status_code')


class RegistrationStatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_message_ar', 'status_message_en', 'status_id')


class NationalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'nationality_ar', 'nationality_en', 'show', 'display_order')
    search_fields = ['nationality_en']


class AgreementItemAdmin(admin.ModelAdmin):
    list_display = ('agreement_text_ar', 'agreement_text_en', 'show', 'display_order')


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
admin.site.register(UserAuth, UserAuthAdmin)
