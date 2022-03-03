from django.urls import path

from weight_points_plus.activity import views


app_name = "activity"


urlpatterns = [
    path("", view=views.all_activity_list_view, name="list"),
    path("mine", view=views.user_activity_list_view, name="mine"),
    path("create", view=views.activity_create_view, name="create"),
    path("<int:pk>", view=views.activity_detail_view, name="detail"),
    path("<int:pk>/update", view=views.activity_update_view, name="update"),
    path("<int:pk>/delete", view=views.activity_delete_view, name="delete"),
]
