from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


class UserHasAllInfoMixin(AccessMixin):
    permission_denied_url = None

    def get_permission_denied_url(self):
        return self.permission_denied_url

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.has_input_all_fields:
            self.permission_denied_url = reverse("users:update")
            self.permission_denied_message = (
                "You need to fill in all of your info first."
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.get_permission_denied_url() or not self.permission_denied_message:
            return super().handle_no_permission()
        messages.add_message(
            self.request, messages.INFO, self.permission_denied_message
        )
        return HttpResponseRedirect(self.get_permission_denied_url())


class UserIsOwnerMixin(AccessMixin):
    permission_denied_url = None

    def get_permission_denied_url(self):
        return self.permission_denied_url

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user or not obj.user_created:
            self.permission_denied_message = (
                "You are not authorized to perform this action."
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.get_permission_denied_url() or not self.permission_denied_message:
            return super().handle_no_permission()
        messages.add_message(
            self.request, messages.INFO, self.permission_denied_message
        )

        return HttpResponseRedirect(reverse(self.get_permission_denied_url()))


class UserCanViewMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_created and obj.user != request.user:
            self.permission_denied_message = "You are not authorized to view this item."
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
