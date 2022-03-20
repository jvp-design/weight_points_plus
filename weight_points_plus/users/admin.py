from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from weight_points_plus.users.forms import UserAdminChangeForm, UserAdminCreationForm
from weight_points_plus.users.models import Weight

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Weight Tracking Info"),
            {
                "fields": (
                    "height",
                    "sex",
                    "weigh_in_day",
                    "birth_date",
                    "birth_day",
                    "birth_month",
                    "birth_year",
                    "weekly_points",
                    "timezone",
                    "nursing",
                    "maintenance_mode",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ["username", "date_recorded", "weight"]

    def username(self, obj):
        return obj.user.username
