from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from weight_points_plus.foods_recipes.models import FoodItem, FoodItemInstance
from weight_points_plus.foods_recipes.recipe.forms import RecipeForm
from weight_points_plus.foods_recipes.utils import (
    FoodItemListView,
    check_conversion_status,
)
from weight_points_plus.utils.misc import (
    is_each_serving,
    is_weight_serving,
    is_volume_serving,
)
from weight_points_plus.utils.mixins import (
    UserHasAllInfoMixin,
    UserCanViewMixin,
    UserIsOwnerMixin,
)
from weight_points_plus.utils.points_calculators import (
    calculate_food_points,
    get_multiplicative_factor,
    points_formula,
    NutritionItem,
)


def calculate_recipe_points(recipe):
    nutrition_item = NutritionItem(fat=0, carbs=0, fiber=0, protein=0)
    for item in recipe.recipe_items.all():
        factor = get_multiplicative_factor(item, item.serving_size, item.serving_unit)
        nutrition_item.fat += item.food.fat * factor
        nutrition_item.carbs += item.food.carbs * factor
        nutrition_item.fiber += item.food.fiber * factor
        nutrition_item.protein += item.food.protein * factor

    recipe.fat = nutrition_item.fat
    recipe.carbs = nutrition_item.carbs
    recipe.fiber = nutrition_item.fiber
    recipe.protein = nutrition_item.protein
    servings_in_recipe = 1
    if recipe.servings_in_recipe is not None:
        servings_in_recipe = recipe.servings_in_recipe
    nutrition_item.fat /= servings_in_recipe
    nutrition_item.carbs /= servings_in_recipe
    nutrition_item.fiber /= servings_in_recipe
    nutrition_item.protein /= servings_in_recipe
    recipe.points_per_serving = points_formula(nutrition_item)
    recipe.save()


class AllRecipesListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(food_item_type="recipe")
            & (Q(user_created=False) | Q(user=self.request.user))
        )
        return super().get_queryset()


all_recipe_list_view = AllRecipesListView.as_view()


class UserRecipeListView(FoodItemListView):
    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user=self.request.user) & Q(food_item_type="recipe")
        )
        return super().get_queryset()


user_recipe_list_view = UserRecipeListView.as_view()


class RecipeDetailView(UserHasAllInfoMixin, UserCanViewMixin, DetailView):
    model = FoodItem
    template_name = "foods_recipes/recipe_detail.html"


recipe_detail_view = RecipeDetailView.as_view()


class RecipeInputMixin:
    form_class = RecipeForm
    template_name = "foods_recipes/recipe_form.html"

    def get_queryset(self):
        return FoodItem.objects.filter(user=self.request.user, food_item_type="recipe")

    def get_success_url(self):
        return reverse("recipe:detail", kwargs={"pk": self.object.pk})


class RecipeCreateView(UserHasAllInfoMixin, RecipeInputMixin, CreateView):
    pass


recipe_create_view = RecipeCreateView.as_view()


class RecipeUpdateView(
    UserHasAllInfoMixin, UserIsOwnerMixin, RecipeInputMixin, UpdateView
):
    pass


recipe_update_view = RecipeUpdateView.as_view()


class RecipeDeleteView(UserHasAllInfoMixin, UserIsOwnerMixin, DeleteView):
    model = FoodItem
    success_url = reverse_lazy("recipe:list")


recipe_delete_view = RecipeDeleteView.as_view()


class RecipeFoodListView(FoodItemListView):
    paginate_by = 20
    # template_name = "foods_recipes/food_search.html"

    def get_queryset(self) -> QuerySet[FoodItem]:
        self.queryset = FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )
        return super().get_queryset()


recipe_food_list_view = RecipeFoodListView.as_view()


class BaseRecipeFoodEditView:
    model = FoodItemInstance
    fields = ["serving_size", "serving_unit"]

    def get_queryset(self):
        return FoodItem.objects.filter(
            Q(user_created=False) | Q(user=self.request.user)
        )

    def get_recipe(self):
        qs = FoodItem.objects.filter(user=self.request.user, food_item_type="recipe")
        return get_object_or_404(qs, pk=self.kwargs.get("recipe_pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["food"] = self.get_food()
        context["recipe_name"] = self.get_recipe().name
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


class RecipeFoodAddView(UserHasAllInfoMixin, BaseRecipeFoodEditView, CreateView):
    def get_food(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.GET.get("food"))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        recipe = self.get_recipe()
        if form.is_valid():
            food = self.get_food()
            if len(recipe.recipe_items.filter(food=food)) > 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "That food is already in the meal. Please update it instead of adding it again.",
                )
                return HttpResponseRedirect(
                    reverse("recipe:detail", kwargs={"pk": recipe.pk})
                )

            try:
                item = FoodItemInstance.objects.get(
                    food=food,
                    serving_unit=request.POST.get("serving_unit"),
                    serving_size=request.POST.get("serving_size"),
                )
            except FoodItemInstance.DoesNotExist:
                item = form.save(commit=False)
                item.food = food
                item.save()
            recipe.recipe_items.add(item)
            calculate_recipe_points(recipe)
            if "recipe-add-another" in request.POST:
                return HttpResponseRedirect(
                    f'{reverse("recipe:food-list", kwargs={"recipe_pk": recipe.pk})}?name={request.POST.get("next-food-search")}'
                )
            return HttpResponseRedirect(
                reverse("recipe:detail", kwargs={"pk": recipe.pk})
            )
        else:
            return self.form_invalid(form)


recipe_food_add_view = RecipeFoodAddView.as_view()


class RecipeFoodUpdateView(UserHasAllInfoMixin, BaseRecipeFoodEditView, UpdateView):
    def get_food(self):
        food_item = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        return food_item.food

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = self.get_form()
        recipe = self.get_recipe()
        recipe.recipe_items.remove(obj)
        if form.is_valid():
            food = obj.food
            try:
                item = FoodItemInstance.objects.get(
                    food=food,
                    serving_unit=request.POST.get("serving_unit"),
                    serving_size=request.POST.get("servings_size"),
                )
            except FoodItemInstance.DoesNotExist:
                item = form.save(commit=False)
                item.food = food
                item.save()
            recipe.recipe_items.add(item)
            if len(obj.fooditem_set.all()) == 0:
                obj.delete()
            calculate_recipe_points(recipe)
            return HttpResponseRedirect(
                reverse("recipe:detail", kwargs={"pk": recipe.pk})
            )
        else:
            return self.form_invalid(form)


recipe_food_update_view = RecipeFoodUpdateView.as_view()


class RecipeFoodDeleteView(UserHasAllInfoMixin, DeleteView):
    model = FoodItemInstance

    def get(self, request, recipe_pk=None, *args, **kwargs):
        qs = FoodItem.objects.filter(user=request.user, food_item_type="recipe")
        recipe = get_object_or_404(qs, pk=recipe_pk)
        obj = self.get_object()
        recipe.recipe_items.remove(obj)
        if len(obj.fooditem_set.all()) == 0:
            obj.delete()
        calculate_recipe_points(recipe)
        return HttpResponseRedirect(reverse("recipe:detail", kwargs={"pk": recipe.pk}))

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        messages.add_message(
            request, messages.ERROR, "You cannot POST to this endpoint."
        )
        return redirect(request.META.get("HTTP_REFERER"))


recipe_food_delete_view = RecipeFoodDeleteView.as_view()
