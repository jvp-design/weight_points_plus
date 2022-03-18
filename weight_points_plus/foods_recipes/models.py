from django.core.validators import MinValueValidator
from django.db import models

from weight_points_plus.utils.misc import SERVING_SIZE_CHOICES, servings


class FoodItem(models.Model):
    class FoodItemType(models.TextChoices):
        FOOD = "food"
        RECIPE = "recipe"

    name = models.CharField(max_length=256, blank=True)
    fat = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    carbs = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    fiber = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    protein = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
    conversion_unit_weight = models.CharField(
        max_length=6,
        choices=[*servings.get("weight"), *servings.get("each")],
        null=True,
        blank=True,
    )
    conversion_unit_volume = models.CharField(
        max_length=6,
        choices=[*servings.get("volume"), *servings.get("each")],
        null=True,
        blank=True,
    )
    conversion_weight_to_volume = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)
    restaurant = models.CharField(max_length=256, null=True, blank=True)
    points_per_serving = models.IntegerField(default=0, blank=True)
    # user_created = models.BooleanField(default=True)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )
    directions = models.TextField(max_length=2048, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    servings_in_recipe = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    food_item_type = models.CharField(
        max_length=8, choices=FoodItemType.choices, blank=True
    )
    recipe_items = models.ManyToManyField("FoodItemInstance", blank=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"({self.food_item_type.title()}) {self.name}"


class FoodItemInstance(models.Model):
    serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
    points = models.IntegerField(null=True)
    # fat = models.FloatField()
    # carbs = models.FloatField()
    # fiber = models.FloatField()
    # protein = models.FloatField()

    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    meal = models.ManyToManyField("meal.Meal", blank=True)

    def __str__(self):
        return f"{self.food.name}, {self.serving_size}{self.serving_unit}"
