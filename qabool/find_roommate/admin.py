from django.contrib import admin

from find_roommate.models import HousingUser, Room, RoommateRequest


class UserHousingAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook', 'twitter', 'sleeping', 'light',
                    'room_temperature', 'visits', 'searchable')

    list_filter = ('searchable', 'user__eligible_for_housing',)


class RoomAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'building', 'room', 'available')

    list_filter = ('available', )


class RoommateRequestAdmin(admin.ModelAdmin):
    list_display = ('requesting_user', 'requested_user', 'status', 'assigned_room', 'request_date', 'updated_on')

    list_filter = ('status', )


admin.site.register(HousingUser, UserHousingAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoommateRequest, RoommateRequestAdmin)
