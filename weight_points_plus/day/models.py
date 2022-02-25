from django.db import models


class Day(models.Model):
    class WeekdayChoices(models.IntegerChoices):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    total_points = models.IntegerField()
    points_used = models.IntegerField(default=0)
    weekly_points_used = models.IntegerField(default=0)
    day_of_week = models.IntegerField(choices=WeekdayChoices.choices)
    date = models.DateField()
    week = models.ForeignKey("week.Week", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    @property
    def points_remaining(self) -> int:
        return self.total_points - self.points_used

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"User: {self.user}, {self.date} ({self.get_day_of_week_display()})"
