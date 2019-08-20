from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from django.utils.translation import ugettext_lazy as _

from .models import *


class TarifiActivitySlotResource(resources.ModelResource):
    class Meta:
        model = TarifiActivitySlot
        import_id_fields = ('id',)
        fields = ('id', 'semester', 'type', 'location_ar', 'location_en', 'slots', 'remaining_slots', 'slot_start_date',
                  'slot_end_date', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class TarifiActivitySlotAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('semester', 'type', 'location_ar', 'location_en', 'slots', 'remaining_slots', 'slot_start_date',
                    'slot_end_date', 'show', 'display_order')
    list_filter = ('semester', 'type', 'location_ar', 'location_en')
    search_fields = ['location_ar', 'location_en', 'type', ]
    resource_class = TarifiActivitySlotResource


class TarifiDataAdmin(admin.ModelAdmin):
    list_display = ('admission_request', 'admission_request__kfupm_id', 'admission_request__semester',
                    'preparation_course_slot', 'english_placement_test_slot',
                    'get_english_speaking_test_date_time', 'desk_no',
                    'received_by', 'created_on')
    list_filter = ('admission_request__semester', 'admission_request__status_message', 'admission_request__semester', )
    search_fields = ['admission_request__user__username', 'admission_request__kfupm_id']
    autocomplete_fields = ['admission_request', 'received_by', 'preparation_course_slot',
                           'english_placement_test_slot', 'english_speaking_test_slot',
                           'preparation_course_attended_by', ]

    def admission_request__semester(self, obj):
        return obj.admission_request.semester

    def admission_request__kfupm_id(self, obj):
        return obj.admission_request.kfupm_id

    admission_request__kfupm_id.short_description = _('KFUPM ID')
    admission_request__kfupm_id.admin_order_field = 'admission_request__kfupm_id'


class BoxesForIDRangesResource(resources.ModelResource):
    class Meta:
        model = BoxesForIDRanges
        import_id_fields = ('id',)
        fields = ('id', 'from_kfupm_id', 'to_kfupm_id', 'box_no')
        skip_unchanged = True
        report_skipped = True


class BoxesForIDRangesAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('from_kfupm_id', 'to_kfupm_id', 'box_no')

    resource_class = BoxesForIDRangesResource


class StudentIssueResource(resources.ModelResource):
    class Meta:
        model = StudentIssue
        import_id_fields = ('id',)
        fields = ('id', 'kfupm_id', 'issues', 'show')
        skip_unchanged = True
        report_skipped = True


class StudentIssueAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('kfupm_id', 'issues', 'show')

    resource_class = StudentIssueResource


admin.site.register(TarifiData, TarifiDataAdmin)
admin.site.register(TarifiActivitySlot, TarifiActivitySlotAdmin)
admin.site.register(BoxesForIDRanges, BoxesForIDRangesAdmin)
admin.site.register(StudentIssue, StudentIssueAdmin)
