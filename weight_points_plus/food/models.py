from django.core.validators import MinValueValidator
from django.db import models


def is_weight_serving(val: str) -> bool:
    return val == "kg" or val == "gm" or val == "oz" or val == "lb"


def is_volume_serving(val: str) -> bool:
    return (
        val == "tsp"
        or val == "tbsp"
        or val == "fl oz"
        or val == "cup"
        or val == "ml"
        or val == "l"
    )


SERVING_SIZE_CHOICES = [
    ("Weight", (("KG", "kg"), ("GM", "gm"), ("OZ", "oz"), ("LB", "lb"))),
    (
        "Volume",
        (
            ("TSP", "tsp"),
            ("TBSP", "tbsp"),
            ("FL_OZ", "fl oz"),
            ("CUP", "cup"),
            ("ML", "ml"),
            ("L", "l"),
        ),
    ),
    ("EACH", "each"),
]


class Food(models.Model):

    name = models.CharField(max_length=256)
    fat = models.FloatField(validators=[MinValueValidator(0.0)])
    carbs = models.FloatField(validators=[MinValueValidator(0.0)])
    fiber = models.FloatField(validators=[MinValueValidator(0.0)])
    protein = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
    conversion_unit_weight = models.CharField(
        max_length=6,
        choices=[*SERVING_SIZE_CHOICES[0][1], SERVING_SIZE_CHOICES[2]],
        null=True,
        blank=True,
    )
    conversion_unit_volume = models.CharField(
        max_length=6,
        choices=[*SERVING_SIZE_CHOICES[1][1], SERVING_SIZE_CHOICES[2]],
        null=True,
        blank=True,
    )
    conversion_weight_to_volume = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)
    restaurant = models.CharField(max_length=256, null=True, blank=True)
    points_per_serving = models.IntegerField()
    user_created = models.BooleanField(default=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class FoodInstance(models.Model):
    serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
    points = models.IntegerField()

    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    meal = models.ForeignKey("meal.Meal", on_delete=models.SET_NULL, null=True)
