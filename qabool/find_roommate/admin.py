from django.contrib import admin

from find_roommate.models import HousingUser


class UserHousingAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook', 'twitter', 'sleeping', 'light',
                    'room_temperature', 'visits', 'searchable')

    list_filter = ('searchable', 'user__eligible_for_housing',)


admin.site.register(HousingUser, UserHousingAdmin)