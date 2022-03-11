from django.urls import path

from weight_points_plus.foods_recipes.recipe import views


app_name = "recipe"


urlpatterns = [
    path("", view=views.all_recipe_list_view, name="list"),
    path("create", view=views.recipe_create_view, name="create"),
    path("<int:pk>/update", view=views.recipe_update_view, name="update"),
    path("<int:pk>/delete", view=views.recipe_delete_view, name="delete"),
    path("<int:recipe_pk>/food", view=views.recipe_food_list_view, name="food-list"),
    path("<int:recipe_pk>/food/add", view=views.recipe_food_add_view, name="add-food"),
    path(
        "<int:recipe_pk>/food/update/<int:pk>",
        view=views.recipe_food_update_view,
        name="update-food-item",
    ),
    path(
        "<int:recipe_pk>/food/delete/<int:pk>",
        view=views.recipe_food_delete_view,
        name="delete-food-item",
    ),
    path("<int:pk>", view=views.recipe_detail_view, name="detail"),
]
