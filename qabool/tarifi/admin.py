from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from .models import TarifiActivitySlot, TarifiUser


class TarifiActivitySlotResource(resources.ModelResource):
    class Meta:
        model = TarifiActivitySlot
        import_id_fields = ('id',)
        fields = ('semester', 'type', 'location_ar', 'location_en', 'slots', 'remaining_slots', 'slot_start_date',
                  'slot_end_date', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class TarifiActivitySlotAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('semester', 'type', 'location_ar', 'location_en', 'slots', 'remaining_slots', 'slot_start_date',
                    'slot_end_date', 'show', 'display_order')
    list_filter = ('semester', 'type', 'location_ar', 'location_en')
    resource_class = TarifiActivitySlotResource


class TarifiUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'preparation_course_attendance_date', 'english_placement_test_date',
                    'english_speaking_test_date', 'english_placement_test_score', 'english_speaking_test_score',
                    'english_level', )
    list_filter = ('user__semester', 'user__status_message',)


admin.site.register(TarifiUser, TarifiUserAdmin)
admin.site.register(TarifiActivitySlot, TarifiActivitySlotAdmin)
