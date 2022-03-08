from datetime import date
import pytz

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Weight Points Plus.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    class WeekdayChoices(models.IntegerChoices):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    class SexChoices(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"

    class NursingChoices(models.IntegerChoices):
        NONE = 0
        SUPPLEMENTAL = 1
        EXCLUSIVE = 2

    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    weight = models.FloatField(null=True)
    height = models.IntegerField(null=True)
    sex = models.CharField(choices=SexChoices.choices, max_length=6, null=True)
    weigh_in_day = models.IntegerField(
        choices=WeekdayChoices.choices, default=WeekdayChoices.MONDAY, null=True
    )
    birth_date = models.DateField(null=True)
    weekly_points = models.IntegerField(default=49, null=True)
    nursing = models.IntegerField(
        choices=NursingChoices.choices, default=NursingChoices.NONE, null=True
    )
    maintenance_mode = models.BooleanField(default=False)
    has_been_updated = models.BooleanField(default=False)
    latest_date = models.DateField(null=True)

    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="UTC")

    @property
    def age(self) -> int:
        return relativedelta(date.today(), self.birth_date).years

    @property
    def has_input_all_fields(self):
        return all(
            [
                self.weight is not None,
                self.height is not None,
                self.sex is not None,
                self.weigh_in_day is not None,
                self.birth_date is not None,
                self.weekly_points is not None,
                self.nursing is not None,
                self.maintenance_mode is not None,
            ]
        )

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
