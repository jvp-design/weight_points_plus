from django.db.models import QuerySet, Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from weight_points_plus.foods_recipes.models import FoodItem, FoodItemInstance
from weight_points_plus.foods_recipes.utils import FoodItemListView
from weight_points_plus.meal.models import Meal
from weight_points_plus.utils.misc import (
    SERVING_SIZE_CHOICES,
    is_weight_serving,
    is_volume_serving,
)
from weight_points_plus.utils.points_calculators import calculate_food_points


class MealFoodListView(FoodItemListView):
    paginate_by = 20
    template_name = "meal/food_search.html"

    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


meal_food_list_view = MealFoodListView.as_view()


class MealFoodAddView(CreateView):
    model = FoodItemInstance
    fields = ["serving_size", "serving_unit"]
    food = None
    choices = None

    def __init__(self):
        super().__init__()

    def get_queryset(self):
        return FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )

    def get_food(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.GET.get("food"))

    def post(self, request, pk=None, *args, **kwargs):
        form = self.get_form()
        qs = Meal.objects.filter(user=request.user)
        meal = get_object_or_404(qs, pk=pk)
        if form.is_valid():
            food = self.get_food()
            if len(meal.fooditeminstance_set.filter(food=food)) > 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "That food is already in the meal. Please update it instead of adding it again.",
                )
                return HttpResponseRedirect(
                    reverse("day:detail", kwargs={"date_val": meal.day.date})
                )

            try:
                item = FoodItemInstance.objects.get(
                    food=food,
                    serving_unit=request.POST.get("serving_unit"),
                    serving_size=request.POST.get("serving_size"),
                )
            except FoodItemInstance.DoesNotExist:
                item = form.save(commit=False)
                item.points = calculate_food_points(
                    food,
                    item.serving_size,
                    item.serving_unit,
                )
                item.food = food
                item.save()
            item.meal.add(meal)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date_val": meal.day.date})
            )
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food"] = self.get_food()
        return context

    def get_form_class(self):
        form = super().get_form_class()
        if self.request.method == "GET":
            food = self.get_food()
            if food.conversion_weight_to_volume is None:
                if is_weight_serving(food.serving_unit):
                    choices = list(
                        filter(
                            lambda x: x[0] == "Weight",
                            form.base_fields["serving_unit"].choices,
                        )
                    )
                elif is_volume_serving(food.serving_unit):
                    choices = list(
                        filter(
                            lambda x: x[0] == "Volume",
                            form.base_fields["serving_unit"].choices,
                        )
                    )
                elif food.serving_unit == "each":
                    choices = list(
                        filter(
                            lambda x: x[0] == "EACH",
                            form.base_fields["serving_unit"].choices,
                        )
                    )
                else:
                    choices = form.base_fields["serving_unit"].choices
                form.base_fields["serving_unit"].choices = choices
            form.base_fields["serving_unit"].initial = food.serving_unit
        return form


meal_food_add_view = MealFoodAddView.as_view()
