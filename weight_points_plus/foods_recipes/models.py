from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver

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
    conversion_weight_value = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True, blank=True
    )
    conversion_volume_value = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)
    restaurant = models.CharField(max_length=256, null=True, blank=True)
    points_per_serving = models.IntegerField(default=0, blank=True)
    # user_created = models.BooleanField(default=True)
    public = models.BooleanField(default=False, blank=True)
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
    version = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["restaurant", "name"]

    def __str__(self):
        return f"({self.food_item_type.title()}) {self.name}"


VERSIONED_FIELDS = (
    "fat", "carbs", "fiber", "protein",
    "serving_size", "serving_unit",
    "conversion_unit_weight", "conversion_unit_volume",
    "conversion_weight_value", "conversion_volume_value",
)


@receiver(pre_save, sender=FoodItem)
def update_conversion_factor(sender, instance, *args, **kwargs):
    if (
        instance.conversion_weight_value is not None
        and instance.conversion_volume_value is not None
    ):
        instance.conversion_weight_to_volume = (
            instance.conversion_weight_value / instance.conversion_volume_value
        )

    if instance.pk:
        try:
            db = FoodItem.objects.get(pk=instance.pk)
            if any(getattr(instance, f) != getattr(db, f) for f in VERSIONED_FIELDS):
                instance.version = db.version + 1
        except FoodItem.DoesNotExist:
            pass


@receiver(m2m_changed, sender=FoodItem.recipe_items.through)
def bump_recipe_version_on_items_change(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        FoodItem.objects.filter(pk=instance.pk).update(version=F("version") + 1)


class FoodItemInstance(models.Model):
    serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
    serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
    points = models.IntegerField(null=True)
    food_version = models.PositiveIntegerField(default=1)
    # fat = models.FloatField()
    # carbs = models.FloatField()
    # fiber = models.FloatField()
    # protein = models.FloatField()

    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    meal = models.ManyToManyField("meal.Meal", blank=True)

    def __str__(self):
        return f"{self.food.name}, {self.serving_size}{self.serving_unit}"
