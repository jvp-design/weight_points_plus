from weight_points_plus.day.models import Activity, Day
from weight_points_plus.users.models import Weight


def calculate_activity_points(item: Activity, day: Day) -> int:
    weight = day.week.weight
    if not weight:
        user = day.user
        user_weight = Weight.objects.filter(user=user).order_by("date_recorded").last()
        if user_weight.weight_units == "kg":
            weight = user_weight.weight * 2.205
        else:
            weight = user_weight.weight
    if item.level == "Low":
        factor = 0.00033
    elif item.level == "Moderate":
        factor = 0.00047
    elif item.level == "High":
        factor = 0.00117
    else:
        factor = 0

    return int(round(float(weight) * item.duration * factor, 0))
