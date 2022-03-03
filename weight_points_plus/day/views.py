import datetime
from datetime import timedelta
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from weight_points_plus.activity.models import ActivityInstance, Activity
from weight_points_plus.activity.utils import calculate_activity_points
from weight_points_plus.activity.views import ActivityListView
from weight_points_plus.day.models import Day
from weight_points_plus.utils.mixins import UserHasAllInfoMixin
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
    for item in day.activityinstance_set.all():
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
        context["is_current_day"] = day.date == timezone.now().date()
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
        for item in day.activityinstance_set.all():
            activities.append(
                {**item.__dict__, "points": calculate_activity_points(item, day)}
            )
        context["activities"] = activities
        return context


class DayDetailView(GetADayView):
    day_is_available = True

    def get_object(self) -> Day:
        try:
            return self.get_queryset().get(date=self.kwargs.get("date"))
        except Day.DoesNotExist:
            self.day_is_available = False
            return self.get_queryset().order_by("date").last()

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
        try:
            return self.get_queryset().get(date=timezone.now().date())
        except Day.DoesNotExist:
            backfill_weeks(self.request.user)
            return self.get_queryset().get(date=timezone.now().date())

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

        new_date = datetime.datetime.strptime(date, "%Y-%m-%d").date() + timedelta(
            days=1
        )
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

        new_date = datetime.datetime.strptime(date, "%Y-%m-%d").date() - timedelta(
            days=1
        )
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


class DayActivityListView(ActivityListView):
    def get_queryset(self) -> QuerySet[Activity]:
        self.queryset = Activity.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


day_activity_list_view = DayActivityListView.as_view()


class BaseActivityEditView(UserHasAllInfoMixin):
    model = ActivityInstance
    fields = ["level", "duration"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity"] = self.get_activity()
        return context


class DayActivityAddView(BaseActivityEditView, CreateView):
    model = ActivityInstance
    fields = ["level", "duration"]

    def get_queryset(self):
        return Activity.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )

    def get_activity(self):
        return get_object_or_404(
            self.get_queryset(), pk=self.request.GET.get("activity")
        )

    def post(self, request, date=None, *args, **kwargs):
        form = self.get_form()
        qs = Day.objects.filter(user=request.user)
        day = get_object_or_404(qs, date=date)
        if form.is_valid():
            if (
                len(
                    day.activityinstance_set.filter(
                        activity=self.get_activity(), level=request.POST.get("level")
                    )
                )
                > 0
            ):
                messages.add_message(
                    request,
                    messages.ERROR,
                    "That activity with level is already added. Please update it instead of adding it again.",
                )
                return HttpResponseRedirect(
                    reverse("day:detail", kwargs={"date": date})
                )
            try:
                item = ActivityInstance.objects.get(
                    activity=self.get_activity(),
                    level=request.POST.get("level"),
                    duration=request.POST.get("duration"),
                )
            except ActivityInstance.DoesNotExist:
                item = form.save(commit=False)
                item.activity = self.get_activity()
                item.save()
            item.day.add(day)
            update_daily_activity_points(day)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": day.date})
            )
        else:
            return self.form_invalid(form)


day_activity_add_view = DayActivityAddView.as_view()


class DayActivityUpdateView(BaseActivityEditView, UpdateView):
    def get_activity(self):
        activity_instance = get_object_or_404(
            self.get_queryset(), pk=self.kwargs.get("pk")
        )
        return activity_instance.activity

    def post(self, request, date=None, *args, **kwargs):
        form = self.get_form()
        qs = Day.objects.filter(user=request.user)
        day = get_object_or_404(qs, pk=date)
        obj = self.get_object()
        obj.day.remove(day)
        if form.is_valid():
            activity = obj.activity
            try:
                item = ActivityInstance.objects.get(
                    activity=activity,
                    level=request.POST.get("level"),
                    duration=request.POST.get("duration"),
                )
            except ActivityInstance.DoesNotExist:
                item = form.save(commit=False)
                item.activity = activity
                item.save()
            item.day.add(day)
            if len(obj.day.all()) == 0:
                obj.delete()
            update_daily_activity_points(day)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": day.date})
            )
        else:
            return self.form_invalid(form)


day_activity_update_view = DayActivityUpdateView.as_view()


class DayActivityDeleteView(UserHasAllInfoMixin, DeleteView):
    model = ActivityInstance

    def get(self, request, date=None, *args, **kwargs):
        qs = Day.objects.filter(user=request.user)
        day = get_object_or_404(qs, date=date)
        obj = self.get_object()
        obj.day.remove(day)
        if len(obj.day.all()) == 0:
            obj.delete()
        update_daily_activity_points(day)
        return HttpResponseRedirect(reverse("day:detail", kwargs={"date": day.date}))

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        messages.add_message(
            request, messages.ERROR, "You cannot POST to this endpoint."
        )
        return redirect(request.META.get("HTTP_REFERER"))


day_activity_delete_view = DayActivityDeleteView.as_view()
