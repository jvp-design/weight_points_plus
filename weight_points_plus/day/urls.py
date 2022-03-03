from datetime import datetime

from django.urls import path, register_converter

from . import views


app_name = "day"


class DateConverter:
    regex = "\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value):
        return value


register_converter(DateConverter, "yyyy")

urlpatterns = [
    path("today/", view=views.today_detail_view, name="today"),
    path("<slug:date>/next/", view=views.next_day_detail_view, name="next"),
    path("<slug:date>/prev/", view=views.prev_day_detail_view, name="prev"),
    path(
        "<slug:date>/activity/", view=views.day_activity_list_view, name="activity-list"
    ),
    path(
        "<slug:date>/activity/add/",
        view=views.day_activity_add_view,
        name="activity-add",
    ),
    path(
        "<slug:date>/activity/update/<int:pk>/",
        view=views.day_activity_update_view,
        name="activity-update",
    ),
    path(
        "<slug:date>/activity/delete/<int:pk>/",
        view=views.day_activity_delete_view,
        name="activity-delete",
    ),
    path("<slug:date>/", view=views.day_detail_view, name="detail"),
]
