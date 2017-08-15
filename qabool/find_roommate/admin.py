from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from find_roommate.models import HousingUser, Room, RoommateRequest


class UserHousingAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook', 'twitter', 'sleeping', 'light',
                    'room_temperature', 'visits', 'searchable')

    list_filter = ('searchable', 'user__eligible_for_housing',)


class RoomResource(resources.ModelResource):
    class Meta:
        model = Room
        import_id_fields = ('id',)
        fields = ('id', 'building', 'room', 'available')
        skip_unchanged = True
        report_skipped = True


class RoomAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('__str__', 'building', 'room', 'available', 'residents')
    list_filter = ('available', )
    resource_class = RoomResource


class RoommateRequestAdmin(admin.ModelAdmin):
    list_display = ('requesting_user', 'requesting_user__kfupm_id', 'requested_user', 'requested_user__kfupm_id',
                    'status', 'assigned_room', 'request_date', 'updated_on')

    list_filter = ('status', )

    search_fields = ['requesting_user__kfupm_id', 'requested_user__kfupm_id']


admin.site.register(HousingUser, UserHousingAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoommateRequest, RoommateRequestAdmin)
