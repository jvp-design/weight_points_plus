from django.contrib import admin
from .models import FoodItem, FoodItemInstance


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ["name", "food_item_type", "user"]


@admin.register(FoodItemInstance)
class FoodItemInstanceAdmin(admin.ModelAdmin):
    list_display = ["get_food", "get_meal"]

    def get_food(self, obj):
        return obj.food.name

    def get_meal(self, obj):
        return obj.meal.name
