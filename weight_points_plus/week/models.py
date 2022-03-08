from datetime import timedelta

from django.db import models
from django.utils import timezone


class Week(models.Model):
    weekly_total_points = models.IntegerField(default=49)
    weekly_points_used = models.IntegerField(default=0)
    weekly_points_remaining = models.IntegerField(default=49)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    start_date = models.DateField()
    weight_recorded = models.BooleanField(default=False)
    activity_points = models.IntegerField(default=0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    @property
    def days_remaining(self) -> int:
        end_date = self.start_date + timedelta(days=7)
        return (end_date - timezone.now().date()).days

    class Meta:
        unique_together = ("user", "start_date")

    def __str__(self):
        return f"User: {self.user}, start date: {self.start_date}"
