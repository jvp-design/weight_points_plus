from datetime import datetime
from typing import Any, Dict, Optional
from pytz import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView, CreateView

from ..day.models import Day
from ..day.views import update_daily_points
from ..utils.mixins import UserHasAllInfoMixin
from weight_points_plus.users.models import Weight
from ..utils.points_calculators import calculate_daily_points
from ..week.models import Week
from ..week.utils import update_weekly_excess_points

User = get_user_model()


# class UserDetailView(LoginRequiredMixin, DetailView):
#
#     model = User
#     slug_field = "username"
#     slug_url_kwarg = "username"
#
#
# user_detail_view = UserDetailView.as_view()


class CurrentUserDetailView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self, queryset: Optional[QuerySet] = ...) -> User:
        return self.model.objects.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_fields = [
            dict(lookup="name", display="Name"),
            dict(lookup="email", display="Email"),
            dict(lookup="age", display="Age"),
            dict(lookup="birth_date", display="Birth Date"),
            dict(lookup="weight"),
            dict(lookup="height"),
            dict(lookup="get_sex_display", display="Sex"),
            dict(lookup="weekly_points", display="Weekly Points"),
            dict(lookup="get_weigh_in_day_display", display="Weigh-In Day"),
            dict(lookup="timezone", display="Time Zone"),
        ]
        if self.request.user.sex == "Female":
            user_fields.append(dict(lookup="get_nursing_display", display="Nursing"))
        user_fields.append(dict(lookup="maintenance_mode", display="Maintenance Mode"))
        context["user_fields"] = []
        for field in user_fields:
            if field["lookup"] == "weight":
                weight_set = self.request.user.weight_set.all()
                if not weight_set:
                    context["user_fields"].append(
                        dict(lookup="Not Yet Recorded", display="Weight (lbs.)")
                    )
                else:
                    last_weight = weight_set.last()
                    context["user_fields"].append(
                        dict(
                            lookup=last_weight.weight,
                            display=f"Weight ({last_weight.weight_units})",
                        )
                    )
            else:
                if field["lookup"] == "height":
                    display = f"Height ({self.request.user.height_units})"
                else:
                    display = field["display"]
                context["user_fields"].append(
                    dict(
                        lookup=getattr(self.request.user, field["lookup"]),
                        display=display,
                    )
                )
        return context


current_user_detail_view = CurrentUserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = [
        "name",
        "height",
        "height_units",
        "sex",
        "weigh_in_day",
        "birth_day",
        "birth_month",
        "birth_year",
        "weekly_points",
        "timezone",
        "nursing",
        "maintenance_mode",
    ]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return reverse("users:redirect")

    def get_object(self):
        return self.request.user

    # def post(self, request, *args, **kwargs):
    #     form = self.get_form()
    #     if form.is_valid():
    #         self.object = form.save(commit=False)
    #         self.object.birth_date = datetime(
    #             self.object.birth_year, self.object.birth_month, self.object.birth_day
    #         )
    #         # if not self.object.username:
    #         #     if self.request.user.username:
    #         #         self.object.username = self.request.user.username
    #         #     else:
    #         #         self.object.username = None
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        if self.request.user.has_input_all_fields:
            return reverse("day:today")
        messages.add_message(
            self.request, messages.INFO, "Please fill in your preliminary information."
        )
        return reverse("users:update")


user_redirect_view = UserRedirectView.as_view()


class WeightRecordView(UserHasAllInfoMixin, CreateView):
    model = Weight
    fields = ["weight", "weight_units"]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.user = request.user
            self.object.date_recorded = datetime.now(
                tz=timezone(self.request.user.timezone)
            )
            self.object.save()
            if request.user.first_weight_recorded:
                day = Day.objects.get(
                    user=request.user, date=self.object.date_recorded.date()
                )
                if not day.week.weight_recorded:
                    points = calculate_daily_points(
                        request.user, self.object.weight, self.object.weight_units
                    )
                    week = Week.objects.get(id=day.week.pk)
                    week.weight = self.object.weight
                    week.weight_units = self.object.weight_units
                    week.weight_recorded = True
                    for day in Day.objects.filter(user=request.user, week=week):
                        day.total_points = points
                        update_daily_points(day)
                    update_weekly_excess_points(week)

            return HttpResponseRedirect(reverse("day:today"))
        else:
            return self.form_invalid(form)


weight_record_view = WeightRecordView.as_view()
