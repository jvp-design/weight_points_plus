from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from .forms import UserUpdateForm

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
            dict(lookup="weight", display="Weight (lbs.)"),
            dict(lookup="height", display="Height (in.)"),
            dict(lookup="get_sex_display", display="Sex"),
            dict(lookup="weekly_points", display="Weekly Points"),
            dict(lookup="get_weigh_in_day_display", display="Weigh-In Day"),
        ]
        if self.request.user.sex == "Female":
            user_fields.append(dict(lookup="get_nursing_display", display="Nursing"))
        user_fields.append(dict(lookup="maintenance_mode", display="Maintenance Mode"))
        context["user_fields"] = [
            dict(lookup=getattr(self.request.user, x["lookup"]), display=x["display"])
            for x in user_fields
        ]
        return context


current_user_detail_view = CurrentUserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = [
        "name",
        "weight",
        "height",
        "sex",
        "weigh_in_day",
        "birth_date",
        "weekly_points",
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


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        if self.request.user.has_input_all_fields:
            now = timezone.now().date()
            return reverse("day:detail", kwargs={"date": now})
        messages.add_message(
            self.request, messages.INFO, "Please fill in your preliminary information."
        )
        return reverse("users:update")


user_redirect_view = UserRedirectView.as_view()
