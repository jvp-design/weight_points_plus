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


def is_weight_serving(val: str) -> bool:
    return val in [x[0] for x in SERVING_SIZE_CHOICES[0][1]] or val in [
        x[1] for x in SERVING_SIZE_CHOICES[0][1]
    ]


def is_volume_serving(val: str) -> bool:
    return val in [x[0] for x in SERVING_SIZE_CHOICES[1][1]] or val in [
        x[1] for x in SERVING_SIZE_CHOICES[1][1]
    ]


def is_each_serving(val: str) -> bool:
    return val == "EACH" or val == "each"
