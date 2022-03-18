import itertools

servings = {
    "weight": [("KG", "kg"), ("GM", "gm"), ("OZ", "oz"), ("LB", "lb")],
    "volume": [
        ("TSP", "tsp"),
        ("TBSP", "tbsp"),
        ("FL_OZ", "fl oz"),
        ("CUP", "cup"),
        ("ML", "ml"),
        ("L", "l"),
    ],
    "each": [("EACH", "each")],
}

SERVING_SIZE_CHOICES = list(itertools.chain(*servings.values()))
# SERVING_SIZE_CHOICES = [
#     ("KG", "kg"),
#     ("GM", "gm"),
#     ("OZ", "oz"),
#     ("LB", "lb"),
#     ("TSP", "tsp"),
#     ("TBSP", "tbsp"),
#     ("FL_OZ", "fl oz"),
#     ("CUP", "cup"),
#     ("ML", "ml"),
#     ("L", "l"),
#     ("EACH", "each"),
# ]


def is_weight_serving(val: str) -> bool:
    return val in list(itertools.chain(*servings.get("weight")))


def is_volume_serving(val: str) -> bool:
    return val in list(itertools.chain(*servings.get("volume")))


def is_each_serving(val: str) -> bool:
    return val in list(itertools.chain(*servings.get("each")))
