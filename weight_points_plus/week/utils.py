from weight_points_plus.week.models import Week


def update_weekly_excess_points(week: Week) -> None:
    week.weekly_points_remaining = sum(
        week.day_set.all().values_list("weekly_points_used", flat=True)
    )
    week.save()
