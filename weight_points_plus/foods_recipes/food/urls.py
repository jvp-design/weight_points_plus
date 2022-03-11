from django.urls import path

from weight_points_plus.foods_recipes.food import views


app_name = "food"


urlpatterns = [
    path("", view=views.all_food_list_view, name="list"),
    # path("mine", view=views.user_food_list_view, name="mine"),
    path("create", view=views.food_create_view, name="create"),
    path("<int:pk>", view=views.food_detail_view, name="detail"),
    path("<int:pk>/update", view=views.food_update_view, name="update"),
    path("<int:pk>/delete", view=views.food_delete_view, name="delete"),
]
