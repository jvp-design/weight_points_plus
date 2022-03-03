from django.db import models


class Meal(models.Model):
    class MealChoices(models.TextChoices):
        BREAKFAST = "breakfast"
        LUNCH = "lunch"
        DINNER = "dinner"
        ANYTIME = "anytime"

    name = models.CharField(
        max_length=9, choices=MealChoices.choices, default=MealChoices.BREAKFAST
    )
    points = models.IntegerField(default=0)
    day = models.ForeignKey("day.Day", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "day", "user")
        ordering = ["pk"]

    def __str__(self):
        return f"User: {self.user}, {self.day.date}/{self.name}"
