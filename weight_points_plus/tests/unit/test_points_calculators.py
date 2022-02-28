import datetime
from dataclasses import dataclass

import pytest

from weight_points_plus.food.models import Food
from weight_points_plus.utils.points_calculators import (
    check_valid_serving_unit,
    convert_weight_and_volume,
    get_multiplicative_factor,
    points_formula,
)

"""
NOTE: TO RUN TESTS RUN
python -m pytest tests/
"""


@dataclass
class FoodWithPoints:
    expected_points: int
    food: Food


no_conversion_weight_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Yoplait Blueberry Blended Fat Free Greek Yogurt",
            fat=0,
            carbs=22,
            fiber=0,
            protein=11,
            serving_size=5.3,
            serving_unit="oz",
        ),
        expected_points=3,
    ),
]

no_conversion_volume_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Kikkoman Low Sodium Soy Sauce",
            fat=0,
            carbs=1,
            fiber=0,
            protein=1,
            serving_size=1,
            serving_unit="tbsp",
        ),
        expected_points=0,
    ),
]

no_conversion_each_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Chicken Wing, Baked",
            fat=6.6,
            carbs=0,
            fiber=0,
            protein=9.1,
            serving_size=1,
            serving_unit="each",
        ),
        expected_points=3,
    ),
    FoodWithPoints(
        food=Food(
            name="Chicken Wing, Baked - Broken",
            fat=6.6,
            carbs=0,
            fiber=0,
            protein=9.1,
            serving_size=1,
            serving_unit="gm",
        ),
        expected_points=3,
    ),
]

no_conversion_foods: list[FoodWithPoints] = [
    *no_conversion_weight_foods,
    *no_conversion_volume_foods,
    *no_conversion_each_foods,
]

weight_to_each_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Vermont Bread Company Potato Hot Dog Buns",
            fat=2,
            carbs=25,
            fiber=1,
            protein=4,
            serving_size=57,
            serving_unit="gm",
            conversion_unit_weight="gm",
            conversion_unit_volume="each",
            conversion_weight_to_volume=57,
            notes="57g = 1 bun",
        ),
        expected_points=4,
    ),
    FoodWithPoints(
        food=Food(
            name="Kit-Kat, Snack Size",
            fat=11,
            carbs=27,
            fiber=0.5,
            protein=3,
            serving_size=42,
            serving_unit="gm",
            conversion_unit_weight="gm",
            conversion_unit_volume="each",
            conversion_weight_to_volume=14,
            notes="42g = 3 two-piece bars",
        ),
        expected_points=6,
    ),
    FoodWithPoints(
        food=Food(
            name="Trader Joe's Premium Angus Beef Filet Mignon Steak",
            fat=21,
            carbs=0,
            fiber=0,
            protein=22,
            serving_size=4,
            serving_unit="oz",
            conversion_unit_weight="oz",
            conversion_unit_volume="each",
            conversion_weight_to_volume=4,
            notes="1 serving = 4 oz",
        ),
        expected_points=7,
    ),
]

weight_to_volume_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Welch's Concord Grape Jelly",
            fat=0,
            carbs=13,
            fiber=0,
            protein=0,
            serving_size=20,
            serving_unit="gm",
            conversion_unit_weight="gm",
            conversion_unit_volume="tbsp",
            conversion_weight_to_volume=20,
            notes="20g = 1 tbsp",
        ),
        expected_points=1,
    ),
    FoodWithPoints(
        food=Food(
            name="Spaghetti Squash",
            fat=0,
            carbs=10,
            fiber=2,
            protein=1,
            serving_size=0.155,
            serving_unit="kg",
            conversion_unit_weight="gm",
            conversion_unit_volume="cup",
            conversion_weight_to_volume=155,
            notes="155gm = 1 cup",
        ),
        expected_points=1,
    ),
    FoodWithPoints(
        food=Food(
            name="Philadelphia Lite Cream Cheese",
            fat=2.3,
            carbs=1,
            fiber=0,
            protein=1.5,
            serving_size=0.6,
            serving_unit="tsp",
            conversion_unit_weight="oz",
            conversion_unit_volume="tbsp",
            conversion_weight_to_volume=0.6,
            notes="0.6oz = 1 tbsp",
        ),
        expected_points=1,
    ),
]

each_to_volume_foods: list[FoodWithPoints] = [
    FoodWithPoints(
        food=Food(
            name="Wholesome Organic Pancake Syrup",
            fat=0,
            carbs=66,
            fiber=0,
            protein=0,
            serving_size=0.25,
            serving_unit="cup",
            conversion_unit_weight="each",
            conversion_unit_volume="cup",
            conversion_weight_to_volume=4,
            notes="1 serving = 1/4 cup",
        ),
        expected_points=7,
    ),
    FoodWithPoints(
        food=Food(
            name="Flik Avocado, Diced ",
            fat=1,
            carbs=0.5,
            fiber=0.5,
            protein=0,
            serving_size=1,
            serving_unit="tsp",
            conversion_unit_weight="each",
            conversion_unit_volume="tbsp",
            conversion_weight_to_volume=1,
            notes="1 serving = 1 tbsp",
        ),
        expected_points=0,
    ),
]

foods: list[FoodWithPoints] = [
    *no_conversion_foods,
    *weight_to_each_foods,
    *weight_to_volume_foods,
    *each_to_volume_foods,
]


@pytest.mark.unit
def test_food_create_points():
    for food in foods:
        assert points_formula(food.food) == food.expected_points


@pytest.mark.unit
def test_convert_weight_and_volume():
    for food in [*weight_to_each_foods, *each_to_volume_foods]:
        with pytest.raises(ValueError) as error:
            convert_weight_and_volume(food.food, 1.5, "each")
        assert "This should not have happened." in str(error)

    for food in no_conversion_weight_foods:
        with pytest.raises(ValueError) as error:
            convert_weight_and_volume(food.food, 100, "kg")
        assert (
            "Cannot convert weight and volume for a food with no conversion factor."
            in str(error)
        )

    for food in weight_to_volume_foods:
        if food.food.name == "Welch's Concord Grape Jelly":
            with pytest.raises(ValueError) as error:
                convert_weight_and_volume(food.food, 2.65, "lb")
            assert "You cannot convert between two units of the same type." in str(
                error
            )
            assert convert_weight_and_volume(food.food, 2.65, "fl oz") == 1.325
            assert convert_weight_and_volume(food.food, 5.34, "ml") == 78.961512
        if food.food.name == "Spaghetti Squash":
            with pytest.raises(ValueError) as error:
                convert_weight_and_volume(food.food, 4.16, "oz")
            assert "You cannot convert between two units of the same type." in str(
                error
            )
            assert convert_weight_and_volume(food.food, 8.75, "l") == 2.07025
            assert convert_weight_and_volume(food.food, 45, "tsp") == 2160
        if food.food.name == "Philadelphia Lite Cream Cheese":
            with pytest.raises(ValueError) as error:
                convert_weight_and_volume(food.food, 3.15, "fl oz")
            assert "You cannot convert between two units of the same type." in str(
                error
            )
            assert convert_weight_and_volume(food.food, 9, "kg") == 2.1225
            assert convert_weight_and_volume(food.food, 1.5, "lb") == 0.78125


@pytest.mark.unit
def test_check_valid_serving_unit():
    for food in no_conversion_weight_foods:
        assert check_valid_serving_unit(food.food, "each") is False
        assert check_valid_serving_unit(food.food, "gm") is True
        assert check_valid_serving_unit(food.food, "cup") is False
    for food in no_conversion_volume_foods:
        assert check_valid_serving_unit(food.food, "each") is False
        assert check_valid_serving_unit(food.food, "tsp") is True
        assert check_valid_serving_unit(food.food, "lb") is False
    for food in no_conversion_each_foods:
        if "broken" not in food.food.name.lower():
            assert check_valid_serving_unit(food.food, "each") is True
            assert check_valid_serving_unit(food.food, "gm") is False
            assert check_valid_serving_unit(food.food, "tsp") is False

    for food in weight_to_each_foods:
        assert check_valid_serving_unit(food.food, "each") is True
        assert check_valid_serving_unit(food.food, "kg") is True
        assert check_valid_serving_unit(food.food, "tsp") is False

    for food in each_to_volume_foods:
        assert check_valid_serving_unit(food.food, "each") is True
        assert check_valid_serving_unit(food.food, "l") is True
        assert check_valid_serving_unit(food.food, "gm") is False

    for food in weight_to_volume_foods:
        assert check_valid_serving_unit(food.food, "each") is False
        assert check_valid_serving_unit(food.food, "l") is True
        assert check_valid_serving_unit(food.food, "lb") is True


@pytest.mark.unit
def test_check_multiplicative_factor():
    # mocker.patch("check_valid_serving_unit", return_value=True)

    assert get_multiplicative_factor(foods[0].food) == 1
    food = no_conversion_each_foods[0]
    assert get_multiplicative_factor(food.food, 4.36, "each") == 4.36
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(no_conversion_each_foods[-1].food, 1.25, "each")
    assert "You cannot pass in an 'each' without a conversion factor." in str(error)

    food = weight_to_each_foods[1]
    assert get_multiplicative_factor(food.food, 6, "each") == 2

    food = each_to_volume_foods[1]
    assert get_multiplicative_factor(food.food, 6, "each") == 18

    food = weight_to_volume_foods[1]
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food.food, 2.5, "each")
    assert "One of the conversion units must be 'each' if passing in an 'each'." in str(
        error
    )

    food = no_conversion_each_foods[0]
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food.food, 2.5, "tsp")
    assert (
        "The food's serving unit is set to 'each' but a conversion factor has not been set."
        in str(error)
    )

    food = Food(
        name="Random Food",
        fat=0,
        carbs=0,
        fiber=0,
        protein=0,
        serving_size=0.25,
        serving_unit="each",
        conversion_unit_weight="each",
        conversion_unit_volume="each",
        conversion_weight_to_volume=4,
    )
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food, 5.5, "gm")
    assert "The volume and weight conversion units cannot both be 'each'." in str(error)

    food.conversion_unit_weight = "kg"
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food, 12, "tsp")
    assert (
        "If the volume conversion unit is 'each' you cannot pass in volume as a serving unit"
        in str(error)
    )

    assert get_multiplicative_factor(food, 800, "gm") == 0.8

    food.serving_size = 2
    food.conversion_unit_weight = "each"
    food.conversion_unit_volume = "fl oz"
    food.conversion_weight_to_volume = 8
    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food, 5.5, "gm")
    assert (
        "If the weight conversion unit is 'each' you cannot pass in weight as a serving unit"
        in str(error)
    )

    assert get_multiplicative_factor(food, 0.5, "cup") == 16

    food = Food(
        name="Random Food",
        fat=0,
        carbs=0,
        fiber=0,
        protein=0,
        serving_size=2,
        serving_unit="lb",
        conversion_unit_weight="each",
        conversion_unit_volume="each",
        conversion_weight_to_volume=4,
    )
    assert get_multiplicative_factor(food, 4, "lb") == 2

    assert get_multiplicative_factor(food, 6, "kg") == 6.6138

    food.serving_unit = "ml"
    food.serving_size = 500
    assert get_multiplicative_factor(food, 2, "l") == 4

    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food, 5.5, "gm")
    assert (
        "You are trying to make a conversion where one of the conversion values is 'each', "
        "but neither the food's serving size nor the passed in serving size is 'each'."
        in str(error)
    )

    food.conversion_unit_volume = "l"
    food.conversion_unit_weight = "lb"

    assert get_multiplicative_factor(food, 2, "gm") == 453.5924

    food = Food(
        name="Random Food",
        fat=0,
        carbs=0,
        fiber=0,
        protein=0,
        serving_size=2,
        serving_unit="lb",
    )

    with pytest.raises(ValueError) as error:
        get_multiplicative_factor(food, 5.5, "ml")
    assert (
        "The food's saved unit is not the same type as the input one and no conversion factor exists."
        in str(error)
    )


# class UsersWithPoints(BaseModel):
#     user: UserDB
#     expected_points: int


# @pytest.mark.unit
# def test_calculate_daily_points():
#     users: list[UsersWithPoints] = [
#         UsersWithPoints(
#             user=UserDB(
#                 weight=245,
#                 height=69,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=45,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=48,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=302,
#                 height=65,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=36,
#                 email="test@example.com",
#                 hashed_password="test_password",
#                 maintenance_mode=True,
#             ),
#             expected_points=65,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=200,
#                 height=70,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=55,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=37,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=150,
#                 height=75,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=55,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=30,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=265,
#                 height=64,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=42,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=51,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=230,
#                 height=67,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=64,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=40,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=280,
#                 height=70,
#                 sex=SexChoices.male,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=51,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=53,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=180,
#                 height=62,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=45,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=26,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=150,
#                 height=64,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=36,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=26,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=200,
#                 height=65,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=52,
#                 email="test@example.com",
#                 hashed_password="test_password",
#                 maintenance_mode=True,
#             ),
#             expected_points=33,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=175,
#                 height=59,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=30,
#                 email="test@example.com",
#                 hashed_password="test_password",
#                 nursing=NursingChoices.EXCLUSIVE,
#             ),
#             expected_points=39,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=220,
#                 height=63,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=26,
#                 email="test@example.com",
#                 hashed_password="test_password",
#                 nursing=NursingChoices.SUPPLEMENTAL,
#             ),
#             expected_points=41,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=175,
#                 height=65,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=60,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=26,
#         ),
#         UsersWithPoints(
#             user=UserDB(
#                 weight=250,
#                 height=62,
#                 sex=SexChoices.female,
#                 birth_date=datetime.datetime(1990, 5, 23),
#                 age=18,
#                 email="test@example.com",
#                 hashed_password="test_password",
#             ),
#             expected_points=39,
#         ),
#     ]
#     for user in users:
#         assert calculate_daily_points(user.user) == user.expected_points
