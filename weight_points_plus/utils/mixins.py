from django.contrib.auth.mixins import LoginRequiredMixin


class UserHasAllInfoMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated. This is a copy-paste from LoginRequiredMixin
        if not request.user.has_input_all_fields:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
