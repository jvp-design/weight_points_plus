from datetime import timedelta
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView

from weight_points_plus.day.models import Day
from weight_points_plus.utils.mixins import UserHasAllInfoMixin
from weight_points_plus.utils.time_tracking import backfill_weeks


def update_daily_points(day: Day) -> None:
    day.points_used = sum(day.meal_set.values_list("points", flat=True))
    day.save()


class GetADayView(UserHasAllInfoMixin, DetailView):
    model = Day
    slug_field = "date"
    slug_url_kwarg = "date"

    def get_queryset(self) -> models.query.QuerySet[Day]:
        return Day.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["is_current_day"] = self.get_object().date == timezone.now().date()
        return context


class DayDetailView(GetADayView):
    def get_object(self) -> Day:
        try:
            return super().get_object()
        except Day.DoesNotExist:
            backfill_weeks(self.request.user)
            return super().get_object()


day_detail_view = DayDetailView.as_view()


class TodayDetailView(GetADayView):
    def get(self):
        return HttpResponseRedirect(
            reverse("day:detail", kwargs={"date": timezone.now().date()})
        )


today_detail_view = TodayDetailView.as_view()


class NextDayDetailView(GetADayView):
    def get_object(self, date=None) -> Day:
        if date is None:
            raise Http404("A date must be included.")
        try:
            return self.get_queryset().get(date=date + timedelta(days=1))
        except Day.DoesNotExist:
            raise Http404("That day is not yet available.")


next_day_detail_view = NextDayDetailView.as_view()


class PrevDayDetailView(GetADayView):
    def get_object(self, date=None) -> Day:
        if date is None:
            raise Http404("A date must be included.")
        try:
            return self.get_queryset().get(date=date - timedelta(days=1))
        except Day.DoesNotExist:
            raise Http404("That day is not yet available.")


prev_day_detail_view = PrevDayDetailView.as_view()
