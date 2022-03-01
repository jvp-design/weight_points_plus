from django.urls import path

from weight_points_plus.meal import views

app_name = "meal"


urlpatterns = [
    path(
        "<str:meal>/<yyyy:date_val>/items-search",
        view=views.meal_food_list_view,
        name="items-search",
    ),
    path(
        "<str:meal>/<yyyy:date_val>/add",
        view=views.meal_food_add_view,
        name="add-food-item",
    ),
]
