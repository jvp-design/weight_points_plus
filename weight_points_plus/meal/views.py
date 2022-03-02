from django.db.models import QuerySet, Q
from django.forms import forms
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

    def post(self, request, pk=None, *args, **kwargs):
        form = self.get_form()
        qs = Meal.objects.filter(user=request.user)
        meal = get_object_or_404(qs, pk=pk)
        if form.is_valid():
            """

            What you'll need to do here is first check if the FoodItemInstance exists in the current meal.
            If it does you'll need to update the serving size.
            In order to do that you'll need to check if a FoodItemInstance with this new serving size exists in the current meal.
            What you'll likely want to do is find all FoodItemInstances with the same serving_unit and meal.
            Add up all of the serving sizes (including what you're passing here) and see if that exists.
            If it does just use that. Otherwise you'll need to create it.

            """
            try:
                self.object = FoodItemInstance.objects.get(
                    food=self.food,
                    serving_size=request.POST.get("serving_size"),
                    serving_unit=request.POST.get("serving_unit"),
                )
                if meal in self.object.meal.all():
                    print("hello")
                    pass
            except FoodItemInstance.DoesNotExist:
                self.object = form.save(commit=False)
                self.object.points = calculate_food_points(
                    self.food,
                    self.object.serving_size,
                    self.object.serving_unit.lower(),
                )
                self.object.food = self.food
                self.object.save()
            self.object.meal.add(meal)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date_val": meal.day.date})
            )
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food"] = self.food
        return context

    def get_form_class(self):
        qs = FoodItem.objects.filter(Q(user_created=False) | Q(user=self.request.user))
        self.food = get_object_or_404(qs, pk=self.request.GET.get("food"))
        form = super().get_form_class()
        if self.food.conversion_weight_to_volume is None:
            if is_weight_serving(self.food.serving_unit):
                choices = list(
                    filter(
                        lambda x: x[0] == "Weight",
                        form.base_fields["serving_unit"].choices,
                    )
                )
            elif is_volume_serving(self.food.serving_unit):
                choices = list(
                    filter(
                        lambda x: x[0] == "Volume",
                        form.base_fields["serving_unit"].choices,
                    )
                )
            elif self.food.serving_unit == "each":
                choices = list(
                    filter(
                        lambda x: x[0] == "EACH",
                        form.base_fields["serving_unit"].choices,
                    )
                )
            else:
                choices = form.base_fields["serving_unit"].choices
            form.base_fields["serving_unit"].choices = choices
        form.base_fields["serving_unit"].initial = self.food.serving_unit
        return form


meal_food_add_view = MealFoodAddView.as_view()
