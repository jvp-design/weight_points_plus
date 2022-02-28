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
