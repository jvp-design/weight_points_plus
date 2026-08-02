import datetime
from typing import Any, Dict

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from weight_points_plus.utils.recaptcha import ReCaptchaFormMixin

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }


class UserSignupForm(ReCaptchaFormMixin, SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    recaptcha_action = "signup"


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class UserUpdateForm(forms.ModelForm):
    class Meta:
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

    def clean(self) -> Dict[str, Any]:
        data = self.cleaned_data
        day = data.get("birth_day")
        month = data.get("birth_month")
        year = data.get("birth_year")
        if month in [4, 6, 9, 11] and day == 31:
            self.add_error("birth_day", _("That is an invalid day for that month."))
        if month == 2:
            if year % 4 == 0:
                if day > 29:
                    self.add_error(
                        "birth_day", _("That is an invalid day for that month.")
                    )
            elif day > 28:
                self.add_error("birth_day", _("That is an invalid day for that month."))
        return data
