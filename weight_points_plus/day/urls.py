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
    path("next/<slug:date>/", view=views.next_day_detail_view, name="next"),
    path("prev/<slug:date>/", view=views.prev_day_detail_view, name="prev"),
    path("<slug:date>/", view=views.day_detail_view, name="detail"),
]
