from django.core.management import BaseCommand

from weight_points_plus.food.models import Food, FoodInstance
from weight_points_plus.user_recipe.models import Recipe, RecipeItem
from weight_points_plus.utils.points_calculators import calculate_food_points


class Command(BaseCommand):
    help = "Delete and re-create some sample recipes"

    def handle(self, *args, **options):
        Recipe.objects.all().delete()
        foods = Food.objects.filter(
            name__in=[
                "Life Cereal, Cinnamon",
                "Milk, Skim",
                "Mayonnaise, Hellman's",
                "DeCecco Cavatappi",
                "Trader Joe's Albacore Tuna in Water",
            ]
        )
        serving_sizes = {
            "Life Cereal, Cinnamon": 44,
            "Milk, Skim": 188,
            "Mayonnaise, Hellman's": 36,
            "DeCecco Cavatappi": 226,
            "Trader Joe's Albacore Tuna in Water": 4,
        }
        serving_units = {
            "Life Cereal, Cinnamon": "gm",
            "Milk, Skim": "gm",
            "Mayonnaise, Hellman's": "gm",
            "DeCecco Cavatappi": "gm",
            "Trader Joe's Albacore Tuna in Water": "oz",
        }
        food_dict = {x: dict() for x in serving_units.keys()}
        food_instances = []
        for food in foods:
            serving_size = serving_sizes[food.name]
            serving_unit = serving_units[food.name]
            points = calculate_food_points(food, serving_size, serving_unit)
            food_instances.append(
                FoodInstance(
                    serving_size=serving_size,
                    serving_unit=serving_unit,
                    food=food,
                    points=points,
                )
            )
        FoodInstance.objects.bulk_create(food_instances)
        cereal = Recipe.objects.create(
            name="Morning cereal",
            serving_size=200,
            serving_unit="gm",
            servings_in_recipe=1,
        )
        RecipeItem.objects.create()
