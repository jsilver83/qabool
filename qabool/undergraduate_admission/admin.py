from django.contrib import admin

from .models import *
from reversion.admin import VersionAdmin
# Register your models here.


class UserAdmin(VersionAdmin):
    list_display = ('username', 'first_name', 'email', 'status_message_id')
    date_hierarchy = 'date_joined'
    exclude = ('password',)


class UserHelpDisk(User):
    class Meta:
        proxy = True


class UserHelpDiskAdmin(VersionAdmin):
    list_display = ('username', 'first_name', 'email', 'status_message_id')
    date_hierarchy = 'date_joined'
    exclude = ('password',)


class RegistrationStatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_message_ar', 'status_message_en', 'status_id')

admin.site.register(Nationality)
admin.site.register(RegistrationStatus)
admin.site.register(RegistrationStatusMessage, RegistrationStatusMessageAdmin)
admin.site.register(City)
admin.site.register(DeniedStudent)
admin.site.register(GraduationYear)
admin.site.register(Agreement)
admin.site.register(AgreementItem)
admin.site.register(AdmissionSemester)
admin.site.register(User, UserAdmin)
admin.site.register(UserHelpDisk, UserHelpDiskAdmin)
