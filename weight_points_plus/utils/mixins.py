from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin


class UserHasAllInfoMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.has_input_all_fields:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserIsOwnerMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.user_created or obj.user != request.user:
            self.permission_denied_message = (
                "You are not authorized to perform this action."
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserCanViewMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user_created and obj.user != request.user:
            self.permission_denied_message = "You are not authorized to view this item."
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
