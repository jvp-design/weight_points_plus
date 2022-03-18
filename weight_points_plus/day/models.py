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

    total_points = models.IntegerField(default=0)
    points_used = models.IntegerField(default=0)
    points_remaining = models.IntegerField(default=0)
    weekly_points_used = models.IntegerField(default=0)
    day_of_week = models.IntegerField(choices=WeekdayChoices.choices)
    date = models.DateField()
    week = models.ForeignKey("week.Week", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    activity_points = models.IntegerField(default=0)
    days_left = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"User: {self.user}, {self.date} ({self.get_day_of_week_display()})"


class Activity(models.Model):
    class LevelChoices(models.TextChoices):
        LOW = "Low"
        MODERATE = "Moderate"
        HIGH = "High"

    name = models.CharField(max_length=256)
    level = models.CharField(max_length=8, choices=LevelChoices.choices)
    duration = models.FloatField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    # user_created = models.BooleanField(default=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return f"{self.name}; {self.level}; {self.duration} minutes; {self.user.username}; {self.day.date}"
