from django.db import models
from django.urls import reverse


class Activity(models.Model):
    name = models.CharField(max_length=256)
    user_created = models.BooleanField(default=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["name", "user"]
        verbose_name_plural = "activities"

    def __str__(self):
        return f"Activity {self.name}, owner {self.user.email}"

    def get_absolute_url(self):
        return reverse("activity:detail", kwargs={"pk": self.pk})


class ActivityInstance(models.Model):
    class LevelChoices(models.TextChoices):
        LOW = "low"
        MODERATE = "moderate"
        HIGH = "high"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    level = models.CharField(max_length=8, choices=LevelChoices.choices)
    duration = models.FloatField()

    day = models.ManyToManyField("day.Day")

    def __str__(self):
        return f"{self.activity.name}, ({self.level}/{round(self.duration, 2)} minutes)"
