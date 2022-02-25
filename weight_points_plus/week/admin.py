from django.contrib import admin
from weight_points_plus.week.models import Week


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = [
        "start_date",
        "user",
        "weight",
        "weekly_points_used",
        "weight_recorded",
    ]
