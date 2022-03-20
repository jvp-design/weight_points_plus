from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


class CustomAlertMixin(AccessMixin):
    permission_denied_url = None

    def get_permission_denied_url(self):
        return self.permission_denied_url

    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.get_permission_denied_url() or not self.permission_denied_message:
            return super().handle_no_permission()
        messages.add_message(
            self.request, messages.INFO, self.permission_denied_message
        )
        return HttpResponseRedirect(self.get_permission_denied_url())


class UserHasAllInfoMixin(CustomAlertMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif not request.user.has_input_all_fields:
            self.permission_denied_url = reverse("users:update")
            self.permission_denied_message = (
                "You need to fill in all of your info first."
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserIsOwnerMixin(CustomAlertMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif not obj.user or obj.user != request.user:
            self.permission_denied_message = (
                "You are not authorized to perform this action."
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserCanViewMixin(CustomAlertMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif obj.user is not None and obj.user != request.user and not obj.public:
            self.permission_denied_message = "You are not authorized to view this item."
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# class UserOwnsParentObject(CustomAlertMixin):
#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_parent()
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         elif obj.user is not None and obj.user != request.user:
#             self.permission_denied_message = "You are not authorized to do that."
#             return self.handle_no_permission()
#         return super().dispatch(request, *args, **kwargs)
