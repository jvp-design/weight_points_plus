from django.db import models


class Week(models.Model):
    weekly_total_points = models.IntegerField(default=49)
    weekly_points_used = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    start_date = models.DateField()
    weight_recorded = models.BooleanField(default=False)
    activity_points = models.IntegerField(default=0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    @property
    def weekly_points_remaining(self) -> int:
        return self.weekly_total_points - self.weekly_points_used

    class Meta:
        unique_together = ("user", "start_date")

    def __str__(self):
        return f"User: {self.user}, start date: {self.start_date}"
