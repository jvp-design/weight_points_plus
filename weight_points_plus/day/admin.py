from django.contrib import admin
from weight_points_plus.day.models import Day


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ["date", "user"]
