from datetime import date, datetime, timedelta
from pytz import timezone

from weight_points_plus.day.models import Day
from weight_points_plus.meal.models import Meal
from weight_points_plus.users.models import User, Weight
from weight_points_plus.utils.points_calculators import calculate_daily_points
from weight_points_plus.week.models import Week


def create_days(start_date: date, user: User, week: Week, num_days: int) -> date:
    if num_days == 0:
        return start_date
    days_left = num_days
    daily_points = calculate_daily_points(
        user, user.weight_set.last().weight, user.weight_set.last().weight_units
    )
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    days = []
    for dt in dates:
        days.append(
            Day(
                total_points=daily_points,
                points_used=0,
                points_remaining=daily_points,
                day_of_week=dt.weekday(),
                date=dt,
                week=week,
                user=user,
                days_left=days_left,
            )
        )
        days_left -= 1

    created_days = Day.objects.bulk_create(days)
    meals = []
    for day in created_days:
        for meal in Meal.MealChoices:
            meals.append(Meal(name=meal, day=day, user=user))
    Meal.objects.bulk_create(meals)

    return dates[-1]


def create_week(start_date: date, user: User, num_days: int = 7) -> date:
    week = Week(
        start_date=start_date,
        weekly_total_points=user.weekly_points,
        user=user,
    )
    if not user.first_weight_recorded:
        week.weight = user.weight_set.last().weight
        week.weight_units = user.weight_set.last().weight_units
        week.weight_recorded = True
        user.first_weight_recorded = True
        user.save()
    week.save()
    return create_days(start_date, user, week, num_days)


def backfill_weeks(user: User) -> None:
    latest_day = Day.objects.filter(user=user).order_by("-date").first()
    today = datetime.now(tz=timezone(user.timezone)).date()
    if not latest_day:
        latest_date = today - timedelta(days=1)
    else:
        latest_date = latest_day.date
    count = 0

    if latest_date <= today:
        num_days = (user.weigh_in_day - latest_date.weekday() - 1) % 7
        if num_days == 0:
            num_days = 7
        latest_date = create_week(latest_date + timedelta(days=1), user, num_days)
        while latest_date < (today + timedelta(days=7)) and count < 52:
            latest_date = create_week(latest_date + timedelta(days=1), user)
            count += 1
    user.latest_date = latest_date
    user.save()
