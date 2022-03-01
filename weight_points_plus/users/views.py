from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


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
            return reverse(
                "day:detail",
                kwargs={
                    "date_val": f"{now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)}"
                },
            )
        messages.add_message(
            self.request, messages.INFO, "Please fill in your preliminary information."
        )
        return reverse("users:update")


user_redirect_view = UserRedirectView.as_view()
