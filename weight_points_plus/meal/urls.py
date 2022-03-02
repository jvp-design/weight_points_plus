from django.urls import path

from weight_points_plus.meal import views

app_name = "meal"


urlpatterns = [
    path(
        "<int:pk>/items-search",
        view=views.meal_food_list_view,
        name="items-search",
    ),
    path(
        "<int:pk>/add",
        view=views.meal_food_add_view,
        name="add-food-item",
    ),
]
