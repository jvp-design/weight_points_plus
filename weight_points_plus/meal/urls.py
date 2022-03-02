from django.urls import path

from weight_points_plus.meal import views

app_name = "meal"


urlpatterns = [
    path(
        "<int:meal_pk>/items-search",
        view=views.meal_food_list_view,
        name="items-search",
    ),
    path(
        "<int:meal_pk>/add",
        view=views.meal_food_add_view,
        name="add-food-item",
    ),
    path(
        "<int:meal_pk>/update/<int:pk>",
        view=views.meal_food_update_view,
        name="update-food-item",
    ),
]
