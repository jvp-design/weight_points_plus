from django.contrib import admin
from weight_points_plus.day.models import Day, Activity


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ["date", "user"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "date"]

    def date(self, obj):
        return obj.day.date
