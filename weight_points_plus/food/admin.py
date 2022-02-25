from django.contrib import admin
from weight_points_plus.food.models import Food, FoodInstance


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "user"]


@admin.register(FoodInstance)
class FoodInstanceAdmin(admin.ModelAdmin):
    list_display = ["food", "meal"]
