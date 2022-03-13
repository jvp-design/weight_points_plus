from weight_points_plus.day.models import Activity, Day


def calculate_activity_points(item: Activity, day: Day) -> int:
    weight = day.week.weight
    if item.level == "Low":
        factor = 0.00033
    elif item.level == "Moderate":
        factor = 0.00047
    elif item.level == "High":
        factor = 0.00117
    else:
        factor = 0

    return int(round(float(weight) * item.duration * factor, 0))
