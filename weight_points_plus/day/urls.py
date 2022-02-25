from datetime import datetime

from django.urls import path, register_converter

from weight_points_plus.day.views import day_detail_view


app_name = "day"


class DateConverter:
    regex = "\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value):
        return value


register_converter(DateConverter, "yyyy")

urlpatterns = [path("<yyyy:date_val>/", view=day_detail_view, name="detail")]
