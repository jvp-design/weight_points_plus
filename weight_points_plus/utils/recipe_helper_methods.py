# from pydantic import BaseModel, Field
#
# from weight_points_plus.user_recipe.models import Recipe
# from weight_points_plus.utils.points_calculators import get_multiplicative_factor
#
#
# class NutritionFields(BaseModel):
#     fat: float = Field(ge=0)
#     carbs: float = Field(ge=0)
#     fiber: float = Field(ge=0)
#     protein: float = Field(ge=0)
#
#
# def update_recipe_nutrition(
#     items: list[Food] | list[Recipe], recipe: RecipeCreate | Recipe
# ) -> NutritionFields:
#     nutrition_item = NutritionFields(fat=0, carbs=0, fiber=0, protein=0)
#     if len(items) == 0:
#         return nutrition_item
#     item_type = "foods"
#     if type(items[0]) == Recipe:
#         item_type = "recipes"
#     for item in items:
#         recipe_item = list(
#             filter(lambda x: x.id == item.id, getattr(recipe, item_type))
#         )[0]
#
#         factor = get_multiplicative_factor(
#             item, recipe_item.serving_size, recipe_item.serving_unit
#         )
#         nutrition_item.fat += item.fat * factor
#         nutrition_item.carbs += item.carbs * factor
#         nutrition_item.fiber += item.fiber * factor
#         nutrition_item.protein += item.protein * factor
#
#     return nutrition_item
#
#
# def get_nutrition_items(
#     foods: list[Food], recipes: list[Recipe], recipe: RecipeCreate | Recipe
# ) -> tuple[float, float, float, float]:
#     foods_nutrition = update_recipe_nutrition(foods, recipe)
#     recipes_nutrition = update_recipe_nutrition(recipes, recipe)
#
#     fat = foods_nutrition.fat + recipes_nutrition.fat
#     carbs = foods_nutrition.carbs + recipes_nutrition.carbs
#     fiber = foods_nutrition.fiber + recipes_nutrition.fiber
#     protein = foods_nutrition.protein + recipes_nutrition.protein
#
#     return fat, carbs, fiber, protein
#
#
# def calculate_recipe_points_per_serving(
#     foods: list[Food], recipes: list[Recipe], recipe: RecipeCreate | Recipe
# ) -> PointsPerServingCalcOutput:
#     fat, carbs, fiber, protein = get_nutrition_items(foods, recipes, recipe)
#
#     fat /= recipe.servings_in_recipe
#     carbs /= recipe.servings_in_recipe
#     fiber /= recipe.servings_in_recipe
#     protein /= recipe.servings_in_recipe
#     points_per_serving = points_formula(
#         NutritionFields(fat=fat, carbs=carbs, fiber=fiber, protein=protein),
#     )
#     return PointsPerServingCalcOutput(
#         fat=fat,
#         carbs=carbs,
#         fiber=fiber,
#         protein=protein,
#         points_per_serving=points_per_serving,
#     )
