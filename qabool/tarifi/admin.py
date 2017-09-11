from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

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
    resource_class = TarifiActivitySlotResource


class TarifiUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'user__kfupm_id', 'preparation_course_slot', 'english_placement_test_slot',
                    'get_english_speaking_test_date_time',
                    'received_by', 'creation_date')
    list_filter = ('user__semester', 'user__status_message',)


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


admin.site.register(TarifiUser, TarifiUserAdmin)
admin.site.register(TarifiActivitySlot, TarifiActivitySlotAdmin)
admin.site.register(BoxesForIDRanges, BoxesForIDRangesAdmin)
admin.site.register(StudentIssue, StudentIssueAdmin)
