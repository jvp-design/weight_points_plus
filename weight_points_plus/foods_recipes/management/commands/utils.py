import csv
import random
from pathlib import Path

from django.contrib.auth import get_user_model

from weight_points_plus.foods_recipes.models import FoodItem
from weight_points_plus.utils.points_calculators import calculate_food_points

User = get_user_model()


def grab_and_parse_foods(
    filename: Path, food_names: list[str], users: list[User]
) -> tuple[list[FoodItem], list[str]]:
    foods = []
    excluded_foods = []
    with open(filename, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        header = next(csv_reader)
        is_restaurant = "restaurant" in header
        for row in csv_reader:
            if row[0] not in food_names:
                row_item = []
                for entry in row:
                    x = None if not entry else entry
                    row_item.append(x)
                user_created = row[7] == "TRUE"
                if not is_restaurant:
                    conversion_unit_weight = row_item[9]
                    conversion_unit_volume = row_item[10]
                    if conversion_unit_weight is not None:
                        conversion_unit_weight = conversion_unit_weight.upper()
                    if conversion_unit_volume is not None:
                        conversion_unit_volume = conversion_unit_volume.upper()
                    food_dict = dict(
                        name=row_item[0],
                        fat=float(row_item[1]),
                        carbs=float(row_item[2]),
                        fiber=float(row_item[3]),
                        protein=float(row_item[4]),
                        serving_size=float(row_item[5]),
                        serving_unit=row_item[6].upper(),
                        conversion_weight_to_volume=row_item[8],
                        conversion_unit_weight=conversion_unit_weight,
                        conversion_unit_volume=conversion_unit_volume,
                        notes=row_item[11],
                    )
                else:
                    food_dict = dict(
                        name=row_item[1],
                        fat=row_item[3],
                        carbs=row_item[4],
                        fiber=row_item[5],
                        protein=row_item[6],
                        serving_size=row_item[7],
                        serving_unit=row_item[8].upper(),
                        notes=row_item[9],
                    )

                food_dict["food_item_type"] = "food"

                if (
                    food_dict.get("fat") is None
                    or food_dict.get("fiber") is None
                    or food_dict.get("carbs") is None
                    or food_dict.get("protein") is None
                    or food_dict.get("serving_size") is None
                ):
                    excluded_foods.append(food_dict.get("name"))
                    continue
                else:
                    food_dict["fat"] = float(food_dict["fat"])
                    food_dict["carbs"] = float(food_dict["carbs"])
                    food_dict["fiber"] = float(food_dict["fiber"])
                    food_dict["protein"] = float(food_dict["protein"])
                    food_dict["serving_size"] = float(food_dict["serving_size"])
                if food_dict.get("conversion_weight_to_volume") is not None:
                    food_dict["conversion_weight_to_volume"] = float(
                        food_dict["conversion_weight_to_volume"]
                    )
                # try:
                food_item = FoodItem(**food_dict)
                # except ValidationError:
                #     print(food_dict)
                #     break
                try:
                    points = calculate_food_points(food_item)
                except TypeError:
                    excluded_foods.append(food_dict.get("name"))
                    continue
                food_item.points_per_serving = points
                if user_created:
                    food_item.user = random.choice(users)
                    food_item.user_created = True
                else:
                    food_item.user_created = False
                foods.append(food_item)
    return foods, excluded_foods


def seed_foods(
    path: Path, restaurant_foods: bool = False, delete_foods: bool = False
) -> tuple[int, list[str]]:
    if delete_foods:
        qs = FoodItem.objects.filter(food_item_type="food")
        if not restaurant_foods:
            qs = qs.filter(restaurant__isnull=True)
        qs.delete()
    users = User.objects.all()
    # food_names = FoodItem.objects.all().values_list("name")
    food_names = []
    foods, excluded_foods = grab_and_parse_foods(path, food_names, users)

    if len(foods) > 0:
        FoodItem.objects.bulk_create(foods)

    return len(foods), excluded_foods
