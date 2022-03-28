from weight_points_plus.week.models import Week


def update_weekly_excess_points(week: Week) -> None:
    week.weekly_points_used = sum(
        week.day_set.all().values_list("weekly_points_used", flat=True)
    )
    week.weekly_points_remaining = week.weekly_total_points - week.weekly_points_used
    week.save()


def update_weekly_activity_points(week: Week) -> None:
    week.activity_points = sum(
        week.day_set.all().values_list("activity_points", flat=True)
    )
    week.save()
