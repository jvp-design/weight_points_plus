from weight_points_plus.activity.models import ActivityInstance
from weight_points_plus.day.models import Day


def calculate_activity_points(item: ActivityInstance, day: Day) -> int:
    weight = day.week.weight
    if item.level == "low":
        factor = 0.00033
    elif item.level == "moderate":
        factor = 0.00047
    elif item.level == "hight":
        factor = 0.00117
    else:
        factor = 0

    return int(round(float(weight) * item.duration * factor, 0))
