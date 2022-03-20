from datetime import date, datetime
import pytz

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


BIRTH_DAY_CHOICES = [(i, i) for i in range(1, 32)]
BIRTH_YEAR_CHOICES = [(i, i) for i in range(1900, date.today().year + 1)]


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

    class HeightUnitChoices(models.TextChoices):
        INCHES = "in"
        CENTIMETERS = "cm"

    class BirthMonthChoices(models.IntegerChoices):
        JANUARY = 1
        FEBRUARY = 2
        MARCH = 3
        APRIL = 4
        MAY = 5
        JUNE = 6
        JULY = 7
        AUGUST = 8
        SEPTEMBER = 9
        OCTOBER = 10
        NOVEMBER = 11
        DECEMBER = 12

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
    height = models.IntegerField(null=True)
    height_units = models.CharField(
        choices=HeightUnitChoices.choices,
        max_length=2,
        null=True,
        default=HeightUnitChoices.INCHES,
    )
    sex = models.CharField(choices=SexChoices.choices, max_length=6, null=True)
    weigh_in_day = models.IntegerField(
        choices=WeekdayChoices.choices, default=WeekdayChoices.MONDAY, null=True
    )
    birth_date = models.DateField(null=True)
    birth_month = models.IntegerField(choices=BirthMonthChoices.choices, null=True)
    birth_day = models.IntegerField(choices=BIRTH_DAY_CHOICES, null=True)
    birth_year = models.IntegerField(choices=BIRTH_YEAR_CHOICES, null=True)
    weekly_points = models.IntegerField(default=49, null=True)
    nursing = models.IntegerField(
        choices=NursingChoices.choices, default=NursingChoices.NONE, null=True
    )
    maintenance_mode = models.BooleanField(default=False)
    latest_date = models.DateField(null=True)
    first_weight_recorded = models.BooleanField(default=False)

    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="UTC")

    @property
    def age(self) -> int:
        return relativedelta(date.today(), self.birth_date).years

    @property
    def has_input_all_fields(self):
        return all(
            [
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


@receiver(pre_save, sender=User)
def set_birth_date(sender, instance, *args, **kwargs):
    instance.birth_date = datetime(
        instance.birth_year, instance.birth_month, instance.birth_day
    )


class WeightUnitChoices(models.TextChoices):
    POUNDS = "lbs"
    KILOGRAMS = "kg"


class Weight(models.Model):
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight_units = models.CharField(
        choices=WeightUnitChoices.choices,
        max_length=3,
        null=True,
        default=WeightUnitChoices.POUNDS,
    )
    date_recorded = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
