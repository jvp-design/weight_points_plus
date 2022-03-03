from django.contrib import admin
from .models import Activity, ActivityInstance


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["name", "user"]


@admin.register(ActivityInstance)
class ActivityInstanceAdmin(admin.ModelAdmin):
    list_display = ["activity_name", "level", "duration"]

    def activity_name(self, obj):
        return obj.activity.name
