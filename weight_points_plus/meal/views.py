from django.db.models import QuerySet, Q
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from weight_points_plus.day.views import update_daily_points
from weight_points_plus.foods_recipes.models import FoodItem, FoodItemInstance
from weight_points_plus.foods_recipes.utils import FoodItemListView
from weight_points_plus.meal.models import Meal
from weight_points_plus.utils.misc import (
    is_weight_serving,
    is_volume_serving,
    is_each_serving,
)
from weight_points_plus.utils.mixins import UserHasAllInfoMixin
from weight_points_plus.utils.points_calculators import calculate_food_points


def update_meal_points(meal: Meal) -> None:
    meal.points = sum(meal.fooditeminstance_set.values_list("points", flat=True))
    meal.save()


class MealFoodListView(FoodItemListView):
    paginate_by = 20
    # template_name = "foods_recipes/food_search.html"

    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


meal_food_list_view = MealFoodListView.as_view()


class BaseMealFoodEditView:
    model = FoodItemInstance
    fields = ["serving_size", "serving_unit"]

    def get_meal(self):
        qs = Meal.objects.filter(user=self.request.user)
        return get_object_or_404(qs, pk=self.kwargs.get("meal_pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food"] = self.get_food()
        context["hello"] = "world"
        context["meal"] = self.get_meal()
        context["date"] = self.get_meal().day.date
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
                elif is_each_serving(food.serving_unit):
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


class MealFoodAddView(UserHasAllInfoMixin, BaseMealFoodEditView, CreateView):
    def get_queryset(self):
        return FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )

    def get_food(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.GET.get("food"))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        meal = self.get_meal()
        if form.is_valid():
            food = self.get_food()
            if len(meal.fooditeminstance_set.filter(food=food)) > 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "That food is already in the meal. Please update it instead of adding it again.",
                )
                return HttpResponseRedirect(
                    reverse("day:detail", kwargs={"date": meal.day.date})
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
            update_meal_points(meal)
            update_daily_points(meal.day)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": meal.day.date})
            )
        else:
            return self.form_invalid(form)


meal_food_add_view = MealFoodAddView.as_view()


class MealFoodUpdateView(UserHasAllInfoMixin, BaseMealFoodEditView, UpdateView):
    def get_queryset(self):
        return FoodItemInstance.objects.filter(meal=self.get_meal())

    def get_food(self):
        food_item = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        return food_item.food

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        meal = self.get_meal()
        obj = self.get_object()
        obj.meal.remove(meal)
        if form.is_valid():
            food = obj.food
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
            if len(obj.meal.all()) == 0:
                obj.delete()
            update_meal_points(meal)
            update_daily_points(meal.day)
            return HttpResponseRedirect(
                reverse("day:detail", kwargs={"date": meal.day.date})
            )
        else:
            return self.form_invalid(form)


meal_food_update_view = MealFoodUpdateView.as_view()


class MealFoodDeleteView(UserHasAllInfoMixin, DeleteView):
    model = FoodItemInstance

    def get(self, request, meal_pk=None, *args, **kwargs):
        qs = Meal.objects.filter(user=request.user)
        meal = get_object_or_404(qs, pk=meal_pk)
        obj = self.get_object()
        obj.meal.remove(meal)
        if len(obj.meal.all()) == 0:
            obj.delete()
        update_meal_points(meal)
        update_daily_points(meal.day)
        return HttpResponseRedirect(
            reverse("day:detail", kwargs={"date": meal.day.date})
        )

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        messages.add_message(
            request, messages.ERROR, "You cannot POST to this endpoint."
        )
        return redirect(request.META.get("HTTP_REFERER"))


meal_food_delete_view = MealFoodDeleteView.as_view()
