from django.urls import path

from weight_points_plus.users import views

app_name = "users"
urlpatterns = [
    path("~redirect/", view=views.user_redirect_view, name="redirect"),
    path("~update/", view=views.user_update_view, name="update"),
    path("me/", view=views.current_user_detail_view, name="me"),
    # path("<str:username>/", view=views.user_detail_view, name="detail"),
]
