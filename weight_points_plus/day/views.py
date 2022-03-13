from datetime import timedelta, datetime
from typing import Any, Dict
from pytz import timezone

from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

# from weight_points_plus.activity.models import ActivityInstance, Activity
from weight_points_plus.day.utils import calculate_activity_points
from weight_points_plus.day.models import Day, Activity
from weight_points_plus.users.models import Weight
from weight_points_plus.utils.mixins import UserHasAllInfoMixin, UserIsOwnerMixin
from weight_points_plus.utils.time_tracking import backfill_weeks
from weight_points_plus.week.utils import update_weekly_excess_points


def update_daily_points(day: Day) -> None:
    day.points_used = sum(day.meal_set.values_list("points", flat=True))
    points_remaining = day.total_points - day.points_used
    if points_remaining < 0:
        day.weekly_points_used = -points_remaining
        day.points_remaining = 0
        update_weekly_excess_points(day.week)
    else:
        day.points_remaining = points_remaining
    day.save()


def update_daily_activity_points(day: Day) -> None:
    points = 0
    for item in day.activity_set.all():
        points += calculate_activity_points(item, day)
    day.activity_points = points
    day.save()


class GetADayView(UserHasAllInfoMixin, DetailView):
    model = Day
    slug_field = "date"
    slug_url_kwarg = "date"

    def get_queryset(self) -> models.query.QuerySet[Day]:
        return Day.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if kwargs.get("object") is not None and isinstance(kwargs.get("object"), Day):
            day = kwargs.get("object")
        else:
            day = self.get_object()
        today = datetime.now(tz=timezone(self.request.user.timezone)).date()
        try:
            context["record_weight_trigger"] = (
                not self.get_queryset().get(date=today).week.weight_recorded
            )
        except Day.DoesNotExist:
            context["record_weight_trigger"] = False

        context["is_current_day"] = day.date == today
        context["next_day_is_available"] = True
        context["prev_day_is_available"] = True
        if (
            len(
                self.get_queryset().filter(
                    date=self.get_object().date + timedelta(days=1)
                )
            )
            == 0
        ):
            context["next_day_is_available"] = False
        if (
            len(
                self.get_queryset().filter(
                    date=self.get_object().date - timedelta(days=1)
                )
            )
            == 0
        ):
            context["prev_day_is_available"] = False
        activities = []
        for item in day.activity_set.all():
            activities.append(
                {**item.__dict__, "points": calculate_activity_points(item, day)}
            )
        context["activities"] = activities
        return context

    def get(self, request, *args, **kwargs):
        if len(Weight.objects.filter(user=request.user)) == 0:
            messages.add_message(
                request,
                messages.INFO,
                "You need to record your weight before you can continue.",
            )
            return HttpResponseRedirect(reverse("users:record-weight"))
        return super().get(request, *args, **kwargs)


class DayDetailView(GetADayView):
    day_is_available = True

    def get_object(self) -> Day:
        try:
            return self.get_queryset().get(date=self.kwargs.get("date"))
        except Day.DoesNotExist:
            self.day_is_available = False
            return self.get_queryset().order_by("date").last()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["activity_info"] = []
        for item in self.object.activity_set.all():
            context["activity_info"].append(
                dict(
                    pk=item.pk,
                    name=item.name,
                    duration=item.duration,
                    level=item.level,
                    points=calculate_activity_points(item, self.object),
                )
            )
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if not self.day_is_available:
            messages.add_message(
                self.request,
                messages.ERROR,
                f"{self.kwargs.get('date')} is not yet available.",
            )
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": self.get_object().date})
            )
        else:
            return super().render_to_response(context, **response_kwargs)


day_detail_view = DayDetailView.as_view()


class TodayDetailView(GetADayView):
    def get_object(self) -> Day:
        now = datetime.now(tz=timezone(self.request.user.timezone)).date()
        if (
            not self.request.user.latest_date
            or (self.request.user.latest_date - now).days <= 0
        ):
            backfill_weeks(self.request.user)
        try:
            return self.get_queryset().get(date=now)
        except Day.DoesNotExist:
            backfill_weeks(self.request.user)
            return self.get_queryset().get(date=now)

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        return HttpResponseRedirect(
            reverse("day:detail", kwargs={"date": self.get_object().date})
        )


today_detail_view = TodayDetailView.as_view()


class NextDayDetailView(GetADayView):
    date_not_available = None

    def get_object(self) -> Day:
        date = self.kwargs.get("date")
        if date is None:
            raise Http404("A date must be included.")

        new_date = datetime.strptime(date, "%Y-%m-%d").date() + timedelta(days=1)
        try:
            return self.get_queryset().get(date=new_date)
        except Day.DoesNotExist:
            self.date_not_available = new_date
            return self.get_queryset().get(date=date)

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.date_not_available is not None:
            messages.add_message(
                self.request,
                messages.ERROR,
                f"{self.date_not_available} is not available.",
            )
        return HttpResponseRedirect(
            reverse("day:detail", kwargs={"date": self.get_object().date})
        )


next_day_detail_view = NextDayDetailView.as_view()


class PrevDayDetailView(GetADayView):
    date_not_available = None

    def get_object(self) -> Day:
        date = self.kwargs.get("date")
        if date is None:
            raise Http404("A date must be included.")

        new_date = datetime.strptime(date, "%Y-%m-%d").date() - timedelta(days=1)
        try:
            return self.get_queryset().get(date=new_date)
        except Day.DoesNotExist:
            self.date_not_available = new_date
            return self.get_queryset().get(date=date)

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.date_not_available is not None:
            messages.add_message(
                self.request,
                messages.ERROR,
                f"{self.date_not_available} is not available.",
            )
        return HttpResponseRedirect(
            reverse("day:detail", kwargs={"date": self.get_object().date})
        )


prev_day_detail_view = PrevDayDetailView.as_view()


class DayActivityAddView(UserHasAllInfoMixin, CreateView):
    model = Activity
    fields = ["name", "level", "duration"]

    def post(self, request, date=None, *args, **kwargs):
        form = self.get_form()
        qs = Day.objects.filter(user=request.user)
        day = get_object_or_404(qs, date=date)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.day = day
            self.object.save()
            update_daily_activity_points(day)
            messages.add_message(
                request,
                messages.SUCCESS,
                f'Activity "{self.object.name}" has been added.',
            )
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": day.date})
            )
        else:
            return self.form_invalid(form)


day_activity_add_view = DayActivityAddView.as_view()


class DayActivityUpdateView(UserHasAllInfoMixin, UserIsOwnerMixin, UpdateView):
    model = Activity
    fields = ["level", "duration"]

    def get_queryset(self) -> models.query.QuerySet[Activity]:
        return Activity.objects.filter(day__date=self.kwargs.get("date"))

    def get_permission_denied_url(self):
        return reverse("day:detail", kwargs={"date": self.kwargs.get("date")})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            form.save()
            update_daily_activity_points(self.object.day)
            messages.add_message(
                request,
                messages.SUCCESS,
                f'Activity "{self.object.name}" has been updated.',
            )
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": self.object.day.date})
            )
        else:
            return self.form_invalid(form)


day_activity_update_view = DayActivityUpdateView.as_view()


class DayActivityDeleteView(UserHasAllInfoMixin, UserIsOwnerMixin, DeleteView):
    model = Activity

    def get_queryset(self) -> models.query.QuerySet[Activity]:
        return Activity.objects.filter(day__date=self.kwargs.get("date"))

    def get_permission_denied_url(self):
        return reverse("day:detail", kwargs={"date": self.kwargs.get("date")})

    def get(self, request, date=None, *args, **kwargs):
        self.object = self.get_object()
        day = self.object.day
        name = self.object.name
        self.object.delete()
        update_daily_activity_points(day)
        messages.add_message(
            request,
            messages.SUCCESS,
            f'Activity "{name}" has been deleted.',
        )
        return HttpResponseRedirect(reverse("day:detail", kwargs={"date": day.date}))

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        messages.add_message(
            request, messages.ERROR, "You cannot POST to this endpoint."
        )
        return redirect(request.META.get("HTTP_REFERER"))


day_activity_delete_view = DayActivityDeleteView.as_view()
