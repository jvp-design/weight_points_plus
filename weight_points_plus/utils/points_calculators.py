from typing import Optional

from pydantic import BaseModel

from weight_points_plus.foods_recipes.models import (
    FoodItem,
)
from weight_points_plus.utils.misc import (
    SERVING_SIZE_CHOICES,
    is_weight_serving,
    is_volume_serving,
    is_each_serving,
)
from weight_points_plus.users.models import User


unit_dict = {
    "gm": {"kg": 0.001, "oz": 0.0353, "lb": 0.0022, "gm": 1.0},
    "kg": {"gm": 1000.0, "oz": 35.274, "lb": 2.2046, "kg": 1.0},
    "oz": {"gm": 28.3495, "kg": 0.0283, "lb": 0.0625, "oz": 1.0},
    "lb": {"gm": 453.5924, "kg": 0.4536, "oz": 16.0, "lb": 1.0},
    "tsp": {
        "tbsp": 0.3333,
        "fl oz": 0.1667,
        "cup": 0.0208,
        "ml": 4.9289,
        "l": 0.0049,
        "tsp": 1.0,
    },
    "tbsp": {
        "tsp": 3.0,
        "fl oz": 0.5,
        "cup": 0.0625,
        "ml": 14.7868,
        "l": 0.0148,
        "tbsp": 1.0,
    },
    "fl oz": {
        "tsp": 6.0,
        "tbsp": 2.0,
        "cup": 0.125,
        "ml": 29.5735,
        "l": 0.0296,
        "fl oz": 1.0,
    },
    "cup": {
        "tsp": 48.0,
        "tbsp": 16.0,
        "fl oz": 8.0,
        "ml": 236.5882,
        "l": 0.2366,
        "cup": 1.0,
    },
    "ml": {
        "tsp": 0.2029,
        "tbsp": 0.0676,
        "fl oz": 0.0338,
        "cup": 0.0042,
        "l": 0.001,
        "ml": 1.0,
    },
    "l": {
        "tsp": 202.8841,
        "tbsp": 67.628,
        "fl oz": 33.814,
        "cup": 4.2268,
        "ml": 1000.0,
        "l": 1.0,
    },
    "GM": {"KG": 0.001, "OZ": 0.0353, "LB": 0.0022, "GM": 1.0},
    "KG": {"GM": 1000.0, "OZ": 35.274, "LB": 2.2046, "KG": 1.0},
    "OZ": {"GM": 28.3495, "KG": 0.0283, "LB": 0.0625, "OZ": 1.0},
    "LB": {"GM": 453.5924, "KG": 0.4536, "OZ": 16.0, "LB": 1.0},
    "TSP": {
        "TBSP": 0.3333,
        "FL OZ": 0.1667,
        "CUP": 0.0208,
        "ML": 4.9289,
        "L": 0.0049,
        "TSP": 1.0,
    },
    "TBSP": {
        "TSP": 3.0,
        "FL OZ": 0.5,
        "CUP": 0.0625,
        "ML": 14.7868,
        "L": 0.0148,
        "TBSP": 1.0,
    },
    "FL OZ": {
        "TSP": 6.0,
        "TBSP": 2.0,
        "CUP": 0.125,
        "ML": 29.5735,
        "L": 0.0296,
        "FL OZ": 1.0,
    },
    "CUP": {
        "TSP": 48.0,
        "TBSP": 16.0,
        "FL OZ": 8.0,
        "ML": 236.5882,
        "L": 0.2366,
        "CUP": 1.0,
    },
    "ML": {
        "TSP": 0.2029,
        "TBSP": 0.0676,
        "FL OZ": 0.0338,
        "CUP": 0.0042,
        "L": 0.001,
        "ML": 1.0,
    },
    "L": {
        "TSP": 202.8841,
        "TBSP": 67.628,
        "FL OZ": 33.814,
        "CUP": 4.2268,
        "ML": 1000.0,
        "L": 1.0,
    },
}


class NutritionItem(BaseModel):
    fat: float
    carbs: float
    fiber: float
    protein: float


def calculate_daily_points(user: User) -> int:
    MIN_POINTS = 26
    MAX_POINTS = 71

    weight = float(user.weight) * 0.453592
    height = user.height * 0.0254

    if user.sex == User.SexChoices.MALE:
        tee = 864 - (9.72 * user.age) + (1.12 * (14.2 * weight + 503 * height))
    else:
        tee = 387 - (7.31 * user.age) + (1.14 * (10.9 * weight + 660.7 * height))

    atee = tee - (tee * 0.1) + 200

    target = round(min(max(atee - 1000, 1000), 2500) / 35)

    if user.sex == User.SexChoices.FEMALE:
        if user.nursing == 1:
            target += 7
        elif user.nursing == 2:
            target += 14

    daily_points = max(min(target - 11, MAX_POINTS), MIN_POINTS)
    if user.maintenance_mode:
        return daily_points + 6
    return daily_points


def points_formula(food: FoodItem | NutritionItem, multiplier: float = 1.0) -> int:
    return max(
        round(
            (
                multiplier
                * (
                    16 * food.protein
                    + 19 * food.carbs
                    + 45 * food.fat
                    - 14 * food.fiber
                )
            )
            / 175
        ),
        0,
    )


def check_valid_serving_unit(food: FoodItem, serving_unit: str) -> bool:
    if is_each_serving(serving_unit):
        if is_each_serving(food.serving_unit):
            return True
        if food.conversion_weight_to_volume is not None:
            if is_weight_serving(food.serving_unit) and is_each_serving(
                food.conversion_unit_volume
            ):
                return True
            if is_volume_serving(food.serving_unit) and is_each_serving(
                food.conversion_unit_weight
            ):
                return True

    if is_weight_serving(serving_unit):
        if is_weight_serving(food.serving_unit):
            return True
        if (
            is_volume_serving(food.serving_unit)
            and food.conversion_weight_to_volume is not None
            and not is_each_serving(food.conversion_unit_weight)
        ):
            return True
        if (
            is_each_serving(food.serving_unit)
            and food.conversion_weight_to_volume is not None
            and is_each_serving(food.conversion_unit_volume)
        ):
            return True

    if is_volume_serving(serving_unit):
        if is_volume_serving(food.serving_unit):
            return True
        if (
            is_weight_serving(food.serving_unit)
            and food.conversion_weight_to_volume is not None
            and not is_each_serving(food.conversion_unit_volume)
        ):
            return True
        if (
            is_each_serving(food.serving_unit)
            and food.conversion_weight_to_volume is not None
            and is_each_serving(food.conversion_unit_weight)
        ):
            return True
    return False


def convert_weight_and_volume(
    food: FoodItem, serving_size: float, serving_unit: str
) -> float:
    if food.conversion_weight_to_volume is None:
        raise ValueError(
            "Cannot convert weight and volume for a food with no conversion factor."
        )
    if is_each_serving(food.conversion_unit_weight) or is_each_serving(
        food.conversion_unit_volume
    ):
        raise ValueError(
            "The serving unit passed in is a different type to the food's serving unit, but one of the conversion "
            "factors is 'each'.  This should not have happened."
        )
    if (is_weight_serving(food.serving_unit) and is_weight_serving(serving_unit)) or (
        is_volume_serving(food.serving_unit) and is_volume_serving(serving_unit)
    ):
        raise ValueError("You cannot convert between two units of the same type.")
    if is_weight_serving(serving_unit):
        conversion_unit_key = "conversion_unit_weight"
        other_unit_key = "conversion_unit_volume"
    else:
        conversion_unit_key = "conversion_unit_volume"
        other_unit_key = "conversion_unit_weight"
    conversion_unit = getattr(food, conversion_unit_key)
    passed_multiplier = unit_dict[conversion_unit][serving_unit] * serving_size

    other_unit = getattr(food, other_unit_key)
    other_multiplier = unit_dict[other_unit][food.serving_unit]

    if is_weight_serving(serving_unit):
        operation = (
            passed_multiplier / food.conversion_weight_to_volume * other_multiplier
        ) / food.serving_size
    else:
        operation = (
            passed_multiplier * food.conversion_weight_to_volume * other_multiplier
        ) / food.serving_size

    return operation


def get_multiplicative_factor(
    food: FoodItem,
    serving_size: Optional[float] = None,
    serving_unit: Optional[str] = None,
) -> float:
    # This is to calculate the points of a generic serving
    if serving_unit is None or serving_size is None:
        return 1

    # Check if 'each' is passed in
    if is_each_serving(serving_unit):
        # If the serving_unit is also each then this is simple
        if is_each_serving(food.serving_unit):
            return serving_size / food.serving_size
        # Otherwise, make sure that there is a conversion factor
        if food.conversion_weight_to_volume is None:
            raise ValueError(
                "You cannot pass in an 'each' without a conversion factor."
            )

        # If the conversion_unit_volume value is each then
        # you need to get the weight multiplier because you'll
        # convert from each to weight and then convert to
        # the food's base weight value
        if is_each_serving(food.conversion_unit_volume):
            multiplier = unit_dict[food.conversion_unit_weight][food.serving_unit]
            return (
                multiplier
                * food.conversion_weight_to_volume
                * serving_size
                / food.serving_size
            )
        # Vice-versa for volume
        if is_each_serving(food.conversion_unit_weight):
            multiplier = unit_dict[food.conversion_unit_volume][food.serving_unit]
            return (
                multiplier
                / food.conversion_weight_to_volume
                * serving_size
                / food.serving_size
            )
        raise ValueError(
            "One of the conversion units must be 'each' if passing in an 'each'."
        )

    # Instead, check if the food's serving unit is each
    if is_each_serving(food.serving_unit):
        # Again, return an error if there is no conversion factor
        if food.conversion_weight_to_volume is None:
            raise ValueError(
                "The food's serving unit is set to 'each' but a conversion factor has not been set."
            )
        if is_each_serving(food.conversion_unit_volume) and is_each_serving(
            food.conversion_unit_weight
        ):
            raise ValueError(
                "The volume and weight conversion units cannot both be 'each'."
            )

        # If the food's conversion_unit_volume is each then
        # you need to convert the passed in values (the weight) to base units
        if is_each_serving(food.conversion_unit_volume):
            if is_volume_serving(serving_unit):
                raise ValueError(
                    "If the volume conversion unit is 'each' you cannot pass in volume as a serving unit"
                )
            multiplier = unit_dict[serving_unit][food.conversion_unit_weight]
            return (
                multiplier
                / food.conversion_weight_to_volume
                * serving_size
                / food.serving_size
            )
        if is_each_serving(food.conversion_unit_weight):
            if is_weight_serving(serving_unit):
                raise ValueError(
                    "If the weight conversion unit is 'each' you cannot pass in weight as a serving unit"
                )
            multiplier = unit_dict[serving_unit][food.conversion_unit_volume]
            return (
                multiplier
                * food.conversion_weight_to_volume
                * serving_size
                / food.serving_size
            )
        raise ValueError(
            "You should never get here because if the serving unit is each then the prior 'if' statement is hit."
        )
    # If the input serving unit is equal to the food's serving unit
    # then you just multiply by the serving_size
    if serving_unit == food.serving_unit:
        return serving_size / food.serving_size

    # If the input serving unit is a weight unit and the food's serving
    # unit is a weight unit you'll just need to convert
    if is_weight_serving(serving_unit) and is_weight_serving(food.serving_unit):
        return (
            serving_size
            * unit_dict[serving_unit][food.serving_unit]
            / food.serving_size
        )

    # If the input serving unit is a volume unit and the food's serving
    # unit is a volume unit you'll just need to convert
    if is_volume_serving(serving_unit) and is_volume_serving(food.serving_unit):
        return (
            serving_size
            * unit_dict[serving_unit][food.serving_unit]
            / food.serving_size
        )

    # This means that the serving units are not both each, both weight,
    # or both volume serving units, in which case we need to check if
    # there is a conversion factor.  If there is, then just convert
    # to base units of both and use the conversion factor to get back
    # to the needed size
    if food.conversion_weight_to_volume is not None:
        if is_each_serving(food.conversion_unit_weight) or is_each_serving(
            food.conversion_unit_volume
        ):
            raise ValueError(
                "You are trying to make a conversion where one of the conversion values is 'each', "
                "but neither the food's serving size nor the passed in serving size is 'each'."
            )
        return convert_weight_and_volume(food, serving_size, serving_unit)

    raise ValueError(
        "The food's saved unit is not the same type as the input one and no conversion factor exists."
    )


def calculate_food_points(
    food: FoodItem,
    serving_size: Optional[float] = None,
    serving_unit: Optional[str] = None,
) -> Optional[int]:
    if serving_size is not None and serving_unit is not None:
        if not check_valid_serving_unit(food, serving_unit):
            raise ValueError("There was an error with the serving unit you included")

    multiplicative_factor = get_multiplicative_factor(food, serving_size, serving_unit)
    return points_formula(food, multiplicative_factor)
