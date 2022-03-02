from django.contrib import admin
from .models import FoodItem, FoodItemInstance


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ["name", "food_item_type", "user"]


@admin.register(FoodItemInstance)
class FoodItemInstanceAdmin(admin.ModelAdmin):
    list_display = ["food_name", "serving_size", "serving_unit"]

    def food_name(self, obj):
        return obj.food.name
