# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator
# from django.db import models
#
# from weight_points_plus.utils.misc import SERVING_SIZE_CHOICES
#
#
# class Recipe(models.Model):
#     name = models.CharField(max_length=256)
#     fat = models.FloatField(validators=[MinValueValidator(0.0)])
#     carbs = models.FloatField(validators=[MinValueValidator(0.0)])
#     fiber = models.FloatField(validators=[MinValueValidator(0.0)])
#     protein = models.FloatField(validators=[MinValueValidator(0.0)])
#     serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
#     serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
#     conversion_unit_weight = models.CharField(
#         max_length=6,
#         choices=[*SERVING_SIZE_CHOICES[0][1], SERVING_SIZE_CHOICES[2]],
#         null=True,
#         blank=True,
#     )
#     conversion_unit_volume = models.CharField(
#         max_length=6,
#         choices=[*SERVING_SIZE_CHOICES[1][1], SERVING_SIZE_CHOICES[2]],
#         null=True,
#         blank=True,
#     )
#     conversion_weight_to_volume = models.FloatField(
#         validators=[MinValueValidator(0.0)], null=True, blank=True
#     )
#     notes = models.TextField(null=True, blank=True)
#     restaurant = models.CharField(max_length=256, null=True, blank=True)
#     points_per_serving = models.IntegerField()
#     user_created = models.BooleanField(default=True)
#     user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True)
#     directions = models.TextField(max_length=2048, null=True, blank=True)
#     url = models.URLField(null=True)
#     servings_in_recipe = models.FloatField(
#         validators=[MinValueValidator(0.0)], null=True
#     )
#
#     def __str__(self):
#         return self.name
#
#
# class RecipeInstance(models.Model):
#     serving_size = models.FloatField(validators=[MinValueValidator(0.0)])
#     serving_unit = models.CharField(max_length=6, choices=SERVING_SIZE_CHOICES)
#     points = models.IntegerField()
#     # fat = models.FloatField()
#     # carbs = models.FloatField()
#     # fiber = models.FloatField()
#     # protein = models.FloatField()
#
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     meal = models.ManyToManyField("meal.Meal")
#
#
# class RecipeItem(models.Model):
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     food_instance = models.ForeignKey(
#         "food.FoodInstance", on_delete=models.SET_NULL, null=True
#     )
#     recipe_instance = models.ForeignKey(
#         RecipeInstance, on_delete=models.SET_NULL, null=True
#     )
#
#     def clean(self) -> None:
#         if self.food_instance is not None and self.recipe_instance is not None:
#             raise ValidationError(
#                 "Cannot have both a food_instance and a recipe_instance"
#             )
#         if self.food_instance is None and self.recipe_instance is None:
#             raise ValidationError("Must set either a food_instance or recipe_instance.")
#         super().clean()
#
#     def save(self, *args, **kwargs) -> None:
#         self.full_clean()
#         super().save(*args, **kwargs)
