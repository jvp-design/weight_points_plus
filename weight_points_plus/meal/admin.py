from django.contrib import admin
from weight_points_plus.meal.models import Meal


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ["name", "day", "user"]
