from django.db import models
from django.views.generic import DetailView

from weight_points_plus.day.models import Day
from weight_points_plus.utils.mixins import UserHasAllInfoMixin
from weight_points_plus.utils.time_tracking import backfill_weeks


class DayDetailView(UserHasAllInfoMixin, DetailView):
    model = Day

    def get_queryset(self) -> models.query.QuerySet[Day]:
        return Day.objects.filter(user=self.request.user)

    def get_object(self) -> Day:
        queryset = self.get_queryset()
        try:
            return queryset.get(date=self.kwargs.get("date_val"))
        except Day.DoesNotExist:
            backfill_weeks(self.request.user)
            return queryset.get(date=self.kwargs.get("date_val"))


day_detail_view = DayDetailView.as_view()
